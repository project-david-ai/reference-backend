import json
import time
from typing import List, Dict, Any

import ollama
from dotenv import load_dotenv
from flask import jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required

from backend.app.services.logging_service.logger import LoggingUtility
from . import bp_llama
from ..models import Assistant

client = ollama.OllamaClient()
logging_utility = LoggingUtility()
load_dotenv()

current_run = {}


def show_json(obj):
    json_str = json.dumps(obj, indent=4)
    print(json_str)


def assistant_run_status_checker(run):
    show_json(run)


@bp_llama.route('/api/assistant/run-status', methods=['GET'])
def assistant_run_status():
    thread_id = current_run.get('thread_id')
    run_id = current_run.get('run_id')

    if thread_id and run_id:
        run = client.run_service.retrieve_run(request_id=run_id, thread_id=thread_id)
        return jsonify({"status": run.status})
    else:
        return jsonify({"status": "not_found"}), 404


@bp_llama.route('/api/messages/process', methods=['POST'])
@jwt_required()
def process_messages():
    logging_utility = LoggingUtility()

    # Debug statement to log headers
    logging_utility.info(f"Headers: {request.headers}")

    incoming_messages = request.json.get('messages', [])
    user_id = request.json.get('userId')  # Get user ID from the request payload
    thread_id = request.json.get('threadId')
    selected_model = request.json.get('model', 'llama3.1')
    logging_utility.info("Incoming request: %d messages, userId=%s, threadId=%s, model=%s",
                         len(incoming_messages), user_id, thread_id, selected_model)

    try:
        # Ensure that incoming_messages is a list of dictionaries
        logging_utility.info(f"Message structure: {incoming_messages}")
        if isinstance(incoming_messages, list) and all(isinstance(msg, dict) for msg in incoming_messages):
            # Extract the content from the first message
            user_message = incoming_messages[0].get('content', '') if incoming_messages else ''
            logging_utility.info("Processing conversation for thread ID: %s", thread_id)
            response = conversation(thread_id=thread_id, user_message=user_message,
                                    user_id=user_id, selected_model=selected_model)
            return response
        else:
            raise ValueError("Invalid message format")

    except Exception as e:
        logging_utility.error("Error in process_messages: %s", str(e))
        return jsonify({'error': 'An error occurred while processing the message'}), 500


@bp_llama.route('/api/threads/create', methods=['POST'])
@jwt_required()
def create_thread():
    logging_utility.info("Received request to create a new thread")
    thread_id = create_new_thread()
    if thread_id:
        logging_utility.info("Successfully created a new thread with ID: %s", thread_id)
        return jsonify({'thread_id': thread_id}), 200
    else:
        logging_utility.error("Failed to create a new thread")
        return jsonify({'error': 'Failed to create thread'}), 500


@bp_llama.route('/api/threads/delete', methods=['POST'])
@jwt_required()
def delete_thread():
    thread_id = request.json.get('thread_id')
    if not thread_id:
        logging_utility.error("No thread ID provided in request")
        return jsonify({'error': 'No thread ID provided'}), 400

    logging_utility.info("Received request to delete thread with ID: %s", thread_id)
    success = delete_existing_thread(thread_id)
    if success:
        logging_utility.info("Successfully deleted thread with ID: %s", thread_id)
        return jsonify({'message': 'Thread deleted successfully'}), 200
    else:
        logging_utility.error("Failed to delete thread with ID: %s", thread_id)
        return jsonify({'error': 'Failed to delete thread'}), 500


@bp_llama.route('/api/assistants/create', methods=['POST'])
@jwt_required()
def create_assistant():
    logging_utility.info("Received request to create a new assistant")

    # Extract data from request
    data = request.json
    user_id = data.get('user_id')
    model = data.get('model')
    instructions = data.get('instructions')
    name = data.get('name', '')
    tools = data.get('tools', [])
    description = data.get('description', '')

    # Validate required fields
    if not all([user_id, model]):
        logging_utility.error("Missing required fields for assistant creation")
        return jsonify({'error': 'Missing required fields'}), 400

    result = create_new_assistant(
        user_id=user_id,
        model=model,
        instructions=instructions,
        name=name,
        tools=tools,
        description=description
    )

    if result:
        logging_utility.info("Successfully created a new assistant with ID: %s", result['assistant_id'])
        return jsonify(result), 200
    else:
        logging_utility.error("Failed to create a new assistant")
        return jsonify({'error': 'Failed to create assistant'}), 500

# Helpers here


@bp_llama.route('/api/threads/list', methods=['GET'])
@jwt_required()
def list_threads_route():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        threads = list_threads(user_id)
        return jsonify({'threads': threads}), 200
    except Exception as e:
        logging_utility.error(f"Error in list_threads_route: {str(e)}")
        return jsonify({'error': 'An error occurred while listing threads'}), 500


