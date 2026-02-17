import json
import logging
import os
import time
from datetime import datetime
from pipes import quote

from flask import Response, jsonify, request, stream_with_context
from flask_jwt_extended import get_jwt_identity, jwt_required
from projectdavid import Entity  # Main SDK entry point
from projectdavid_common import (UtilsInterface,  # Common utilities
                                 ValidationInterface)

from . import bp_common

# ─────────────────────────────────────────────────────────────
# Logger: This will correctly inherit handlers from the root logger
# configured in your main create_app function.
# ─────────────────────────────────────────────────────────────
log = logging.getLogger("projectdavid.api.common")


# ─────────────────────────────────────────────────────────────
# Safe logging wrappers (to prevent telemetry from crashing requests)
# ─────────────────────────────────────────────────────────────
def _log_error_safe(message, *args, **kwargs):
    try:
        log.error(message, *args, **kwargs)
    except Exception:
        try:
            import sys

            print(
                f"[log-fallback] ERROR: {message} | args={args} kwargs={kwargs}",
                file=getattr(sys, "__stderr__", None) or sys.stderr,
                flush=True,
            )
        except Exception:
            pass


def _log_warning_safe(message, *args, **kwargs):
    try:
        log.warning(message, *args, **kwargs)
    except Exception:
        pass


def _log_info_safe(message, *args, **kwargs):
    try:
        log.info(message, *args, **kwargs)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────
def _safe_count(obj):
    """Return a length if we can, otherwise None (handles SDK list-like containers)."""
    for attr in ("data", "items", "messages", "results"):
        seq = getattr(obj, attr, None)
        if isinstance(seq, (list, tuple)):
            return len(seq)
    try:
        return len(obj)  # will work for real sequences
    except Exception:
        try:
            return len(list(obj))  # last resort if it's an iterable
        except Exception:
            return None


def _jsonify_sdk_list(obj):
    """Best-effort conversion of SDK list-like objects to a JSON-serializable structure."""
    if isinstance(obj, (list, tuple)):
        return obj
    for attr in ("data", "items", "messages", "results"):
        seq = getattr(obj, attr, None)
        if isinstance(seq, (list, tuple)):
            return seq
    # Fallback: try to serialize directly; if it fails, return a representation
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return {"repr": repr(obj), "type": type(obj).__name__}


# ─────────────────────────────────────────────────────────────
# SDK Client Initialization
# ─────────────────────────────────────────────────────────────
try:
    client = Entity(api_key=os.environ.get("ENTITIES_API_KEY"))
except Exception as e:
    _log_error_safe(
        "Failed to initialize ProjectDavid Entity client: %s", e, exc_info=True
    )
    client = None


# ─────────────────────────────────────────────────────────────
# Assistant Endpoints
# ─────────────────────────────────────────────────────────────
@bp_common.route("/api/assistant/deep-research", methods=["POST"])
@jwt_required()
def update_deep_research():
    """
    Updates the deep_research state (True/False).
    """
    if not client:
        return jsonify({"error": "Service configuration error"}), 503

    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415

        data = request.get_json()

        # 1. Get State (Fail fast if missing)
        if "deep_research" not in data:
            return jsonify({"error": "Missing 'deep_research' boolean parameter"}), 400

        deep_research_state = data["deep_research"]

        if not isinstance(deep_research_state, bool):
            return jsonify({"error": "'deep_research' must be a boolean"}), 400

        # 2. Handle Assistant ID
        # FIXME: Hardcoded for now per your request.
        # When ready to fix frontend, remove this line and use data.get("assistant_id")
        assistant_id = "asst_13HyDgBnZxVwh5XexYu74F"

        # --- Future proofing: Logic to handle dynamic ID if/when you remove the hardcode ---
        # incoming_id = data.get("assistant_id")
        # if incoming_id:
        #     # If frontend sends a full URL (http://.../DeepSeek-R1), strip it to get the ID
        #     if "/" in incoming_id:
        #         assistant_id = incoming_id.split("/")[-1]
        #     else:
        #         assistant_id = incoming_id
        # ---------------------------------------------------------------------------------

        if not assistant_id:
            return jsonify({"error": "assistant_id is required"}), 400

        _log_info_safe(
            "Updating deep_research to %s for assistant ID: %s",
            deep_research_state,
            assistant_id,
        )

        # 3. Call SDK
        updated_assistant = client.assistants.update_assistant(
            assistant_id=assistant_id,
            deep_research=deep_research_state,
        )

        # 4. Return Response
        # Fix: The error 'AssistantRead has no attribute d' happened here.
        # We must access .deep_research, not .d
        return (
            jsonify(
                {
                    "status": "success",
                    "assistant_id": updated_assistant.id,
                    "deep_research": updated_assistant.deep_research,
                    # Assuming _jsonify_sdk_list handles the Pydantic object serialization
                    "data": _jsonify_sdk_list(updated_assistant),
                }
            ),
            200,
        )

    except Exception as e:
        error_msg = str(e)
        _log_error_safe(
            "Failed to update assistant deep_research state. Error: %s", error_msg
        )

        if "404" in error_msg:
            return (
                jsonify(
                    {
                        "error": f"Assistant not found. ID '{assistant_id}' may be incorrect."
                    }
                ),
                404,
            )

        return jsonify({"error": f"Failed to update assistant: {error_msg}"}), 500


