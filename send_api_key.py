# Import the public SDK interface.
import os
import pprint

from dotenv import load_dotenv
from projectdavid import Entity

client = Entity()
load_dotenv()

user = client.users.create_user(name="test_user")

thread = client.threads.create_thread(participant_ids=[user.id])

assistant = client.assistants.create_assistant()

message = client.messages.create_message(
    thread_id=thread.id,
    role="user",
    content="Hello, This is a test message.",
    assistant_id=assistant.id,
)

run = client.runs.create_run(
    assistant_id=assistant.id,
    thread_id=thread.id,
)

try:
    completion = client.inference.stream_inference_response(
        provider="Hyperbolic",
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        thread_id=thread.id,
        message_id=message.id,
        run_id=run.id,
        assistant_id=assistant.id,
        api_key=os.getenv("HYPERBOLIC_API_KEY"),
    )
    pprint.pprint(completion)
finally:
    pass
