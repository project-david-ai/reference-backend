import os

from config_orc_fc import config
from dotenv import load_dotenv
from projectdavid import Entity

load_dotenv()


print("\n--- Test 3: Creating a new assistant---")
try:
    client = Entity(
        base_url=os.getenv("BASE_URL", "http://localhost:9000"),
        api_key="ea_Y4OIjjbHMluwjT0lcjGSRT-SsFjNt1oxi4YHcNp8vE4",
    )

    # -------------------------------------------
    # create_assistant
    # --------------------------------------------
    assistant = client.assistants.create_assistant(
        name="Test Assistant",
        model="gpt-oss-120b",
        instructions="You are a helpful AI assistant, your name is Nexa.",
        tools=[
            {"type": "code_interpreter"},
            {"type": "computer"},
            {"type": "file_search"},
            {"type": "web_search"},
            {
                "type": "function",
                "function": {
                    "name": "get_flight_times",
                    "description": "Get flight times",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "departure": {"type": "string"},
                            "arrival": {"type": "string"},
                        },
                        "required": ["departure", "arrival"],
                    },
                },
            },
        ],
    )

    print(assistant.id)
    print(assistant.instructions)

    update_assistant = client.assistants.update_assistant(
        assistant_id=assistant.id,
        agent_mode=False,
        decision_telemetry=False,
        web_access=False,
        deep_research=False,
        engineer=False,
    )

    # If we reach here the ownership guard is NOT working — flag it loudly.
    thread = client.threads.create_thread()
    run = client.runs.create_run(thread_id=thread.id, assistant_id=assistant.id)

    print(f"User ID      : {run.user_id}")
    print(f"agent_mode   : {update_assistant.agent_mode}")
    print(f"telemetry    : {update_assistant.decision_telemetry}")
    print(f"web_access   : {update_assistant.web_access}")
    print(f"deep_research: {update_assistant.deep_research}")
    print(f"assistant_id : {update_assistant.id}")
    print(f"engineer     : {update_assistant.engineer}")
    print("\n[WARNING] Test 3 succeeded — ownership working for new assistant.")

except Exception as e:
    print(f"[EXPECTED] Test 3 was rejected: {e}")
