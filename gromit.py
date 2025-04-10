import os
import time

from projectdavid import Entity
from dotenv import load_dotenv

from send_api_key import assistant

# In dev environments the base url will default
# to http://localhost:9000
# In prod encvironments, you need to set it to your FDQN

client = Entity(
      base_url='http://localhost:9000',
      api_key=os.getenv("API_KEY")
)

# user = client.users.create_user(name='test_user2')


user_id = "user_ZAtDMEfZ37wuVnUZYmW08a"



#assistant = client.assistants.create_assistant(name='test_assistant',
#                                               instructions='You are a helpful AI assistant',
#
#                                               )

assistant_id = "id='asst_DCS7zdMWdnLjsChfajuUYW"


# step 1 - Create a thread

# thread = client.threads.create_thread(participant_ids=["user_s1xkwzViWkq0dqUBGri9EU"])


thread_id = "thread_VQFF1noFyeo5d0YT7DZeWc"


# step 2 - Create a message

message = client.messages.create_message(
      thread_id=thread_id,
      role="user",
      content="Hello, assistant!",
      assistant_id=assistant_id
)

# step 3 - Create a run

run = client.runs.create_run(
      assistant_id=assistant_id,
      thread_id=thread_id
)


# Instantiate the syncronous streaming helper

sync_stream = client.synchronous_inference_stream


# step 4 - Set up the stream

sync_stream.setup(
            user_id=user_id,
            thread_id=thread_id,
            assistant_id="default",
            message_id=message.id,
            run_id=run.id,
            api_key=os.getenv("HYPERBOLIC_API_KEY")

        )

# step 5 - Stream the response

# Stream completions synchronously

# The api_key param is optional but needed if you are usign
# a cloud inference providider

import logging
import json

logging.basicConfig(level=logging.INFO)

# Stream completions synchronously
logging.info("Beginning sync stream...")
for chunk in sync_stream.stream_chunks(
    provider="Hyperbolic",
    model="hyperbolic/deepseek-ai/DeepSeek-V3",
    timeout_per_chunk=15.0,
    api_key=os.getenv("HYPERBOLIC_API_KEY"),
):
    logging.info(json.dumps(chunk, indent=2))

logging.info("Stream finished.")