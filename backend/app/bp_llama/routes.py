import json
import time
import threading
from flask import jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required
from entities_api import OllamaClient, ClientAssistantService, LocalInference, CloudInference
from backend.app.services.logging_service.logger import LoggingUtility
from backend.app.services.llm_routing_services.llm_router_service import LlmRouter
from . import bp_llama

logging_utility = LoggingUtility()
client = OllamaClient()

# Initialize the LlmRouter with the path to the routing configuration file
llm_router = LlmRouter('llm_model_routing_config.json')


def monitor_run_status(run_id: str, run_service):
    """
    Continuously monitor the status of a run and handle specific statuses like 'action_required'.
    """
    while True:
        try:
            run = run_service.retrieve_run(run_id)
            logging_utility.info(f"Run {run_id} status: {run.status}")

            if run.status == "action_required":
                logging_utility.info("Action required for run %s. Handling...", run_id)

                # Fetch pending actions for the run
                pending_actions = client.get_action_service.get_pending_actions(run_id=run_id)
                logging_utility.info(f"Pending actions for run {run_id}: {pending_actions}")

                # Perform actions for 'action_required' status
                handle_action_required(run, pending_actions)
                break  # Exit the loop after handling

            elif run.status in ["completed", "failed", "cancelled"]:
                logging_utility.info("Run %s has ended with status: %s", run_id, run.status)
                break  # Exit the loop if the run has ended

            # Wait before polling again
            time.sleep(2)  # Adjust the polling interval as needed

        except Exception as e:
            logging_utility.error(f"Error monitoring run {run_id}: {str(e)}")
            break


def handle_action_required(run, pending_actions):
    """
    Handle the 'action_required' status for a run by processing pending actions.
    """
    logging_utility.info(f"Handling action required for run {run.id}")

    if not pending_actions:
        logging_utility.info("No pending actions found for run %s", run.id)
        return

    for action in pending_actions:
        action_id = action.get("action_id")
        tool_name = action.get("tool_name")
        function_arguments = action.get("function_arguments")
        run_id = action.get("run_id")

        logging_utility.info(
            f"Processing pending action: action_id={action_id}, tool_name={tool_name}, "
            f"function_arguments={function_arguments}, run_id={run_id}"
        )

        # Add your logic here to handle the pending action
        # For example, trigger a tool, update the action status, or notify the user
        # Example:
        # result = trigger_tool(tool_name, function_arguments)
        # client.get_action_service.update_action(action_id, status="completed", result=result)
        # notify_user(run.thread_id, f"Action {action_id} completed for tool {tool_name}.")


@bp_llama.route('/api/messages/process', methods=['POST'])
@jwt_required()
def process_messages():
    """
    Handle incoming message processing requests. This endpoint validates the request,
    resolves the appropriate LLM handler, and streams the conversation response.

    Returns:
        Response: A streaming response with the conversation chunks.
    """
    logging_utility.info(f"Request data: {request.json}")
    logging_utility.info(f"Headers: {request.headers}")

    try:
        data = request.json

        # Handle both camelCase and snake_case
        messages = data.get('messages', [])
        user_id = data.get('userId') or data.get('user_id')
        thread_id = data.get('threadId') or data.get('thread_id')
        selected_model = data.get('model', 'llama3.1')  # Default to 'llama3.1' if not provided
        inference_point = data.get('inferencePoint')  # 'local' or 'cloud'
        provider = data.get('provider')  # 'DeepSeek', 'Llama', etc.

        # Log the selected model, inference type, and provider
        logging_utility.info(f"Selected model: {selected_model}")
        logging_utility.info(f"Inference type: {inference_point}")
        logging_utility.info(f"Provider: {provider}")
        logging_utility.info(
            "Incoming request: user_id=%s, thread_id=%s, model=%s, inference_point=%s, provider=%s",
            user_id, thread_id, selected_model, inference_point, provider
        )

        if not messages or not isinstance(messages, list):
            raise ValueError("Invalid or missing 'messages' in request")

        user_message = messages[0].get('content', '')
        if not user_message:
            raise ValueError("Message content is missing")

        logging_utility.info("Processing conversation for thread ID: %s", thread_id)

        response = conversation(
            thread_id=thread_id,
            user_message=user_message,
            user_id=user_id,
            selected_model=selected_model,
            inference_point=inference_point,
            provider=provider
        )
        return response

    except ValueError as ve:
        logging_utility.error("Validation error in process_messages: %s", str(ve))
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging_utility.error("Error in process_messages: %s", str(e))
        return jsonify({'error': 'An error occurred while processing the message'}), 500


def conversation(thread_id, user_message, user_id, selected_model, inference_point, provider):
    assistant = "asst_NEyUOqgjpLutD581F2o3EU"

    # Log the selected model, inference type, and provider at the start of the conversation
    logging_utility.info(
        f"Starting conversation: model={selected_model}, "
        f"inference={inference_point}, provider={provider}"
    )

    # Create message and run
    the_message = client.message_service.create_message(
        thread_id=thread_id,
        content=user_message,
        role='user',
        sender_id=user_id
    )
    message_id = the_message['id']

    run = client.run_service.create_run(thread_id=thread_id, assistant_id=assistant)
    run_id = run.id

    # Start monitoring the run status in a separate thread
    status_monitor_thread = threading.Thread(
        target=monitor_run_status,
        args=(run_id, client.run_service)
    )
    status_monitor_thread.start()

    def generate_chunks():
        try:
            # Resolve the appropriate handler using LlmRouter
            handler = llm_router.resolve_handler(inference_point, provider, selected_model)
            handler_class, method_name = handler.split('.')
            handler_class = LocalInference if handler_class == 'LocalInference' else CloudInference

            logging_utility.info(
                f"Using {handler_class.__name__}.{method_name} for "
                f"[{inference_point}/{provider}/{selected_model}]"
            )

            # Get the processing method
            handler_instance = handler_class()
            retrieval_method = getattr(handler_instance, method_name)
            model_instance = retrieval_method()  # Get the actual model instance

            # Send the run_id as the first chunk
            yield f"data: {json.dumps({'run_id': run_id})}\n\n"

            # Prepare arguments for process_conversation
            process_args = {
                "thread_id": thread_id,
                "message_id": message_id,
                "run_id": run.id,
                "assistant_id": assistant,
                "model": selected_model,
            }

            # Conditionally add stream_reasoning only for "deepseek-reasoner"
            if selected_model == "deepseek-reasoner":
                process_args["stream_reasoning"] = True

            # Process conversation stream using the actual instance
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