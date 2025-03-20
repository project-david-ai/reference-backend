import pprint

from entities import Entities



client = Entities()

user = client.user_service.create_user(name='test_case3')
thread = client.thread_service.create_thread(participant_ids=[user.id])
assistant = client.assistant_service.create_assistant(model='gpt')


message = client.message_service.create_message(
    thread_id=thread.id,
    role='user',
    content='Hello, This is a test',
    assistant_id=assistant.id
)

run = client.run_service.create_run(assistant_id=assistant.id,
                                    thread_id=thread.id,

                                    )


# Example usage
import asyncio
import pprint
from entities import Entities

async def stream_output():
    client = Entities()
    async for chunk in client.inference_service.stream_inference_response(
        provider="Hyperbolic",
        model="hyperbolic/deepseek-ai/DeepSeek-V3",
        thread_id=thread.id,
        message_id=message['id'],
        run_id=run.id,
        assistant_id=assistant.id,
    ):
        pprint.pprint(chunk)
    await client.inference_service.close()

if __name__ == "__main__":
    asyncio.run(stream_output())

