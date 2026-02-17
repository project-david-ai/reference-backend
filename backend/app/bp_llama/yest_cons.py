import entities_api

client = entities_api.OllamaClient()

meta_data = {"tool_call_id": "1236"}


user = client.user_service.create_user(name="test2025")
user_id = user.id

thread = client.thread_service.create_thread(participant_ids=[user_id])


the_message = client.message_service.submit_tool_output(
    thread_id=thread.id,
    assistant_id="asst_YSWGOuJ3yny7qcm6zxAfBl",
    content="Hello world",
    role="tool",
    sender_id=user_id,
    tool_id="123456789",
)


conversation_history = client.message_service.get_formatted_messages(
    thread.id, system_message="Test"
)


print(conversation_history)
