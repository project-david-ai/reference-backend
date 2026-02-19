import json
import logging
import os
import queue
import threading
import time

import httpx
from flask import Response, jsonify, request, stream_with_context
from flask_jwt_extended import jwt_required
# --- Event Classes ---
from projectdavid import (CodeExecutionGeneratedFileEvent,
                          CodeExecutionOutputEvent,
                          ComputerExecutionOutputEvent, ContentEvent, Entity,
                          HotCodeEvent, ReasoningEvent, StatusEvent,
                          ToolCallRequestEvent)
from projectdavid.events import ActivityEvent
from projectdavid_common import UtilsInterface

# Assuming this is part of a Blueprint
from . import bp_llama

# Setup Logger
logging_utility = UtilsInterface.LoggingUtility()
log = logging.getLogger(__name__)

# ------------------------------------------------------------------
# 1. Initialize Client & Bind for Recursion
# ------------------------------------------------------------------
try:
    client = Entity(api_key=os.environ.get("ENTITIES_API_KEY"))

    # [CRITICAL] Bind internal clients to enable SDK-managed recursion.
    if client and hasattr(client, "synchronous_inference_stream"):
        client.synchronous_inference_stream.bind_clients(
            client.runs, client.actions, client.messages, client.assistants
        )
except Exception as e:
    logging_utility.error(
        f"Failed to initialize ProjectDavid Entity client: {e}", exc_info=True
    )
    client = None


def faux_tool_handler(tool_name, arguments):
    """Consumer's actual tool execution logic."""
    logging_utility.info(
        f"[ConsumerApp] Handling tool: {tool_name} | Args: {arguments}"
    )

    # Simulate work
    time.sleep(1)

    if tool_name == "get_flight_times":
        departure = arguments.get("departure", "Unknown")
        arrival = arguments.get("arrival", "Unknown")
        return json.dumps(
            {
                "status": "success",
                "info": f"Flight from {departure} to {arrival}",
                "duration": "4h 30m",
                "price": "$450",
            }
        )
    else:
        return json.dumps(
            {
                "status": "success",
                "message": f"Executed tool '{tool_name}' successfully.",
            }
        )


def stream_with_thread_isolation(generator_func, *args, **kwargs):
    """
    Executes a generator function in a separate thread and yields the results
    back to the main Flask thread via a Queue.

    Why: The ProjectDavid SDK uses 'asyncio.run_until_complete' internally.
    If Flask (or a debugger) has already started an event loop on the main thread,
    calling the SDK directly causes a "RuntimeError: This event loop is already running".

    Running the SDK in a fresh thread ensures it has a clean environment with
    no active event loop, allowing it to create its own safely.
    """
    q = queue.Queue()

    def worker():
        try:
            # Run the generator in this isolated thread
            # The SDK will successfully create/use its own loop here.
            for chunk in generator_func(*args, **kwargs):
                q.put(chunk)
            q.put(None)  # Sentinel: Stream finished successfully
        except Exception as e:
            # Pass exceptions back to main thread
            q.put(e)

    # Daemon=True ensures thread dies if main process dies
    t = threading.Thread(target=worker, daemon=True)
    t.start()

    # Consume queue in the main Flask thread
    while True:
        try:
            # Wait for data (blocks the request thread, not the server if threaded)
            # Timeout ensures we don't hang forever if the worker dies silently
            item = q.get(timeout=300)

            if item is None:
                break  # Clean exit

            if isinstance(item, Exception):
                # We can't change the HTTP status code once streaming starts,
                # so we log the error and break the stream with a JSON error block.
                error_msg = str(item)
                log.error(f"Stream worker thread failed: {error_msg}")
                yield json.dumps({"type": "error", "error": error_msg}) + "\n"
                break

            yield item
        except queue.Empty:
            log.warning("Stream timed out waiting for SDK thread.")
            yield json.dumps({"type": "error", "error": "Stream timeout"}) + "\n"
            break


