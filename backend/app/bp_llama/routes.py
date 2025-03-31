import json
import threading
from flask import jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required

from backend.app.services.logging_service.logger import LoggingUtility
from entities import Entities
from entities.clients.actions import ActionsClient
from entities import EventsInterface  # Must expose MonitorLauncher here
from . import bp_llama

logging_utility = LoggingUtility()
client = Entities(base_url="http://localhost:9000")
actions_client = ActionsClient(base_url="http://localhost:9000")


def my_custom_tool_handler(run_id, run_data, pending_actions):
    try:
        logging_utility.info(f"[ACTION_REQUIRED] run {run_id} has {len(pending_actions)} pending action(s)")

        for action in pending_actions:
            action_id = action.get("id")
            tool_name = action.get("tool_name")
            args = action.get("function_args", {})

            logging_utility.info(f"[ACTION] ID: {action_id}, Tool: {tool_name}, Args: {args}")

            # TODO: Here you can route to your tool logic and return the result
            # You could optionally collect results and submit them using:
            # client.runs.submit_tool_outputs(...)

    except Exception as e:
        logging_utility.error(f"[ToolHandler] Error processing actions for run {run_id}: {e}")


@bp_llama.route('/api/messages/process', methods=['POST'])
@jwt_required()
def process_messages():
    logging_utility.info("Request received: %s", request.json)
    run_id_local = None

    try:
        data = request.json
        messages = data.get('messages', [])
        user_id = data.get('userId') or data.get('user_id')
        thread_id = data.get('threadId') or data.get('thread_id')
        selected_model = data.get('model', 'llama3.1')
        provider = data.get('provider', "Hyperbolic")

        if not thread_id:
            raise ValueError("Missing 'threadId' in request")
        if not messages or not isinstance(messages, list):
            raise ValueError("Invalid or missing 'messages'")
        user_message = messages[0].get('content', '').strip()
        if not user_message:
            raise ValueError("Message content is missing")

        # Step 1: Create message and run
        message = client.messages.create_message(
            thread_id=thread_id,
            assistant_id="default",
            content=user_message,
            role='user'
        )
        run = client.runs.create_run(
            thread_id=thread_id,
            assistant_id="default"
        )
        run_id = run.id
        run_id_local = run_id
        logging_utility.info(f"Created run {run_id}")

        # Step 2: Launch monitor with custom tool handler
        monitor_launcher = EventsInterface.MonitorLauncher(
            client,
            actions_client,
            run_id,
            on_action_required=my_custom_tool_handler,
            events=EventsInterface
        )
        monitor_launcher.start()

        # Step 3: Setup sync stream
        sync_stream = client.synchronous_inference_stream
        sync_stream.setup(
            user_id=user_id,
            thread_id=thread_id,
            assistant_id="default",
            message_id=message.id,
            run_id=run_id
        )

        def generate_chunks():
            try:
                for chunk in sync_stream.stream_chunks(provider=provider, model=selected_model):
                    logging_utility.debug(f"Streaming chunk: {chunk}")
                    yield json.dumps(chunk) + "\n"
                yield json.dumps({"type": "status", "status": "inference_complete"}) + "\n"
            except Exception as e:
                yield json.dumps({'type': 'error', 'error': str(e)}) + "\n"
            finally:
                try:
                    sync_stream.close()
                except Exception as e:
                    logging_utility.error(f"Error closing sync stream: {repr(e)}")

        return Response(
            stream_with_context(generate_chunks()),
            content_type='application/x-ndjson',
            headers={
                'X-Conversation-Id': run_id,
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Expose-Headers': 'X-Conversation-Id'
            }
        )

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging_utility.error(f"Unexpected error in /process: {repr(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
