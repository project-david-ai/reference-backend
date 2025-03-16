import json
import asyncio

from flask import jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required

# Import backend services needed for routing and logging.
from backend.app.services.llm_routing_services.llm_router_service import LlmRouter
from backend.app.services.logging_service.logger import LoggingUtility

# Import the public SDK interface.
from entities import Entities

# Initialize logging.
logging_utility = LoggingUtility()

# Instantiate the main Entities client, which exposes all functionality (including inference_service).
client = Entities()

# Initialize the LLM router with the configuration file.
llm_router = LlmRouter('llm_model_routing_config.json')

# Import the Flask blueprint (adjust as needed for your project).
from . import bp_llama


@bp_llama.route('/api/messages/process', methods=['POST'])
@jwt_required()
def process_messages():
    """
    Handle incoming message processing requests:
      - Validates the request.
      - Creates message and run records via the Entities client.
      - Streams inference response chunks via the asynchronous inference service.
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
        provider = data.get('provider')

        # Forcing provider to "Hyperbolic"
        provider = "Hyperbolic"

        logging_utility.info(
            "Processing request: user_id=%s, thread_id=%s, model=%s, inference_point=%s, provider=%s",
            user_id, thread_id, selected_model, inference_point, provider
        )

        if not messages or not isinstance(messages, list):
            raise ValueError("Invalid or missing 'messages' in request")

        user_message = messages[0].get('content', '').strip()
        if not user_message:
            raise ValueError("Message content is missing")

        # Create a message record using the Entities client's message service.
        the_message = client.message_service.create_message(
            thread_id=thread_id,
            assistant_id="default",
            content=user_message,
            role='user'
        )
        message_id = the_message['id']

        # Create a run record using the Entities client's run service.
        run = client.run_service.create_run(
            thread_id=thread_id,
            assistant_id="default"
        )
        run_id = run.id

        # Define an asynchronous generator that streams inference response chunks.
        async def async_generate_chunks():
            try:
                async for chunk in client.inference_service.stream_inference_response(
                        provider="Hyperbolic",
                        model=selected_model,
                        thread_id=thread_id,
                        message_id=message_id,
                        run_id=run_id,
                        assistant_id="default"
                ):
                    logging_utility.debug("Streaming chunk: %s", chunk)
                    yield "data: " + json.dumps(chunk) + "\n\n"
            except Exception as e:
                logging_utility.error("Error during streaming inference: %s", str(e))
                yield "data: " + json.dumps({"error": str(e)}) + "\n\n"
            finally:
                # Close the inference service
                # Since we're within an async generator, schedule the close.
                await client.inference_service.close()

        # Wrap the asynchronous generator in a synchronous generator.
        def generate_chunks():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            gen = async_generate_chunks()  # Async generator instance
            try:
                while True:
                    try:
                        chunk = loop.run_until_complete(gen.__anext__())
                        yield chunk
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()

        # Return a Server-Sent Events (SSE) response.
        return Response(
            stream_with_context(generate_chunks()),
            content_type='text/event-stream',
            headers={'X-Conversation-Id': run_id}
        )

    except ValueError as ve:
        logging_utility.error("Validation error: %s", str(ve))
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging_utility.error("Unexpected error: %s", str(e))
        return jsonify({'error': 'An error occurred while processing the message'}), 500
