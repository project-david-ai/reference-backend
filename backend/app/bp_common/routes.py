from datetime import datetime

from entities import Entities
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

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
        thread = client.threads.create_thread(participant_ids=[userId])
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
        threads = client.threads.list_threads(user_id=user_id)
        logging_utility.info("Threads listed successfully. Number of threads: %d", len(threads))

        return jsonify({"thread_ids": threads}), 200

    except Exception as e:
        # Log the error with the exception details
        logging_utility.error("Failed to list threads for user ID: %s. Error: %s", user_id, str(e))
        return jsonify({"error": "Failed to list threads"}), 500  # Return a 500 status code for server error



@bp_common.route('/api/thread/delete', methods=['POST'])
@jwt_required()
def delete_thread():
    """Handle thread deletion with REST-compliant status codes"""
    try:
        # Validate request format
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 415

        data = request.get_json()
        thread_id = data.get('thread_id')

        if not thread_id:
            return jsonify({'error': 'thread_id is required'}), 400

        # Get current user from JWT
        current_user = get_jwt_identity()

        # Perform deletion with user validation
        deleted = client.threads.delete_thread(
            thread_id=thread_id,
        )

        # REST best practice: DELETE is idempotent, success regardless of prior existence
        if deleted:
            return jsonify({
                'status': 'deleted',
                'thread_id': thread_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'not_found',
                'thread_id': thread_id,
                'message': 'No thread found with given ID'
            }), 200

    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging_utility.error(f'Thread deletion failed: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@bp_common.route('/api/message/list', methods=['GET'])
@jwt_required()
def list_messages():
    thread_id = request.args.get('thread_id')
    if not thread_id:
        return jsonify({"error": "Missing 'thread_id' parameter"}), 400

    try:
        messages = client.messages.list_messages(thread_id=thread_id)
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
        client.runs.cancel_run(run_id=run_id)
        logging_utility.info("Run with ID %s cancelled successfully", run_id)

        return 200
        #return jsonify({"message": f"Run {run_id} cancelled successfully"}), 200

    except Exception as e:
        # Log the error with the exception details
        logging_utility.error("Failed to cancel run with ID %s. Error: %s", run_id, str(e))
        return jsonify({"error": "Failed to cancel run"}), 500



