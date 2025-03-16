from entities import Entities

from flask import jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required
from backend.app.services.logging_service.logger import LoggingUtility
from . import bp_common

# Initialize the LoggingUtility instance
logging_utility = LoggingUtility()

# Initialize the client
client = Entities()


@bp_common.route('/api/thread/create', methods=['POST'])
@jwt_required()
def create_thread():
    """
    API endpoint to create a new thread.

    Returns:
        str: The ID of the created thread.
    """
    data = request.json
    userId = data.get('userId')

    if not userId:
        return jsonify({"error": "userId is required"}), 400

    logging_utility.info("Received request to create a thread for user ID: %s", userId)

    try:
        # Attempt to create a thread
        thread = client.thread_service.create_thread(participant_ids=[userId])
        logging_utility.info("Thread created successfully. Thread ID: %s", thread.id)

        return jsonify({"thread_id": thread.id}), 201  # Return the thread ID with a 201 status code

    except Exception as e:
        # Log the error with the exception details
        logging_utility.error("Failed to create thread for user ID: %s. Error: %s", userId, str(e))
        return jsonify({"error": "Failed to create thread"}), 500  # Return a 500 status code for server error


@bp_common.route('/api/thread/list', methods=['GET'])
@jwt_required()
def list_threads():
    """
    API endpoint to fetch a list of threads for the given user ID.

    Returns:
        dict: A dictionary containing a list of thread IDs.
    """
    data = request.args
    user_id = data.get('userId') or data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    logging_utility.info("Received request to fetch threads for user ID: %s", user_id)

    try:
        # Attempt to list threads
        threads = client.thread_service.list_threads(user_id=user_id)
        logging_utility.info("Threads listed successfully. Number of threads: %d", len(threads))

        return jsonify({"thread_ids": threads}), 200

    except Exception as e:
        # Log the error with the exception details
        logging_utility.error("Failed to list threads for user ID: %s. Error: %s", user_id, str(e))
        return jsonify({"error": "Failed to list threads"}), 500  # Return a 500 status code for server error


@bp_common.route('/api/message/list', methods=['GET'])
@jwt_required()
def list_messages():
    thread_id = request.args.get('thread_id')
    if not thread_id:
        return jsonify({"error": "Missing 'thread_id' parameter"}), 400

    try:
        messages = client.message_service.list_messages(thread_id=thread_id)
        logging_utility.info("Listed messages successfully. Number of messages: %d", len(messages))
        return jsonify({"messages": messages}), 200
    except Exception as e:
        logging_utility.error("Failed to list messages for thread ID: %s. Error: %s", thread_id, str(e))
        return jsonify({"error": "Failed to list messages"}), 500


@bp_common.route('/api/run/cancel', methods=['POST'])
@jwt_required()
def cancel_run():
    try:
        # Extract the run_id from the request
        run_id = request.json.get('run_id')

        if not run_id:
            logging_utility.error("Missing 'run_id' in request")
            return jsonify({"error": "Missing 'run_id' parameter"}), 400

        # Attempt to cancel the run
        client.run_service.cancel_run(run_id=run_id)
        logging_utility.info("Run with ID %s cancelled successfully", run_id)

        return 200
        #return jsonify({"message": f"Run {run_id} cancelled successfully"}), 200

    except Exception as e:
        # Log the error with the exception details
        logging_utility.error("Failed to cancel run with ID %s. Error: %s", run_id, str(e))
        return jsonify({"error": "Failed to cancel run"}), 500



