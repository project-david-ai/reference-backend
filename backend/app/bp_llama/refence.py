import json
import threading
import time

from entities_api import (CloudInference, EntitiesEventHandler, LocalInference,
                          OllamaClient)
from flask import Response, jsonify, request, stream_with_context
from flask_jwt_extended import jwt_required

from backend.app.services.llm_routing_services.llm_router_service import \
    LlmRouter
from backend.app.services.logging_service.logger import LoggingUtility

from . import bp_llama

logging_utility = LoggingUtility()
client = OllamaClient()

# Initialize the LlmRouter with the path to the routing configuration file
llm_router = LlmRouter("llm_model_routing_config.json")


def monitor_run_status(run_id: str, run_service):
    """
    Continuously monitor the status of a run and handle specific statuses like 'action_required'.
    """
    while True:
        try:
            run = run_service.retrieve_run(run_id)
            logging_utility.info(f"Run {run_id} status: {run.status}")

            if run.status == "action_required":
                logging_utility.info(
                    f"Action required for run {run_id}. Checking pending actions..."
                )

                # Fetch all pending actions for the run
                pending_actions = []
                pending_action_ids = client.action_service.get_actions_by_status(
                    run_id, status="pending"
                )

                if pending_action_ids:
                    for action_id in pending_action_ids:
                        try:
                            action = client.action_service.get_action(action_id["id"])
                            if action:  # Ensure action is not None
                                pending_actions.append(action)
                        except Exception as e:
                            logging_utility.warning(
                                f"Failed to retrieve action {action_id['id']}: {str(e)}"
                            )

                if pending_actions:
                    logging_utility.info(
                        f"Processing {len(pending_actions)} pending actions for run {run_id}."
                    )
                    handle_action_required(run, pending_actions)
                else:
                    logging_utility.info(
                        f"No valid pending actions found for run {run_id}."
                    )

                break  # Exit loop after handling

            elif run.status in ["completed", "failed", "cancelled"]:
                logging_utility.info(
                    f"Run {run_id} has ended with status: {run.status}"
                )
                break  # Exit loop if the run has ended

            time.sleep(2)  # Adjust polling interval as needed

        except Exception as e:
            logging_utility.error(f"Error monitoring run {run_id}: {str(e)}")
            break


def handle_action_required(run, pending_actions):
    """
    Handle the 'action_required' status for a run by processing pending actions.
    """
    logging_utility.info(f"Handling action required for run {run.id}")

    # Check if there are any pending actions
    if not pending_actions:
        logging_utility.info(f"No pending actions found for run {run.id}")
        return

    for action in pending_actions:
        try:
            # Access action attributes using dot notation
            action_id = action.id
            tool_id = action.tool_id

            function_args = action.function_args
            expires_at = action.expires_at
            status = action.status

            # Log the action details for debugging
            logging_utility.info(
                f"Processing action with ID__gerrtr6t {action_id}: "
                f"function_args={function_args}, expires_at={expires_at}"
            )

            # Example: Update action status to 'in_progress'
            if status == "pending":
                logging_utility.info(f"Action {action_id} marked as in_progress.")
                # Here, you would typically call a method to update the action status in the database
                # Example: client.action_service.update_action_status(action_id, "in_progress")

            # Example: Invoke a tool based on the action's function_args
            if function_args:
                logging_utility.info(
                    f"Invoking tool with function_args: {function_args}"
                )
                # Here, you would typically call a method to invoke the tool
                # Example: tool_result = invoke_tool(function_args)

            if tool_id:
                logging_utility.info(f"Invoking tool with the ID: {tool_id}")
                # Here, you would typically call a method to invoke the tool
                # Example: tool_result = invoke_tool(function_args)

        except Exception as e:
            logging_utility.error(
                f"Error processing action with ID {action_id}: {str(e)}"
            )


@bp_llama.route("/api/messages/process", methods=["POST"])
@jwt_required()
def process_messages():
    """
    Handle incoming message processing requests.
    """
    logging_utility.info(f"Request received: {request.json}")
    logging_utility.info(f"Headers: {request.headers}")

    try:
        data = request.json

        messages = data.get("messages", [])
        user_id = data.get("userId") or data.get("user_id")
        thread_id = data.get("threadId") or data.get("thread_id")
        selected_model = data.get("model", "llama3.1")
        inference_point = data.get("inferencePoint")
        provider = data.get("provider")

        logging_utility.info(
            f"Processing request: user_id={user_id}, thread_id={thread_id}, "
            f"model={selected_model}, inference_point={inference_point}, provider={provider}"
        )

        if not messages or not isinstance(messages, list):
            raise ValueError("Invalid or missing 'messages' in request")

        user_message = messages[0].get("content", "")
        if not user_message:
            raise ValueError("Message content is missing")

        return conversation(
            thread_id=thread_id,
            user_message=user_message,
            user_id=user_id,
            selected_model=selected_model,
            inference_point=inference_point,
            provider=provider,
        )

    except ValueError as ve:
        logging_utility.error(f"Validation error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging_utility.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An error occurred while processing the message"}), 500


def conversation(
    thread_id, user_message, user_id, selected_model, inference_point, provider
):
    """
    Orchestrates the conversation process by managing model execution and streaming responses.
    """
    assistant = "asst_iLlQPlRwRT6sRz9W7bjupX"

    logging_utility.info(
        f"Starting conversation: model={selected_model}, "
        f"inference={inference_point}, provider={provider}"
    )

    # Create message and run
    the_message = client.message_service.create_message(
        thread_id=thread_id,
        assistant_id=assistant,
        content=user_message,
        role="user",
        sender_id=user_id,
    )
    message_id = the_message["id"]

    run = client.run_service.create_run(thread_id=thread_id, assistant_id=assistant)
    run_id = run.id

    # Monitor the run status in a separate thread
    threading.Thread(
        target=monitor_run_status, args=(run_id, client.run_service)
    ).start()

    def generate_chunks():
        try:
            handler = llm_router.resolve_handler(
                inference_point, provider, selected_model
            )
            handler_class, method_name = handler.split(".")
            handler_class = (
                LocalInference if handler_class == "LocalInference" else CloudInference
            )

            logging_utility.info(
                f"Using {handler_class.__name__}.{method_name} for "
                f"[{inference_point}/{provider}/{selected_model}]"
            )

            handler_instance = handler_class()
            retrieval_method = getattr(handler_instance, method_name)
            model_instance = retrieval_method()

            yield f"data: {json.dumps({'run_id': run_id})}\n\n"

            process_args = {
                "thread_id": thread_id,
                "message_id": message_id,
                "run_id": run.id,
                "assistant_id": assistant,
                "model": selected_model,
            }

            if selected_model == "deepseek-reasoner":
                process_args["stream_reasoning"] = True

            for chunk in model_instance.process_conversation(**process_args):
                logging_utility.debug(f"Streaming chunk: {chunk}")
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            logging_utility.error(f"Error during conversation: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate_chunks()),
        content_type="text/event-stream",
        headers={"X-Conversation-Id": run_id},
    )