@bp_common.route("/api/assistant/web-access", methods=["POST"])
@jwt_required()
def update_web_access():
    """
    Updates the web_access state (True/False).
    """
    if not client:
        return jsonify({"error": "Service configuration error"}), 503

    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415

        data = request.get_json()

        # 1. Get State (Fail fast if missing)
        if "web_access" not in data:
            return jsonify({"error": "Missing 'web_access' boolean parameter"}), 400

        web_access_state = data["web_access"]

        if not isinstance(web_access_state, bool):
            return jsonify({"error": "'web_access' must be a boolean"}), 400

        # 2. Handle Assistant ID
        # FIXME: Hardcoded for now per your request.
        # When ready to fix frontend, remove this line and use data.get("assistant_id")
        assistant_id = "asst_13HyDgBnZxVwh5XexYu74F"

        # --- Future proofing: Logic to handle dynamic ID if/when you remove the hardcode ---
        # incoming_id = data.get("assistant_id")
        # if incoming_id:
        #     if "/" in incoming_id:
        #         assistant_id = incoming_id.split("/")[-1]
        #     else:
        #         assistant_id = incoming_id
        # ---------------------------------------------------------------------------------

        if not assistant_id:
            return jsonify({"error": "assistant_id is required"}), 400

        _log_info_safe(
            "Updating web_access to %s for assistant ID: %s",
            web_access_state,
            assistant_id,
        )

        # 3. Call SDK
        updated_assistant = client.assistants.update_assistant(
            assistant_id=assistant_id,
            web_access=web_access_state,
        )

        # 4. Return Response
        return (
            jsonify(
                {
                    "status": "success",
                    "assistant_id": updated_assistant.id,
                    "web_access": updated_assistant.web_access,
                    "data": _jsonify_sdk_list(updated_assistant),
                }
            ),
            200,
        )

    except Exception as e:
        error_msg = str(e)
        _log_error_safe(
            "Failed to update assistant web_access state. Error: %s", error_msg
        )

        if "404" in error_msg:
            return (
                jsonify(
                    {
                        "error": f"Assistant not found. ID '{assistant_id}' may be incorrect."
                    }
                ),
                404,
            )

        return jsonify({"error": f"Failed to update assistant: {error_msg}"}), 500


# Thread Endpoints
# ─────────────────────────────────────────────────────────────
@bp_common.route("/api/thread/create", methods=["POST"])
@jwt_required()
def create_thread():
    data = request.json or {}
    userId = data.get("userId")
    if not userId:
        return jsonify({"error": "userId is required"}), 400

    _log_info_safe("Received request to create a thread for user ID: %s", userId)
    try:
        thread = client.threads.create_thread(participant_ids=[userId])
        _log_info_safe(
            "Thread created successfully. Thread ID: %s",
            getattr(thread, "id", "unknown"),
        )
        return jsonify({"thread_id": getattr(thread, "id", None)}), 201
    except Exception as e:
        _log_error_safe(
            "Failed to create thread for user ID: %s. Error: %s", userId, str(e)
        )
        return jsonify({"error": "Failed to create thread"}), 500


@bp_common.route("/api/thread/list", methods=["GET"])
@jwt_required()
def list_threads():
    user_id = request.args.get("userId") or request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    _log_info_safe("Received request to fetch threads for user ID: %s", user_id)
    try:
        threads = client.threads.list_threads(user_id=user_id)
        count = _safe_count(threads)
        if count is not None:
            _log_info_safe("Threads listed successfully. Number of threads: %s", count)
        else:
            _log_info_safe(
                "Threads listed successfully. Type=%s", type(threads).__name__
            )
        return jsonify({"threads": _jsonify_sdk_list(threads)}), 200
    except Exception as e:
        _log_error_safe(
            "Failed to list threads for user ID: %s. Error: %s", user_id, str(e)
        )
        return jsonify({"error": "Failed to list threads"}), 500


