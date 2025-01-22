# backend/app/bp_llama/routes.py
import json
from flask import jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required
from entities_api import OllamaClient, ClientAssistantService, LocalInference
from backend.app.services.logging_service.logger import LoggingUtility


from . import bp_llama

logging_utility = LoggingUtility()

client = OllamaClient()


@bp_llama.route('/api/messages/process', methods=['POST'])
@jwt_required()
def process_messages():
    logging_utility.info(f"Request data: {request.json}")
    logging_utility.info(f"Headers: {request.headers}")

    try:
        data = request.json

        # Handle both camelCase and snake_case
        messages = data.get('messages', [])
        user_id = data.get('userId') or data.get('user_id')  # Handle both cases
        thread_id = data.get('threadId') or data.get('thread_id')  # Handle both cases
        selected_model = data.get('model', 'llama3.1')

        logging_utility.info("Incoming request: user_id=%s, thread_id=%s, model=%s",
                             user_id, thread_id, selected_model)

        if not messages or not isinstance(messages, list):
            raise ValueError("Invalid or missing 'messages' in request")

        user_message = messages[0].get('content', '')
        if not user_message:
            raise ValueError("Message content is missing")

        logging_utility.info("Processing conversation for thread ID: %s", thread_id)
        response = conversation(thread_id=thread_id, user_message=user_message,
                                user_id=user_id, selected_model=selected_model)
        return response

    except ValueError as ve:
        logging_utility.error("Validation error in process_messages: %s", str(ve))
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging_utility.error("Error in process_messages: %s", str(e))
        return jsonify({'error': 'An error occurred while processing the message'}), 500


def conversation(thread_id, user_message, user_id, selected_model):

    assistant = "asst_NEyUOqgjpLutD581F2o3EU"

    the_message = client.message_service.create_message(thread_id=thread_id,
                                          content=user_message,
                                          role='user',
                                          sender_id=user_id)

    message_id = the_message['id']

    run = client.run_service.create_run(thread_id=thread_id, assistant_id=assistant)
    run_id = run.id

    def generate_chunks():

        inference = LocalInference()

        try:
            # Send the run_id as the first chunk
            yield f"data: {json.dumps({'run_id': run_id})}\n\n"

            for chunk in inference.process_conversation(thread_id=thread_id,
                                                        message_id=message_id,
                                                        run_id=run.id,
                                                        assistant_id=assistant,
                                                        model='llama3.1'):

                logging_utility.debug("Received chunk: %s", chunk)

                # Wrap the entire chunk in a JSON object to ensure it's valid
                json_chunk = {
                    "chunk": chunk
                }

                yield f"data: {json.dumps(json_chunk)}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            logging_utility.error(f"Error during conversation: {str(e)}")
            yield "data: [ERROR]\n\n"

    return Response(stream_with_context(generate_chunks()), content_type='text/event-stream')
