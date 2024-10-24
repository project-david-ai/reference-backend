import re


def extract_message_id(message_id_with_prefix):

    if message_id_with_prefix:
        # Match 'thread_' prefix
        if message_id_with_prefix.startswith('thread_'):
            message_id = message_id_with_prefix.replace('thread_', '')
            return message_id

        # Check if the prefix is directly the ID without `Q: (...)`
        if message_id_with_prefix.startswith('msg_'):
            return message_id_with_prefix

        # Match 'Q: (msg_' prefix
        match = re.search(r'Q:\s?\((msg_\w+)\)', message_id_with_prefix)
        if match:
            message_id = match.group(1)  # Already includes 'msg_'
            return message_id
        else:
            print("Invalid message ID format")  # Debug print to confirm path
    else:
        print("No message ID provided")  # Debug print for no input case

    return None
