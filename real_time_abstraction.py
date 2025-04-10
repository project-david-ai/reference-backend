import pprint


from projectdavid import Entity

# Full integration test
if __name__ == "__main__":
    # Step 1: Initialize the Entities client
    entities_client = Entity()

    # Step 2: Explicitly set up the required entities
    user = entities_client.user_service.create_user(name="test_case3")
    thread = entities_client.thread_service.create_thread(participant_ids=[user.id])
    assistant = entities_client.assistant_service.create_assistant(model="gpt")

    message = entities_client.message_service.create_message(
        thread_id=thread.id,
        role="user",
        content="Hello, this is a test!",
        assistant_id=assistant.id
    )

    run = entities_client.run_service.create_run(
        assistant_id=assistant.id,
        thread_id=thread.id,
    )

    # Step 3: Use the synchronous inference stream wrapper
    sync_stream = entities_client.synchronous_inference_stream

    # Step 4: Set up the wrapper with the provided IDs
    sync_stream.setup(
        user_id=user.id,
        thread_id=thread.id,
        assistant_id=assistant.id,
        message_id=message.id,
        run_id=run.id
    )

    # Step 5: Stream and process inference results in real time
    print("Starting real-time streaming output...")
    try:
        for chunk in sync_stream.stream_chunks(provider="Hyperbolic", model="hyperbolic/deepseek-ai/DeepSeek-V3"):
            print("Received chunk:")
            pprint.pprint(chunk)
    finally:
        # Step 6: Clean up resources
        sync_stream.close()