@bp_llama.route("/api/messages/process", methods=["POST"])
@jwt_required()
def process_messages():
    if not client:
        return (
            jsonify(
                {"error": "Internal server configuration error (client init failed)"}
            ),
            500,
        )

    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        # ------------------------------------------------------------------
        # 2. Extract Parameters
        # ------------------------------------------------------------------
        messages = data.get("messages", [])
        # Support various casing conventions
        user_id = data.get("userId") or data.get("user_id")
        thread_id = data.get("threadId") or data.get("thread_id")
        assistant_id = data.get("assistantId", "asst_13HyDgBnZxVwh5XexYu74F")

        selected_model = data.get("model") or "hyperbolic/deepseek-ai/DeepSeek-V3-0324"
        provider = data.get("provider") or "Hyperbolic"
        hyperbolic_api_key = data.get("apiKey") or os.getenv("HYPERBOLIC_API_KEY")

        if not thread_id or not assistant_id or not messages:
            raise ValueError(
                "Missing required fields (threadId, assistantId, or messages)"
            )

        user_message_content = messages[-1].get("content", "").strip()

        # ------------------------------------------------------------------
        # 3. Create Message & Run
        # ------------------------------------------------------------------
        logging_utility.info(f"Creating message for thread {thread_id}...")
        message = client.messages.create_message(
            thread_id=thread_id,
            assistant_id=assistant_id,
            content=user_message_content,
            role="user",
        )

        run = client.runs.create_run(thread_id=thread_id, assistant_id=assistant_id)
        run_id = run.id
        logging_utility.info(f"Created Run: {run_id}")

        # ------------------------------------------------------------------
        # 4. Define the Generator (Unified Single Loop)
        # ------------------------------------------------------------------
        def generate_events_stream():
            sync_stream = client.synchronous_inference_stream

            sync_stream.setup(
                thread_id=thread_id,
                assistant_id=assistant_id,
                message_id=message.id,
                run_id=run_id,
                api_key=hyperbolic_api_key,
            )

            logging_utility.info(f"[{run_id}] Starting unified event stream...")

            try:
                for event in sync_stream.stream_events(
                    provider=provider, model=selected_model
                ):
                    # --- [DEBUG LOGGING] Catch-all for event types ---
                    # We use DEBUG for high-volume events (content) and INFO for structural events
                    event_type = type(event).__name__

                    if event_type not in [
                        "ContentEvent",
                        "HotCodeEvent",
                        "ReasoningEvent",
                    ]:
                        logging_utility.info(
                            f"[{run_id}] ⚡ Event Received: {event_type}"
                        )

                    # A. Standard Content
                    if isinstance(event, ContentEvent):
                        yield json.dumps(
                            {
                                "type": "content",
                                "content": event.content,
                                "run_id": event.run_id,
                            }
                        ) + "\n"

                    # B. Reasoning
                    elif isinstance(event, ReasoningEvent):
                        yield json.dumps(
                            {
                                "type": "reasoning",
                                "content": event.content,
                                "run_id": event.run_id,
                            }
                        ) + "\n"

                    # C. Hot Code
                    elif isinstance(event, HotCodeEvent):
                        yield json.dumps(
                            {
                                "type": "hot_code",
                                "content": event.content,
                                "run_id": event.run_id,
                            }
                        ) + "\n"

                    # D. Code Execution Output
                    elif isinstance(event, CodeExecutionOutputEvent):
                        # Log output to see what the sandbox is saying
                        logging_utility.info(
                            f"[{run_id}] 📟 Sandbox Output: {event.content.strip()[:100]}"
                        )
                        yield json.dumps(
                            {
                                "type": "hot_code_output",
                                "content": event.content,
                                "run_id": event.run_id,
                            }
                        ) + "\n"

                    # E. Computer/Shell Output
                    elif isinstance(event, ComputerExecutionOutputEvent):
                        yield json.dumps(
                            {
                                "type": "computer_output",
                                "content": event.content,
                                "run_id": event.run_id,
                            }
                        ) + "\n"

                    # F. Generated Files
                    elif isinstance(event, CodeExecutionGeneratedFileEvent):
                        logging_utility.info(
                            f"[{run_id}] 📎 FILE GENERATED EVENT DETECTED:\n"
                            f"   - Filename: {event.filename}\n"
                            f"   - File ID: {event.file_id}\n"
                            f"   - URL Present: {bool(event.url)}\n"
                            f"   - URL: {event.url}"
                        )

                        yield json.dumps(
                            {
                                "type": "code_interpreter_file",
                                "filename": event.filename,
                                "file_id": event.file_id,
                                "mime_type": event.mime_type,
                                "url": event.url,
                                "base64": event.base64_data,
                                "run_id": event.run_id,
                            }
                        ) + "\n"

                    # G. TOOL EXECUTION
                    elif isinstance(event, ToolCallRequestEvent):
                        logging_utility.info(
                            f"[{run_id}] 🛠️ Tool Request: {event.tool_name} | Args: {event.args}"
                        )

                        yield json.dumps(
                            {
                                "type": "tool_call_start",
                                "tool": event.tool_name,
                                "args": event.args,
                            }
                        ) + "\n"

                        try:
                            start_time = time.time()
                            success = event.execute(faux_tool_handler)
                            duration = time.time() - start_time

                            if success:
                                logging_utility.info(
                                    f"[{run_id}] ✅ Tool executed successfully in {duration:.2f}s."
                                )
                                yield json.dumps(
                                    {
                                        "type": "status",
                                        "status": "tool_execution_complete",
                                    }
                                ) + "\n"
                            else:
                                logging_utility.error(
                                    f"[{run_id}] ❌ Tool execution returned False."
                                )
                                yield json.dumps(
                                    {
                                        "type": "error",
                                        "error": "Tool execution failed internally",
                                    }
                                ) + "\n"
                        except Exception as exec_err:
                            logging_utility.error(
                                f"[{run_id}] 💥 Exception during tool execute: {exec_err}",
                                exc_info=True,
                            )
                            yield json.dumps(
                                {"type": "error", "error": str(exec_err)}
                            ) + "\n"

                    # -------------------------------------------------------------
                    # H. SCRATCHPAD (New)
                    # -------------------------------------------------------------
                    elif isinstance(event, ScratchpadEvent):
                        logging_utility.info(
                            f"[{run_id}] 📝 Scratchpad Update: {event.operation}"
                        )
                        yield json.dumps(
                            {
                                "type": "scratchpad",
                                "operation": event.operation,
                                "activity": event.activity,
                                "state": event.state,
                                "entry": event.entry,
                                "content": event.content,
                                "run_id": event.run_id,
                            }
                        ) + "\n"

                    # I. Activity
                    elif isinstance(event, ActivityEvent):
                        logging_utility.info(
                            f"[{run_id}] ℹ️ Activity: {event.activity} ({event.state})"
                        )
                        yield json.dumps(
                            {
                                "type": "activity",
                                "activity": event.activity,
                                "tool": event.tool,
                                "state": event.state,
                                "run_id": event.run_id,
                            }
                        ) + "\n"

                    # J. Status
                    elif isinstance(event, StatusEvent):
                        logging_utility.info(
                            f"[{run_id}] 🔄 Status Update: {event.status}"
                        )
                        yield json.dumps(
                            {
                                "type": "status",
                                "status": event.status,
                                "run_id": event.run_id,
                                "tool": getattr(event, "tool", None),
                                "message": getattr(event, "message", None),
                            }
                        ) + "\n"

                # End of Stream
                logging_utility.info(f"[{run_id}] 🏁 Stream complete.")
                yield json.dumps(
                    {"type": "status", "status": "complete", "run_id": run_id}
                ) + "\n"

                if hasattr(sync_stream, "close"):
                    sync_stream.close()

            except Exception as e:
                logging_utility.error(
                    f"[{run_id}] 🔥 Fatal Stream Error: {e}", exc_info=True
                )
                yield json.dumps({"type": "error", "error": str(e)}) + "\n"

        return Response(
            stream_with_context(stream_with_thread_isolation(generate_events_stream)),
            content_type="application/x-ndjson",
            headers={
                "X-Conversation-Id": run_id,
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging_utility.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"error": "An unexpected internal server error occurred"}), 500
