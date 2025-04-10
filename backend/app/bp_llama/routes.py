import json
import os
import time
# Removed threading import as it's no longer used for polling
from flask import jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required
from projectdavid import Entity # Main SDK entry point
from projectdavid_common import UtilsInterface, ValidationInterface # Common utilities

from . import bp_llama

logging_utility = UtilsInterface.LoggingUtility()
# Initialize the main SDK client instance
# Ensure BASE_URL and API_KEY are correctly set in your environment for this client
try:
    # Ensure your Entity client provides access to sub-clients like .runs, .actions, .messages
    # and synchronous_inference_stream
    client = Entity()
except Exception as e:
    logging_utility.error(f"Failed to initialize ProjectDavid Entity client: {e}", exc_info=True)
    client = None



def faux_tool_handler(tool_name, arguments):
    """Placeholder for the consumer's actual tool execution logic."""
    logging_utility.info(f"[ConsumerApp] Handling tool: {tool_name} with args: {arguments}")
    # Simulate work
    time.sleep(1) # Simulate tool execution time
    if tool_name == 'get_flight_times':
        departure = arguments.get('departure', 'Unknown')
        arrival = arguments.get('arrival', 'Unknown')
        # Simulate calling an internal API or service for the consumer
        result = {
            "status": "success",
            "message": f"Simulated flight time for {departure} to {arrival}: 4 hours 30 minutes.",
            "departure_time": "10:00 AM PST",
            "arrival_time": "06:30 PM EST"
        }
        # The SDK helper expects the executor to return a STRING
        return json.dumps(result)
    else:
        # Handle other tools supported by this consumer application
        result = {
            "status": "success",
            "message": f"Consumer app simulated successful execution of tool '{tool_name}'."
        }
        # The SDK helper expects the executor to return a STRING
        return json.dumps(result)


