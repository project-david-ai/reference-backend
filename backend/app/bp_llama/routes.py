import threading
import json
import os
import time
from flask import jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required
from projectdavid import Entity
from projectdavid_common import UtilsInterface

from . import bp_llama

logging_utility = UtilsInterface.LoggingUtility()
client = Entity(base_url="http://localhost:9000") # Assuming client is initialized

# --- Shared State ---
# Stores information about runs currently being processed
# Needs cleanup after request finishes or times out
_run_status_lock = threading.Lock()
_run_status_registry = {} # run_id -> {"tool_handled": False, "start_time": time.time()}
# --- End Shared State ---


# --- Faux Handler (Unchanged) ---
def faux_tool_handler(tool_name, arguments):
    # ... (keep existing implementation) ...
    logging_utility.info(f"[FauxHandler] Handling tool: {tool_name}")
    logging_utility.info(f"[FauxHandler] Arguments: {arguments}")

    if tool_name == 'get_flight_times':
        departure = arguments.get('departure', 'Unknown')
        arrival = arguments.get('arrival', 'Unknown')
        result = {
            "status": "success",
            "message": f"Simulated flight time for {departure} to {arrival}: 4 hours 30 minutes.",
            "departure_time": "10:00 AM PST",
            "arrival_time": "06:30 PM EST"
        }
        return json.dumps(result)
    else:
        result = {
            "status": "success",
            "message": f"Simulated successful execution of tool '{tool_name}'."
        }
        return json.dumps(result)


# --- Modified Poller ---
def poll_and_handle_pending_actions(run_id, thread_id, assistant_id, interval=0.2, timeout=30):
    """
    Polls for pending actions, handles them, submits output,
    AND sets a flag in the shared registry upon successful handling.
    """
    def _monitor():
        global _run_status_registry, _run_status_lock # Allow modification
        logging_utility.info(f"[ActionHandler] Starting polling/handling loop for run {run_id}")
        start_time = time.time()
        action_handled_successfully = False # Track success specifically

        while (time.time() - start_time) < timeout:
            # Check if the run still exists in registry (might have been cleaned up)
            with _run_status_lock:
                if run_id not in _run_status_registry:
                    logging_utility.warning(f"[ActionHandler] Run {run_id} no longer in registry, stopping poll.")
                    break

            action_to_handle = None
            try:
                logging_utility.debug(f"[ActionHandler] Checking pending actions for run {run_id}")
                pending_actions = client.actions.get_pending_actions(run_id=run_id)

                if pending_actions and isinstance(pending_actions, list) and len(pending_actions) > 0:
                    action_to_handle = pending_actions[0] # Grab potential action data

            except Exception as e:
                logging_utility.error(f"[ActionHandler] Error checking actions for run {run_id}: {e}", exc_info=True)
                # Decide if we should break or continue polling after an error during check
                time.sleep(interval * 2) # Longer sleep on error
                continue # Try checking again

            # --- Process the action if found ---
            if action_to_handle:
                action_id = action_to_handle.get('action_id')
                tool_name = action_to_handle.get('tool_name')
                function_arguments = action_to_handle.get('function_arguments')
                current_run_status = action_to_handle.get('run_status')

                logging_utility.info(f"[ActionHandler] Found pending action: ID={action_id}, Tool={tool_name}, Status={current_run_status}")

                if not action_id or not tool_name:
                    logging_utility.error(f"[ActionHandler] Invalid action data found: {action_to_handle}")
                    time.sleep(interval)
                    continue

                try:
                    # --- Call Handler & Submit ---
                    tool_output_content = faux_tool_handler(tool_name, function_arguments)
                    logging_utility.info(f"[ActionHandler] Submitting tool output for action {action_id}...")

                    client.messages.submit_tool_output(
                        thread_id=thread_id,
                        tool_id=action_id,
                        content=tool_output_content,
                        role="tool",
                        assistant_id=assistant_id
                    )
                    client.runs.update_run_status(run_id=run_id, new_status='processing')

                    logging_utility.info(f"[ActionHandler] Successfully submitted tool output for action {action_id}")

                    # *** SET THE FLAG on SUCCESS ***
                    with _run_status_lock:
                        if run_id in _run_status_registry: # Check again, might have been cleaned up
                            _run_status_registry[run_id]['tool_handled'] = True
                            logging_utility.info(f"[ActionHandler] Marked tool_handled=True for run {run_id}")

                    action_handled_successfully = True
                    break # Exit the while loop after successful handling

                except Exception as e:
                     logging_utility.error(f"[ActionHandler] Error handling/submitting action {action_id} for run {run_id}: {e}", exc_info=True)
                     # Don't set flag, break loop to prevent retries on submission error?
                     break
            else:
                logging_utility.debug(f"[ActionHandler] No pending actions found for run {run_id}.")

            # --- Check Run Status for Completion/Failure ---
            # Optional: Check run status (e.g., client.runs.get_run(run_id))
            # If status becomes 'completed', 'failed', 'expired', etc., stop polling.
            # try:
            #    current_run = client.runs.get_run(run_id)
            #    if current_run.status not in ['queued', 'in_progress', 'action_required', 'processing']:
            #        logging_utility.info(f"[ActionHandler] Run {run_id} reached terminal state {current_run.status}, stopping poll.")
            #        break
            # except Exception as e:
            #    logging_utility.warning(f"[ActionHandler] Could not get run status for {run_id}: {e}")

            time.sleep(interval) # Wait before next poll

        # --- Loop End Logging ---
        if not action_handled_successfully and (time.time() - start_time) >= timeout:
            logging_utility.warning(f"[ActionHandler] Timeout reached waiting for pending actions on run {run_id}")
        elif not action_handled_successfully:
            logging_utility.info(f"[ActionHandler] Polling loop finished for run {run_id} without handling an action.")
        else:
            logging_utility.info(f"[ActionHandler] Action handling thread finished successfully for run {run_id}.")

    threading.Thread(target=_monitor, daemon=True).start()


