import json
import time

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
      - Stream inference response chunks as properly formatted JSON.
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
        provider = data.get('provider', "Hyperbolic")  # Force provider to "Hyperbolic"


        print(selected_model)
        print(provider)
        #time.sleep(1000)



        logging_utility.info(
            "Processing request: user_id=%s, thread_id=%s, model=%s, inference_point=%s, provider=%s",
            user_id, thread_id, selected_model, inference_point, provider
        )

        if not messages or not isinstance(messages, list):
            raise ValueError("Invalid or missing 'messages' in request")

        user_message = messages[0].get('content', '').strip()
        if not user_message:
            raise ValueError("Message content is missing")

        # Create a message record via the Entities client.
        message = client.messages.create_message(
            thread_id=thread_id,
            assistant_id="default",
            content=user_message,
            role='user'
        )

        # Create a run record
        run = client.runs.create_run(
            thread_id=thread_id,
            assistant_id="default"
        )
        run_id = run.id

        # Initialize the synchronous inference stream wrapper
        sync_stream = client.synchronous_inference_stream
        sync_stream.setup(
            user_id=user_id,
            thread_id=thread_id,
            assistant_id="default",
            message_id=message.id,
            run_id=run_id
        )

        # Define a generator function to stream response chunks as raw JSON
        def generate_chunks():
            try:
                for chunk in sync_stream.stream_chunks(provider=provider, model=selected_model):
                    logging_utility.debug("Streaming chunk: %s", chunk)
                    # Make sure each JSON object is on its own line with a newline terminator
                    yield json.dumps(chunk) + "\n"
                # Send completion marker
                yield json.dumps({"type": "status", "status": "complete"}) + "\n"
            except Exception as e:
                err_msg = str(e) or repr(e)
                logging_utility.error("Error during streaming inference: %s", err_msg)
                yield json.dumps({'type': 'error', 'error': err_msg}) + "\n"
            finally:
                logging_utility.info("Cleaning up streaming resources.")
                try:
                    sync_stream.close()
                except Exception as e:
                    logging_utility.error("Error closing synchronous inference stream: %s", repr(e))

        # Return the streaming response with appropriate headers for JSON streaming
        return Response(
            stream_with_context(generate_chunks()),
            content_type='application/x-ndjson',  # Using newline delimited JSON format
            headers={
                'X-Conversation-Id': run_id,
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',  # Add CORS header if needed
                'Access-Control-Expose-Headers': 'X-Conversation-Id'
            }
        )

    except ValueError as ve:
        logging_utility.error("Validation error: %s", str(ve))
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging_utility.error("Unexpected error: %s", repr(e))
        return jsonify({'error': 'An error occurred while processing the message'}), 500