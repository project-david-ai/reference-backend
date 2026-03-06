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
                          HotCodeEvent, ReasoningEvent, ToolCallRequestEvent,
                          WebStatusEvent)
from projectdavid.events import (CodeStatusEvent, EngineerStatusEvent,
                                 ResearchStatusEvent, ScratchpadEvent,
                                 ToolInterceptEvent)
# --- Utilities ---
from projectdavid.utils.network_device_handler import NetworkDeviceHandler
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

import json
# ------------------------------------------------------------------
# 1.5. Local Tool Execution Environment (Network Handlers & Dispatcher)
# ------------------------------------------------------------------
import os
import time

# ------------------------------------------------------------------
# GNS3 Lab Inventory — hostname → localhost telnet console mapping
# ------------------------------------------------------------------
GNS3_INVENTORY = {
    "R1": {"host": "127.0.0.1", "port": 10000},
    "R2": {"host": "127.0.0.1", "port": 10001},
    "R3": {"host": "127.0.0.1", "port": 10002},
}


def get_secure_device_credentials(hostname: str) -> dict:
    """
    Resolves connection parameters for a given hostname.
    """
    logging_utility.info(f"🔒 [Auth] Resolving credentials for '{hostname}'...")

    # --- GNS3 Lab: resolve hostname to localhost console port ---
    lab_entry = GNS3_INVENTORY.get(hostname.upper())
    if lab_entry:
        logging_utility.info(
            f"🧪 [Auth] GNS3 lab match: {hostname} → {lab_entry['host']}:{lab_entry['port']} (telnet)"
        )
        return {
            "device_type": "cisco_ios_telnet",
            "host": lab_entry["host"],
            "port": lab_entry["port"],
            # 🛑 CRITICAL GNS3 FIX: Console ports don't usually prompt for auth.
            # If your GNS3 routers just drop you into R1> without a login screen,
            # passing a username/password causes Netmiko to time out waiting for "Username:".
            "username": "",
            "password": "",
            # If your router has an 'enable secret cisco' set, keep this:
            "secret": os.environ.get("NET_ADMIN_PASS", "cisco"),
            # --- STABILITY TWEAKS FOR GNS3 EMULATORS ---
            "global_delay_factor": 4,  # Emulators are slow
            "timeout": 60,  # TCP socket timeout
            "session_timeout": 60,  # General operation timeout
            "fast_cli": False,  # Never use fast_cli on an emulator
            "session_log": f"netmiko_{hostname.lower()}_debug.log",  # Prevents file lock crashes
        }
    # --- Production fallback: real IP via SSH ---
    logging_utility.warning(
        f"⚠️ [Auth] '{hostname}' not in GNS3 inventory. Falling back to SSH with env creds."
    )
    net_user = os.environ.get("NET_ADMIN_USER", "admin")
    net_pass = os.environ.get("NET_ADMIN_PASS", "cisco")

    device_type = "cisco_ios"
    if "nexus" in hostname.lower():
        device_type = "cisco_nxos"
    elif "arista" in hostname.lower():
        device_type = "arista_eos"

    return {
        "device_type": device_type,
        "host": hostname,
        "username": net_user,
        "password": net_pass,
        "secret": net_pass,
        "global_delay_factor": 2,
        "timeout": 30,
    }


# Initialize the Curated Network Handler AFTER defining the resolution logic
network_execution_handler = NetworkDeviceHandler(
    credential_provider_callback=get_secure_device_credentials
)


# ------------------------------------------------------------------
# 1.6 Tool Dispatcher
# ------------------------------------------------------------------
def master_tool_dispatcher(tool_name: str, arguments: dict) -> str:
    """
    Routes incoming tool calls from the Junior Engineer (or other models)
    to the appropriate local Python execution logic.
    """
    logging_utility.info(
        f"🛠️ [Dispatcher] Routing tool: {tool_name} | Args: {arguments}"
    )

    try:
        # --- NETWORK ENGINEERING TOOLS ---
        if tool_name == "execute_network_command":

            # 🛡️ AI RESILIENCE FIX:
            # If the Junior accidentally passes a string instead of a list, fix it silently.
            cmds = arguments.get("commands", [])
            if isinstance(cmds, str):
                logging_utility.warning(
                    "🩹 [Auto-Fix] Junior passed a string instead of a list. Wrapping in array."
                )
                arguments["commands"] = [cmds]

            return network_execution_handler("run_network_commands", arguments)

        # --- OTHER TOOLS ---
        elif tool_name == "get_flight_times":
            time.sleep(1)
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

        # --- UNKNOWN TOOLS ---
        else:
            err_msg = (
                f"Tool '{tool_name}' is not registered in the consumer dispatcher."
            )
            logging_utility.error(err_msg)
            return json.dumps({"status": "error", "error": err_msg})

    except Exception as e:
        logging_utility.error(
            f"💥 [Dispatcher] Unhandled error executing {tool_name}: {e}"
        )
        return json.dumps(
            {"status": "error", "error": f"Local execution failed: {str(e)}"}
        )