# --- Cleanup Function ---
def cleanup_run_status(run_id):
    global _run_status_registry, _run_status_lock
    with _run_status_lock:
        if run_id in _run_status_registry:
            del _run_status_registry[run_id]
            logging_utility.info(f"Cleaned up run status registry for run_id: {run_id}")

# --- Main Route ---
@bp_llama.route('/api/messages/process', methods=['POST'])
@jwt_required()
def process_messages():
    global _run_status_registry, _run_status_lock # Needed to add run_id to registry
    logging_utility.info("Request received: %s", request.json)
    run_id = None # Keep track for registry and cleanup
    stream_completed_successfully = False # Track if stream finishes ok

    try:
        data = request.json

        messages = data.get('messages', [])
        user_id = data.get('userId') or data.get('user_id')
        thread_id = data.get('threadId') or data.get('thread_id')
        assistant_id = "default"
        selected_model = data.get('model', 'llama3.1')
        provider = data.get('provider', "Hyperbolic")

        if not thread_id: raise ValueError("Missing 'threadId'")
        if not messages: raise ValueError("Invalid 'messages'")
        user_message_content = messages[-1].get('content', '').strip()
        if not user_message_content: raise ValueError("Last message content empty")

        # Step 1: Create message and run
        message = client.messages.create_message(
            thread_id=thread_id, assistant_id=assistant_id,
            content=user_message_content, role='user'
        )
        run = client.runs.create_run(thread_id=thread_id, assistant_id=assistant_id)
        run_id = run.id # Assign run_id here
        logging_utility.info(f"Created message {message.id} and run {run_id} for thread {thread_id}")

        # *** REGISTER THE RUN ***
        with _run_status_lock:
            _run_status_registry[run_id] = {"tool_handled": False, "start_time": time.time()}
        logging_utility.info(f"Registered run {run_id} in status registry.")

        # Step 2: Start polling in background
        poll_and_handle_pending_actions(run_id, thread_id, assistant_id)

        # Step 3: Setup sync stream
        # ... (keep existing setup logic) ...
        if not hasattr(client, 'synchronous_inference_stream'):
             raise AttributeError("Client object missing 'synchronous_inference_stream'")
        sync_stream = client.synchronous_inference_stream
        sync_stream.setup(
            user_id=user_id, thread_id=thread_id, assistant_id=assistant_id,
            message_id=message.id, run_id=run_id,
            api_key=os.getenv("HYPERBOLIC_API_KEY"),
        )
        logging_utility.info(f"Sync stream setup complete for run {run_id}")

        # Step 4: Define the generator
        def generate_chunks():
            nonlocal stream_completed_successfully # Allow modifying the flag
            tool_was_handled = False # Local check within generate_chunks scope
            logging_utility.info(f"Starting chunk generation for run {run_id}")

            try:
                for chunk in sync_stream.stream_chunks(
                    provider=provider, model=selected_model,
                    api_key=os.environ.get('HYPERBOLIC_API_KEY') # Often passed in setup
                ):
                    logging_utility.debug(f"Streaming chunk for run {run_id}: {chunk}")
                    try:
                        yield json.dumps(chunk) + "\n"
                    except TypeError as te:
                        logging_utility.error(f"Chunk not JSON serializable: {chunk} - Error: {te}")
                        yield json.dumps({'type': 'error', 'error': 'Received non-serializable chunk', 'chunk_repr': repr(chunk)}) + "\n"

                # *** STREAM COMPLETED SUCCESSFULLY ***
                stream_completed_successfully = True # Mark success
                logging_utility.info(f"Inference stream loop finished successfully for run {run_id}")

                # Check the shared registry flag AFTER loop finishes
                with _run_status_lock:
                    tool_was_handled = _run_status_registry.get(run_id, {}).get('tool_handled', False)

                # Yield completion status AND tool metadata if applicable
                completion_data = {"type": "status", "status": "inference_complete", "run_id": run_id}
                if tool_was_handled:
                    completion_data["tool_handled"] = True
                    logging_utility.info(f"Including tool_handled=True metadata for run {run_id}")

                yield json.dumps(completion_data) + "\n"

            except Exception as e:
                logging_utility.error(f"Error during stream chunk generation for run {run_id}: {repr(e)}", exc_info=True)
                yield json.dumps({'type': 'error', 'error': str(e), "run_id": run_id}) + "\n"
                # Stream did not complete successfully
                stream_completed_successfully = False # Ensure flag is false on error exit
            finally:
                # Close stream resources regardless of success inside the loop
                try:
                    if hasattr(sync_stream, 'close') and callable(sync_stream.close):
                        sync_stream.close()
                        logging_utility.info(f"Sync stream closed for run {run_id}")
                except Exception as e:
                    logging_utility.error(f"Error closing sync stream for run {run_id}: {repr(e)}")


        # Step 5: Return the streaming response
        logging_utility.info(f"Returning streaming response for run {run_id}")
        # Use stream_with_context to ensure cleanup happens even if client disconnects
        response = Response(
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

        # Register cleanup function to run after the request context ends
        @response.call_on_close
        def on_close():
             cleanup_run_status(run_id)

        return response

    # --- Error Handling & Cleanup ---
    except ValueError as ve:
        logging_utility.warning(f"Validation error in /process: {str(ve)}")
        if run_id: cleanup_run_status(run_id) # Cleanup if run was created
        return jsonify({'error': str(ve)}), 400
    except AttributeError as ae:
        logging_utility.error(f"Config/client error in /process: {str(ae)}", exc_info=True)
        if run_id: cleanup_run_status(run_id)
        return jsonify({'error': 'Internal configuration error'}), 500
    except Exception as e:
        logging_utility.error(f"Unexpected error in /process [RunID {run_id}]: {repr(e)}", exc_info=True)
        if run_id: cleanup_run_status(run_id) # Crucial: Ensure cleanup on unexpected error
        return jsonify({'error': 'An unexpected internal server error occurred'}), 500