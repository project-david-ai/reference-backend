import json
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
    """
    Handle the conversation logic, including message creation, run initialization,
    and streaming the response using the appropriate LLM handler.

    Args:
        thread_id (str): The ID of the conversation thread.
        user_message (str): The message content from the user.
        user_id (str): The ID of the user.
        selected_model (str): The selected LLM model.
        inference_point (str): The type of inference ('local' or 'cloud').
        provider (str): The provider name (e.g., 'DeepSeek', 'Llama').

    Returns:
        Response: A streaming response with the conversation chunks.
    """
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
            processing_method = getattr(handler_instance, method_name)

            # Send the run_id as the first chunk
            yield f"data: {json.dumps({'run_id': run_id})}\n\n"

            # Process conversation stream

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

            # Process conversation stream
            for chunk in processing_method.process_conversation(**process_args):
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