# ------------------------------------------------------------------
# 1.7 Stream Isolation Helper
# ------------------------------------------------------------------
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
            for chunk in generator_func(*args, **kwargs):
                q.put(chunk)
            q.put(None)  # Sentinel: Stream finished successfully
        except Exception as e:
            q.put(e)

    t = threading.Thread(target=worker, daemon=True)
    t.start()

    while True:
        try:
            item = q.get(timeout=300)

            if item is None:
                break

            if isinstance(item, Exception):
                error_msg = str(item)
                log.error(f"Stream worker thread failed: {error_msg}")
                yield json.dumps({"type": "error", "error": error_msg}) + "\n"
                break

            yield item
        except queue.Empty:
            log.warning("Stream timed out waiting for SDK thread.")
            yield json.dumps({"type": "error", "error": "Stream timeout"}) + "\n"
            break


# ------------------------------------------------------------------
# 2. Main Generation Route
# ------------------------------------------------------------------
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
        # Extract Parameters
        # ------------------------------------------------------------------
        messages = data.get("messages", [])
        user_id = data.get("userId") or data.get("user_id")
        thread_id = data.get("threadId") or data.get("thread_id")
        assistant_id = data.get("assistantId", "asst_yRohmbZfAyflp03AMfdu4B")

        selected_model = data.get("model") or "hyperbolic/deepseek-ai/DeepSeek-V3-0324"
        hyperbolic_api_key = data.get("apiKey") or os.getenv("HYPERBOLIC_API_KEY")

        if not thread_id or not assistant_id or not messages:
            raise ValueError(
                "Missing required fields (threadId, assistantId, or messages)"
            )

        user_message_content = messages[-1].get("content", "").strip()

        # ------------------------------------------------------------------
        # Create Message & Run
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
        # DEBUG FLAG
        # ------------------------------------------------------------------
        DEBUG_STREAM = True

        # ------------------------------------------------------------------
        # EVENT ROUTING REGISTRIES
        # ------------------------------------------------------------------
        WEB_TOOL_NAMES = {
            "perform_web_search",
            "read_web_page",
            "scroll_web_page",
            "search_web_page",
            "web_search",
            "browse",
        }

        DELEGATION_TOOLS = {
            "delegate_research_task",
        }

        # ------------------------------------------------------------------
        # Define the Generator (Unified Single Loop)
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
                for event in sync_stream.stream_events(model=selected_model):
                    event_type = type(event).__name__

                    if event_type not in [
                        "ContentEvent",
                        "HotCodeEvent",
                        "ReasoningEvent",
                    ]:
                        logging_utility.info(
                            f"[{run_id}] ⚡ Event Received: {event_type}"
                        )

                    if DEBUG_STREAM:
                        try:
                            logging_utility.info(
                                f"[{run_id}] 🔬 RAW EVENT: type={event_type} | attrs={vars(event)}"
                            )
                        except Exception:
                            logging_utility.info(
                                f"[{run_id}] 🔬 RAW EVENT: type={event_type} | (no vars)"
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

                    # B2. Code Status
                    elif isinstance(event, CodeStatusEvent):
                        logging_utility.info(
                            f"[{run_id}] 🖥️ CodeStatus: {event.activity!r} | "
                            f"state={event.state} | tool={event.tool}"
                        )
                        yield json.dumps(
                            {
                                "type": "code_status",
                                "activity": event.activity,
                                "state": event.state,
                                "tool": event.tool,
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

                    # G. Tool Execution (Senior / Main Thread)
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

                        if event.tool_name == "execute_network_command":
                            target_host = event.args.get("hostname", "unknown device")
                            yield json.dumps(
                                {
                                    "type": "engineer_status",
                                    "state": "in_progress",
                                    "activity": f"Establishing SSH/Telnet session to {target_host} and executing commands...",
                                    "tool": event.tool_name,
                                    "run_id": run_id,
                                }
                            ) + "\n"

                        try:
                            start_time = time.time()
                            success = event.execute(master_tool_dispatcher)
                            duration = time.time() - start_time

                            if success:
                                logging_utility.info(
                                    f"[{run_id}] ✅ Tool executed successfully in {duration:.2f}s."
                                )

                                is_web_tool = event.tool_name in WEB_TOOL_NAMES
                                is_delegation_tool = event.tool_name in DELEGATION_TOOLS

                                if event.tool_name == "execute_network_command":
                                    yield json.dumps(
                                        {
                                            "type": "engineer_status",
                                            "state": "completed",
                                            "activity": f"Network commands executed successfully in {duration:.2f}s.",
                                            "tool": event.tool_name,
                                            "run_id": run_id,
                                        }
                                    ) + "\n"

                                elif is_web_tool:
                                    yield json.dumps(
                                        {
                                            "type": "web_status",
                                            "run_id": run_id,
                                            "tool": event.tool_name,
                                            "status": "success",
                                            "message": f"'{event.tool_name}' completed in {duration:.2f}s.",
                                        }
                                    ) + "\n"

                                elif not is_delegation_tool:
                                    yield json.dumps(
                                        {
                                            "type": "research_status",
                                            "run_id": run_id,
                                            "tool": event.tool_name,
                                            "state": "completed",
                                            "activity": f"'{event.tool_name}' completed in {duration:.2f}s.",
                                        }
                                    ) + "\n"

                            else:
                                logging_utility.error(
                                    f"[{run_id}] ❌ Tool execution returned False."
                                )
                                yield json.dumps(
                                    {
                                        "type": "error",
                                        "error": f"Tool '{event.tool_name}' execution failed internally",
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

                    # G2. Scratchpad Event
                    elif isinstance(event, ScratchpadEvent):
                        logging_utility.info(
                            f"[{run_id}] 📋 ScratchpadEvent: op={event.operation} | state={event.state} | activity={event.activity}"
                        )
                        yield json.dumps(
                            {
                                "type": "scratchpad_status",
                                "state": event.state,
                                "operation": event.operation,
                                "activity": event.activity,
                                "tool": event.tool,
                                "entry": event.entry or event.content or "",
                                "run_id": getattr(event, "run_id", run_id),
                                "assistant_id": event.assistant_id,
                            }
                        ) + "\n"

                    # H. Research Status
                    elif isinstance(event, ResearchStatusEvent):
                        logging_utility.info(
                            f"[{run_id}] ℹ️ ResearchStatus: {event.activity} | Tool: {event.tool} ({event.state})"
                        )
                        yield json.dumps(
                            {
                                "type": "research_status",
                                "activity": event.activity,
                                "tool": event.tool,
                                "state": event.state,
                                "run_id": event.run_id,
                            }
                        ) + "\n"

                    # I. Web Status
                    elif isinstance(event, WebStatusEvent):
                        yield json.dumps(
                            {
                                "type": "web_status",
                                "status": event.status,
                                "run_id": event.run_id,
                                "tool": event.tool,
                                "message": event.message,
                            }
                        ) + "\n"

                    # J. Engineer Status Event
                    elif isinstance(event, EngineerStatusEvent):
                        logging_utility.info(
                            f"[{run_id}] ⚙️ EngineerStatus: {event.activity} | Tool: {event.tool} ({event.state})"
                        )
                        yield json.dumps(
                            {
                                "type": "engineer_status",
                                "state": event.state,
                                "activity": event.activity,
                                "tool": event.tool,
                                "run_id": getattr(event, "run_id", run_id),
                            }
                        ) + "\n"

                    # K. Tool Intercept Event
                    # Emitted when the delegation handler intercepts a Junior's tool call.
                    # Mirrors section G but uses execute_intercepted, scoped to the worker's thread.
                    elif isinstance(event, ToolInterceptEvent):
                        logging_utility.info(
                            f"[{run_id}] 🔧 ToolIntercept: tool={event.tool_name} | origin={event.origin} | thread={event.thread_id} | args={event.args}"
                        )

                        yield json.dumps(
                            {
                                "type": "tool_call_start",
                                "tool": event.tool_name,
                                "args": event.args,
                                "origin": event.origin,
                                "run_id": run_id,
                            }
                        ) + "\n"

                        if event.tool_name == "execute_network_command":
                            target_host = event.args.get("hostname", "unknown device")
                            yield json.dumps(
                                {
                                    "type": "engineer_status",
                                    "state": "in_progress",
                                    "activity": f"[Junior] Establishing SSH/Telnet session to {target_host}...",
                                    "tool": event.tool_name,
                                    "run_id": run_id,
                                }
                            ) + "\n"

                        try:
                            start_time = time.time()

                            success = event.execute_intercepted(
                                tool_executor=master_tool_dispatcher,
                                runs_client=client.runs,
                                actions_client=client.actions,
                                messages_client=client.messages,
                            )

                            duration = time.time() - start_time

                            if success:
                                logging_utility.info(
                                    f"[{run_id}] ✅ Intercepted tool '{event.tool_name}' executed in {duration:.2f}s."
                                )

                                if event.tool_name == "execute_network_command":
                                    yield json.dumps(
                                        {
                                            "type": "engineer_status",
                                            "state": "completed",
                                            "activity": f"[Junior] Network commands executed successfully in {duration:.2f}s.",
                                            "tool": event.tool_name,
                                            "run_id": run_id,
                                        }
                                    ) + "\n"
                                else:
                                    yield json.dumps(
                                        {
                                            "type": "research_status",
                                            "run_id": run_id,
                                            "tool": event.tool_name,
                                            "state": "completed",
                                            "activity": f"[Junior] '{event.tool_name}' completed in {duration:.2f}s.",
                                        }
                                    ) + "\n"

                            else:
                                logging_utility.error(
                                    f"[{run_id}] ❌ Intercepted tool '{event.tool_name}' returned False."
                                )
                                yield json.dumps(
                                    {
                                        "type": "error",
                                        "error": f"[Junior] Tool '{event.tool_name}' execution failed internally",
                                    }
                                ) + "\n"

                        except Exception as exec_err:
                            logging_utility.error(
                                f"[{run_id}] 💥 Exception during intercepted tool execute: {exec_err}",
                                exc_info=True,
                            )
                            yield json.dumps(
                                {"type": "error", "error": str(exec_err)}
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
