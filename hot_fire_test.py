from entities_api import OllamaClient, ClientAssistantService, LocalInference

client = LocalInference()

client.process_conversation(
    thread_id = thread_id
    message_id = message_id ,
    run_id = run_id,
    assistant_id = assistant_id
)