@bp_llama.route('/api/messages/list', methods=['GET'])
@jwt_required()
def get_messages():
    thread_id = request.args.get('thread_id')
    if not thread_id:
        return jsonify({'error': 'Thread ID is required'}), 400

    messages = list_messages(thread_id)
    return jsonify(messages)





def conversation(thread_id, user_message, user_id, selected_model):
    logging_utility.info("Starting a conversation for user ID: %s with model: %s", user_id, selected_model)

    try:
        # Check if the user already has an assistant
        assistant_record = Assistant.query.filter_by(user_id=user_id).first()

        if not assistant_record:
            logging_utility.error("No assistant found for user ID: %s", user_id)
            return jsonify({'error': 'No assistant found for the user'}), 400

        # Create user
        user1 = client.user_service.create_user(name='Test')
        logging_utility.info("Created user with ID: %s", user1.id)

        # Create a thread
        message = client.message_service.create_message(thread_id=thread_id,
                                                        content=user_message,
                                                        sender_id=user1.id,
                                                        role='user')
        logging_utility.info("Created message: %s with message ID: %s", message, message['id'])

        assistant_id = "asst_FuirCRmKlUvz4uNVVottMv"
        run = client.run_service.create_run(assistant_id=assistant_id, thread_id=thread_id)
        run_id = run['id']
        logging_utility.info("Created run: %s with run ID: %s", run, run_id)

        def generate():
            yield f"data: {json.dumps({'thread_id': thread_id})}\n\n"
            logging_utility.info("Sending initial thread ID: %s", thread_id)
            try:
                for chunk in client.process_conversation(thread_id=thread_id, run_id=run_id, assistant_id=assistant_id, model=selected_model):
                    # Ensure the chunk is a valid JSON before sending it
                    try:
                        json_chunk = json.dumps({'chunk': chunk})
                        logging_utility.info("Sending JSON chunk: %s", json_chunk)
                        yield f"data: {json_chunk}\n\n"
                    except json.JSONDecodeError as json_error:
                        logging_utility.error("Failed to encode chunk as JSON: %s", json_error)
                        yield f"data: {json.dumps({'error': 'Invalid chunk format'})}\n\n"
            except Exception as e:
                logging_utility.error("Error during conversation processing: %s", str(e))
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
            logging_utility.info("Conversation processing completed.")

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    except Exception as e:
        logging_utility.error("Error in start_new_conversation: %s", str(e))
        return jsonify({'error': 'An error occurred while starting a new conversation'}), 500


def create_new_thread():
    try:
        thread = client.thread_service.create_thread()
        logging_utility.info("Created thread: %s with thread ID: %s", thread, thread.id)
        return thread.id
    except Exception as e:
        logging_utility.error("Error creating thread: %s", str(e))
        return None


def delete_existing_thread(thread_id: str) -> bool:
    try:
        client.thread_service.delete_thread(thread_id=thread_id)
        logging_utility.info("Deleted thread with ID: %s", thread_id)
        return True
    except Exception as e:
        logging_utility.error("Error deleting thread: %s", str(e))
        return False


def create_new_assistant(user_id: str, model: str, instructions: str = None, name: str = "", tools: List[Dict[str, Any]] = None, description: str = ""):
    try:
        # Validate that instructions and tools are provided
        if instructions is None:
            raise ValueError("Instructions are required but not provided")

        if tools is None:
            raise ValueError("Tools are required but not provided")

        # Hardcoded user_id for now
        user_id = "user_zFu5VPLgtpzGIqMN30eccb"
        assistant = client.assistant_service.create_assistant(
            user_id=user_id,
            model=model,
            name=name,
            instructions=instructions,
            tools=tools,
            description=description
        )

        logging_utility.info("Created assistant: %s", assistant.id)
        logging_utility.info("Created assistant: %s with assistant ID: %s", assistant.name, assistant.id)

        # Return the assistant ID
        return {
            "assistant_id": assistant.id
        }
    except Exception as e:
        logging_utility.error("Error creating assistant: %s", str(e))
        return None


def list_messages(thread_id: str) -> List[Dict[str, Any]]:
    try:
        # Retrieve messages for the given thread ID
        messages = client.message_service.list_messages(thread_id=thread_id)
        logging_utility.info(f"Retrieved messages for thread_id {thread_id}")

        logging_utility.info(f"Formatted message list for thread_id {thread_id}")

        print(messages)

        return messages

    except Exception as e:
        logging_utility.error(f"Error in list_messages for thread_id {thread_id}: {str(e)}")
        return []


def list_threads(user_id: str) -> List[Dict[str, Any]]:
    try:

        user_id = "user_jFrcfHoIEshRToPdCaASqe"

        threads = client.thread_service.list_threads(user_id=user_id)
        logging_utility.info(f"Retrieved threads for user_id {user_id}")

        logging_utility.info(f"Formatted thread list for user_id {user_id}")

        return threads

    except Exception as e:
        logging_utility.error(f"Error in list_threads for user_id {user_id}: {str(e)}")
        return []






