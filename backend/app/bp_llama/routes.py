import json
from flask import jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required

# Import backend services for routing and logging.
from backend.app.services.llm_routing_services.llm_router_service import LlmRouter
from backend.app.services.logging_service.logger import LoggingUtility

# Import the public SDK interface.
from entities import Entities

# Initialize logging.
logging_utility = LoggingUtility()

# Instantiate the main Entities client.
client = Entities()

# Initialize the LLM router with the configuration file.
llm_router = LlmRouter('llm_model_routing_config.json')

# Import the Flask blueprint.
from . import bp_llama


@bp_llama.route('/api/messages/process', methods=['POST'])
@jwt_required()
def process_messages():
    """
    Handle incoming message processing requests:
      - Validate the request.
      - Create message and run records via the Entities client.
      - Immediately stream inference response chunks from the Entities client.
    """
    logging_utility.info("Request received: %s", request.json)
    logging_utility.info("Headers: %s", request.headers)

    try:
        data = request.json

        messages = data.get('messages', [])
        user_id = data.get('userId') or data.get('user_id')
        thread_id = data.get('threadId') or data.get('thread_id')
        selected_model = data.get('model', 'llama3.1')
        inference_point = data.get('inferencePoint')
        # Force provider to "Hyperbolic"
        provider = data.get('provider', "Hyperbolic")

        logging_utility.info(
            "Processing request: user_id=%s, thread_id=%s, model=%s, inference_point=%s, provider=%s",
            user_id, thread_id, selected_model, inference_point, provider
        )

        if not messages or not isinstance(messages, list):
            raise ValueError("Invalid or missing 'messages' in request")

        user_message = messages[0].get('content', '').strip()
        if not user_message:
            raise ValueError("Message content is missing")

        # Create message and run records via the Entities client.
        the_message = client.message_service.create_message(
            thread_id=thread_id,
            assistant_id="default",
            content=user_message,
            role='user'
        )
        message_id = the_message['id']

        run = client.run_service.create_run(
            thread_id=thread_id,
            assistant_id="default"
        )
        run_id = run.id

        def generate_chunks():
            try:
                # Resolve the proper inference handler (if needed)
                # handler = llm_router.resolve_handler(inference_point, provider, selected_model)
                # For now we directly stream using the inference service:
                for chunk in client.inference_service.stream_inference_response(
                        provider="Hyperbolic",
                        model=selected_model,
                        thread_id=thread_id,
                        message_id=message_id,
                        run_id=run_id,
                        assistant_id="default"
                ):
                    logging_utility.debug("Streaming chunk: %s", chunk)
                    yield "data: " + json.dumps(chunk) + "\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                err_msg = str(e) or repr(e)
                logging_utility.error("Error during streaming inference: %s", err_msg)
                yield "data: " + json.dumps({"error": err_msg}) + "\n\n"
            finally:
                try:
                    client.inference_service.close()
                except Exception as e:
                    logging_utility.error("Error closing inference service: %s", repr(e))

        return Response(
            stream_with_context(generate_chunks()),
            content_type='text/event-stream',
            headers={
                'X-Conversation-Id': run_id,
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )

    except ValueError as ve:
        logging_utility.error("Validation error: %s", str(ve))
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging_utility.error("Unexpected error: %s", repr(e))
        return jsonify({'error': 'An error occurred while processing the message'}), 500