@bp_common.route("/api/thread/delete", methods=["POST"])
@jwt_required()
def delete_thread():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415

        data = request.get_json()
        thread_id = data.get("thread_id")
        if not thread_id:
            return jsonify({"error": "thread_id is required"}), 400

        current_user = get_jwt_identity()  # not used yet; keep for future auth checks

        deleted = client.threads.delete_thread(thread_id=thread_id)

        # DELETE is idempotent; return 200 whether it was deleted now or was already gone.
        return (
            jsonify(
                {
                    "status": "deleted" if deleted else "not_found",
                    "thread_id": thread_id,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        _log_error_safe("Thread deletion failed: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────────────────────
# Message Endpoints
# ─────────────────────────────────────────────────────────────
@bp_common.route("/api/message/list", methods=["GET"])
@jwt_required()
def list_messages():
    thread_id = request.args.get("thread_id")
    if not thread_id:
        return jsonify({"error": "Missing 'thread_id' parameter"}), 400
    try:
        messages = client.messages.list_messages(thread_id=thread_id)
        count = _safe_count(messages)
        if count is not None:
            _log_info_safe(
                "Listed messages successfully. Number of messages: %s", count
            )
        else:
            _log_info_safe(
                "Listed messages successfully. Type=%s", type(messages).__name__
            )
        return jsonify({"messages": _jsonify_sdk_list(messages)}), 200
    except Exception as e:
        _log_error_safe(
            "Failed to list messages for thread ID: %s. Error: %s", thread_id, str(e)
        )
        return jsonify({"error": "Failed to list messages"}), 500


# ─────────────────────────────────────────────────────────────
# Run Endpoints
# ─────────────────────────────────────────────────────────────
@bp_common.route("/api/run/cancel", methods=["POST"])
@jwt_required()
def cancel_run():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415

        data = request.get_json()
        run_id = data.get("run_id")
        if not run_id:
            _log_error_safe("Missing 'run_id' in request")
            return jsonify({"error": "Missing 'run_id' parameter"}), 400

        client.runs.cancel_run(run_id=run_id)
        _log_info_safe("Run with ID %s cancelled successfully", run_id)
        return jsonify({"message": f"Run {run_id} cancelled successfully"}), 200

    except Exception as e:
        _log_error_safe(
            "Failed to cancel run with ID %s. Error: %s",
            run_id if "run_id" in locals() else "unknown",
            str(e),
        )
        return jsonify({"error": "Failed to cancel run"}), 500


# ─────────────────────────────────────────────────────────────
# Computer / Sandbox Endpoints
# ─────────────────────────────────────────────────────────────
@bp_common.route("/api/computer/session", methods=["POST"])
@jwt_required()
def create_computer_session():
    """
    Acts as a secure bridge (BFF).
    1. Authenticates the Frontend User via JWT.
    2. Uses the Server-Side SDK (with API Key) to request a WebSocket ticket.
    3. Returns the ticket to the Frontend.
    """
    # 0. Safety Check
    if not client:
        _log_error_safe("ProjectDavid Entity client is not initialized.")
        return jsonify({"error": "Service configuration error"}), 503

    try:
        # 1. Validate Request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415

        data = request.get_json()

        # Accept 'room_id' (or 'thread_id' as a fallback if your frontend uses that convention)
        room_id = data.get("room_id") or data.get("thread_id")

        if not room_id:
            return jsonify({"error": "room_id is required"}), 400

        # 2. Audit Logging
        # We log who is asking for the token
        current_user = get_jwt_identity()
        _log_info_safe(
            "User '%s' requesting computer session ticket for Room: %s",
            current_user,
            room_id,
        )

        # 3. Call SDK (Server-Side)
        # This securely calls the Main API using the ENTITIES_API_KEY environment variable
        # The frontend NEVER sees the API Key, only the resulting temporary ticket.
        session_data = client.computer.create_session(room_id=room_id)

        # 4. Success Response
        # session_data contains: { "ws_url": "...", "token": "...", "room_id": "..." }
        return jsonify(session_data), 200

    except Exception as e:
        _log_error_safe(
            "Failed to create computer session for room %s. Error: %s",
            room_id if "room_id" in locals() else "unknown",
            str(e),
        )
        return jsonify({"error": "Failed to initialize computer session"}), 500
