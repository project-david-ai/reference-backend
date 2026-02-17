import json


class MessageService:
    @classmethod
    def get_most_recent_message(cls, data):
        """
        Retrieves the most recent message from a list of messages.

        Args:
            data (list): A list of message dictionaries.

        Returns:
            dict: The most recent message as a dictionary.
        """

        # Convert data to JSON object
        json_data = [json.loads(json.dumps(msg)) for msg in data]

        # Sort messages by created_at timestamp in descending order (newest first)
        sorted_messages = sorted(json_data, key=lambda x: x["created_at"], reverse=True)

        # Get the most recent message
        most_recent_message = sorted_messages[0] if sorted_messages else None

        # Extract user prompt and assistant reply from most recent message
        user_prompt = ""
        assistant_reply = ""

        if most_recent_message:
            user_prompt = most_recent_message["content"]
            if (
                "assistant_id" in most_recent_message
                and most_recent_message["assistant_id"] is not None
            ):
                assistant_reply = (
                    most_recent_message["assistant_id"]
                    + ": "
                    + most_recent_message["content"]
                )

            # Create a dictionary with the extracted information
            result = {
                "user_prompt": user_prompt,
                "assistant_reply": assistant_reply,
                "metadata": {
                    "message_id": most_recent_message["id"],
                    "created_at": most_recent_message["created_at"],
                    "sender_id": most_recent_message["sender_id"],
                    "assistant_id": most_recent_message["assistant_id"],
                },
            }

            # Return the result as a dictionary
            return result

        else:
            return None
