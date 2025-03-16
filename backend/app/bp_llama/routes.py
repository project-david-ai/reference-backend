import json
from typing import Any
from entities_api import OllamaClient, LocalInference, CloudInference, EntitiesEventHandler
from flask import jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required

from backend.app.services.llm_routing_services.llm_router_service import LlmRouter
from backend.app.services.function_call_service.function_call_service import FunctionCallService
from backend.app.services.logging_service.logger import LoggingUtility
from . import bp_llama

logging_utility = LoggingUtility()
client = OllamaClient()

# Initialize the LlmRouter with the path to the routing configuration file
llm_router = LlmRouter('llm_model_routing_config.json')

# Define an event callback to immediately process events as they occur.
# Note: The callback now accepts only (event_type, event_data). The event payload itself carries the thread_id and assistant_id.
def handle_event(event_type: str, event_data: Any):
    logging_utility.info(f"[Callback] Event: {event_type}, Data: {event_data}")

    if event_type == "tool_invoked":
        # Extract context and tool data from the event payload.
        action_id = event_data.get("tool_call_id")
        thread_id = event_data.get("thread_id")
        assistant_id = event_data.get("assistant_id")
        tool_name = event_data.get("tool_name")
        tool_id = event_data.get("tool_id")
        result = event_data.get("result")
        function_args = event_data.get("function_args")

        logging_utility.info(f"Tool invoked: {tool_name} (ID: {tool_id}) with result: {result}")
        function_call_service = FunctionCallService()
        handle_function = function_call_service.call_function(function_name=tool_name, arguments=function_args)
        logging_utility.info(f"Handled function call: {handle_function}")


        # The User submits tool output here
        content = handle_function
        if isinstance(handle_function, dict):
            content = json.dumps(handle_function)

        tool_output_submission = client.message_service.submit_tool_output(
            thread_id=thread_id,
            content=content,
            role="tool",
            assistant_id=assistant_id,
            tool_id=tool_id
        )
        client.action_service.update_action(action_id=action_id, status='completed')
        logging_utility.info(f"Tool output inserted!")

        # Additional processing logic can be added here.
    elif event_type == "action_required":
        # Process action_required event if needed.
        logging_utility.info("Action required event received.")
    else:
        logging_utility.info(f"Received event {event_type} with data: {event_data}")


# Initialize the EntitiesEventHandler with the event callback.
# The event handler will now emit events containing thread_id and assistant_id context.
event_handler = EntitiesEventHandler(

    run_service=client.run_service,
    action_service=client.action_service,
    event_callback=handle_event
)

@bp_llama.route('/api/messages/process', methods=['POST'])
@jwt_required()
def process_messages():
    """
    Handle incoming message processing requests.
    """
    logging_utility.info(f"Request received: {request.json}")
    logging_utility.info(f"Headers: {request.headers}")

    try:
        data = request.json

        messages = data.get('messages', [])
        user_id = data.get('userId') or data.get('user_id')
        thread_id = data.get('threadId') or data.get('thread_id')
        selected_model = data.get('model', 'llama3.1')
        inference_point = data.get('inferencePoint')
        provider = data.get('provider')

        logging_utility.info(
            f"Processing request: user_id={user_id}, thread_id={thread_id}, "
            f"model={selected_model}, inference_point={inference_point}, provider={provider}"
        )

        if not messages or not isinstance(messages, list):
            raise ValueError("Invalid or missing 'messages' in request")

        user_message = messages[0].get('content', '').strip()
        if not user_message:
            raise ValueError("Message content is missing")

        return conversation(
            thread_id=thread_id,
            user_message=user_message,
            user_id=user_id,
            selected_model=selected_model,
            inference_point=inference_point,
            provider=provider
        )

    except ValueError as ve:
        logging_utility.error(f"Validation error: {str(ve)}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging_utility.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the message'}), 500


def conversation(thread_id, user_message, user_id, selected_model, inference_point, provider):
    """
    Orchestrates the conversation process by managing model execution and streaming responses.
    """
    assistant = "default"

    logging_utility.info(
        f"Starting conversation: model={selected_model}, inference={inference_point}, provider={provider}"
    )

    # Create message and run
    the_message = client.message_service.create_message(
        thread_id=thread_id,
        assistant_id=assistant,
        content=user_message,
        role='user',
    )
    message_id = the_message['id']

    run = client.run_service.create_run(thread_id=thread_id, assistant_id=assistant)
    run_id = run.id

    # Start monitoring the run via the event handler.
    event_handler.start_monitoring(run_id)

    def generate_chunks():
        try:
            handler = llm_router.resolve_handler(inference_point, provider, selected_model)

            handler_class, method_name = handler.split('.')

            handler_class = LocalInference if handler_class == 'LocalInference' else CloudInference

            logging_utility.info(
                f"Using {handler_class.__name__}.{method_name} for "
                f"[{inference_point}/{provider}/{selected_model}]"
            )

            handler_instance = handler_class()
            retrieval_method = getattr(handler_instance, method_name)
            model_instance = retrieval_method()

            # Emit the run_id as an initial chunk.
            yield f"data: {json.dumps({'run_id': run_id})}\n\n"

            process_args = {
                "thread_id": thread_id,
                "message_id": message_id,
                "run_id": run.id,
                "assistant_id": assistant,
                "model": selected_model,
            }

            if selected_model == "deepseek-reasoner":
                process_args["stream_reasoning"] = True

            for chunk in model_instance.process_conversation(**process_args):
                logging_utility.debug(f"Streaming chunk: {chunk}")
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            logging_utility.error(f"Error during conversation: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate_chunks()),
        content_type='text/event-stream',
        headers={'X-Conversation-Id': run_id}
    )