# --- Main Route ---
@bp_llama.route('/api/messages/process', methods=['POST'])
@jwt_required()
def process_messages():
    # Ensure client was initialized successfully
    if not client:
         logging_utility.error("ProjectDavid client is not initialized. Cannot process request.")
         return jsonify({'error': 'Internal server configuration error (client init failed)'}), 500

    logging_utility.info("Request received: %s", request.json)
    run_id = None # Keep track for logging if needed
    thread_id = None
    assistant_id = None

    try:
        data = request.json
        messages = data.get('messages', [])
        user_id = data.get('userId') or data.get('user_id') # Get user ID if needed
        thread_id = data.get('threadId') or data.get('thread_id')
        # Ensure assistant_id is fetched correctly, not hardcoded if variable
        assistant_id = data.get('assistantId', "default") # Get assistant_id or use default
        selected_model = data.get('model', 'llama3.1') # Get model or use default
        provider = data.get('provider', "Hyperbolic") # Get provider or use default
        # Extract API key if needed by stream setup, get from secure source
        hyperbolic_api_key = os.getenv("HYPERBOLIC_API_KEY")

        # --- Basic Input Validation ---
        if not thread_id: raise ValueError("Missing 'threadId'")
        if not assistant_id: raise ValueError("Missing 'assistantId'") # Validate assistant_id too
        if not messages: raise ValueError("Invalid or missing 'messages'")
        user_message_content = messages[-1].get('content', '').strip()
        if not user_message_content: raise ValueError("Last message content is missing or empty")
        # --- End Validation ---

        # Step 1: Create message and run (using the SDK client)
        logging_utility.info(f"Creating message and run for thread {thread_id}...")
        message = client.messages.create_message(
            thread_id=thread_id, assistant_id=assistant_id,
            content=user_message_content, role='user'
        )
        # Create run, potentially passing model/other params if create_run supports them
        run = client.runs.create_run(thread_id=thread_id, assistant_id=assistant_id)
        run_id = run.id
        logging_utility.info(f"Created message {message.id} and run {run_id} (Status: {run.status})")

        # Step 2: Define the generator using the SDK polling helper
        def generate_chunks():
            action_was_handled = False # Track if the action path was taken via the helper

            logging_utility.info(f"[{run_id}] Starting chunk generation process...")

            # --- A: Initial Streaming ---
            logging_utility.info(f"[{run_id}] Setting up and starting initial stream...")
            sync_stream = None # Define before try block
            try:
                # Ensure the sync stream client is available on the main client
                if not hasattr(client, 'synchronous_inference_stream'):
                    raise AttributeError("Client object missing 'synchronous_inference_stream'")

                sync_stream = client.synchronous_inference_stream
                sync_stream.setup(
                    user_id=user_id,
                    thread_id=thread_id,
                    assistant_id=assistant_id,
                    message_id=message.id, # ID of the user message we created
                    run_id=run_id,
                    api_key=os.getenv("HYPERBOLIC_API_KEY")
                )
                logging_utility.info(f"[{run_id}] Initial sync stream setup complete.")

                # Stream the *initial* response from the LLM
                for chunk in sync_stream.stream_chunks(
                    provider=provider, model=selected_model,
                        api_key=os.getenv("HYPERBOLIC_API_KEY")

                ):
                    logging_utility.debug(f"[{run_id}] Yielding initial chunk: {str(chunk)[:100]}...")
                    try:
                        yield json.dumps(chunk) + "\n"
                    except TypeError as te:
                        logging_utility.error(f"[{run_id}] Initial chunk not JSON serializable: {chunk} - Error: {te}")
                        yield json.dumps({'type': 'error', 'error': 'Received non-serializable initial chunk', 'chunk_repr': repr(chunk)}) + "\n"

                logging_utility.info(f"[{run_id}] Initial inference stream finished.")

            except Exception as e:
                 logging_utility.error(f"[{run_id}] Error during initial stream generation: {repr(e)}", exc_info=True)
                 yield json.dumps({'type': 'error', 'error': f"Initial streaming failed: {str(e)}", "run_id": run_id}) + "\n"
                 return # Stop generation if initial stream fails
            finally:
                 # Always try to close the initial stream instance if it was created
                 if sync_stream and hasattr(sync_stream, 'close') and callable(sync_stream.close):
                      try:
                          sync_stream.close()
                          logging_utility.info(f"[{run_id}] Initial sync stream closed.")
                      except Exception as close_err:
                          logging_utility.error(f"[{run_id}] Error closing initial sync stream: {repr(close_err)}")

            # --- B: Poll, Execute Action, Submit Result (using SDK Helper) ---
            logging_utility.info(f"[{run_id}] Checking for and handling required actions using SDK helper...")
            try:


                # *** CALL THE SDK POLLING AND EXECUTION HELPER ***
                # This is a BLOCKING call within the generator's execution context
                action_was_handled = client.runs.poll_and_execute_action(
                    run_id=run_id,
                    thread_id=thread_id,       # Pass necessary context
                    assistant_id=assistant_id, # Pass necessary context
                    tool_executor=faux_tool_handler, # *** Pass THIS app's handler function ***
                    actions_client=client.actions,     # Pass the ActionsClient instance from the main client
                    messages_client=client.messages,   # Pass the MessagesClient instance from the main client
                    timeout=45.0,                      # Specify timeout
                    interval=1.5                       # Specify interval
                )
                # *** SDK HELPER CALL COMPLETE ***



                if action_was_handled:
                    logging_utility.info(f"[{run_id}] SDK helper successfully handled action.")
                    # Yield status to inform frontend (optional but good UX)
                    yield json.dumps({"type": "status", "status": "tool_execution_complete"}) + "\n"
                else:
                    # This means timeout occurred OR run finished/failed before needing action
                    logging_utility.info(f"[{run_id}] SDK helper reported no action handled (timeout/terminal state/error).")

            except Exception as poll_exec_err:
                 logging_utility.error(f"[{run_id}] Error during SDK poll_and_execute_action: {poll_exec_err}", exc_info=True)
                 yield json.dumps({'type': 'error', 'error': f"Polling/Execution failed: {str(poll_exec_err)}", "run_id": run_id}) + "\n"



            # --- C: Stream Final Response (ONLY if action was handled by helper) ---
            # This part allows streaming the LLM's response *after* the tool result was submitted
            if action_was_handled:
                logging_utility.info(f"[{run_id}] Starting final stream after action handling...")
                yield json.dumps({"type": "status", "status": "generating_final_response"}) + "\n"

                final_stream = None # Define before try
                try:
                    # Re-setup the stream client for the *same run* to get the next response
                    final_stream = client.synchronous_inference_stream # Assume re-usable or get new instance
                    final_stream.setup(
                        user_id=user_id,
                        thread_id=thread_id,
                        assistant_id=assistant_id,
                        message_id='So, what next?', # No new user message ID
                        run_id=run_id,   # Continue the existing run
                        api_key=os.getenv("HYPERBOLIC_API_KEY"),
                    )
                    logging_utility.info(f"[{run_id}] Final sync stream setup complete.")

                    # Stream the final chunks
                    for final_chunk in final_stream.stream_chunks(
                        provider=provider, model=selected_model,
                        api_key=os.getenv("HYPERBOLIC_API_KEY")
                    ):
                        logging_utility.debug(f"[{run_id}] Yielding final chunk: {str(final_chunk)[:100]}...")
                        try:
                            yield json.dumps(final_chunk) + "\n"
                        except TypeError as te:
                             logging_utility.error(f"[{run_id}] Final chunk not JSON serializable: {final_chunk} - Error: {te}")
                             yield json.dumps({'type': 'error', 'error': 'Received non-serializable final chunk', 'chunk_repr': repr(final_chunk)}) + "\n"

                    logging_utility.info(f"[{run_id}] Final stream finished after tool use.")

                except Exception as final_stream_err:
                     logging_utility.error(f"[{run_id}] Error during final stream generation: {repr(final_stream_err)}", exc_info=True)
                     yield json.dumps({'type': 'error', 'error': f"Final streaming failed: {str(final_stream_err)}", "run_id": run_id}) + "\n"
                     # Allow flow to continue to completion signal
                finally:
                     # Close the stream instance used for the final part
                     if final_stream and hasattr(final_stream, 'close') and callable(final_stream.close):
                         try:
                              final_stream.close()
                              logging_utility.info(f"[{run_id}] Final sync stream closed.")
                         except Exception as close_err:
                              logging_utility.error(f"[{run_id}] Error closing final sync stream: {repr(close_err)}")
            # --- End Final Stream ---


            # --- D: Signal Completion ---
            # Send a final status message based on whether an action was handled
            completion_status = "tool_completed" if action_was_handled else "inference_complete"
            logging_utility.info(f"[{run_id}] Yielding final status: {completion_status}")
            yield json.dumps({"type": "status", "status": completion_status, "run_id": run_id}) + "\n"
            logging_utility.info(f"[{run_id}] Generation process fully complete.")

        # --- Main Route Returns Streaming Response ---
        logging_utility.info(f"Returning streaming response object for run {run_id}")
        response = Response(
            stream_with_context(generate_chunks()), # Ensure generate_chunks is called here
            content_type='application/x-ndjson',
            headers={ # Keep necessary headers
                'X-Conversation-Id': run_id,
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*', # Adjust in production
                'Access-Control-Expose-Headers': 'X-Conversation-Id'
            }
        )
        # --- No @response.call_on_close needed for polling state ---
        return response

    # --- Main Route Error Handling (No changes needed here) ---
    except ValueError as ve:
        logging_utility.warning(f"Validation error processing message request: {str(ve)}")
        return jsonify({'error': str(ve)}), 400
    except AttributeError as ae:
         logging_utility.error(f"Configuration or client access error: {str(ae)}", exc_info=True)
         return jsonify({'error': 'Internal configuration error'}), 500
    except Exception as e:
        logging_utility.error(f"Unexpected error in /api/messages/process [RunID maybe {run_id}]: {repr(e)}", exc_info=True)
        return jsonify({'error': 'An unexpected internal server error occurred'}), 500