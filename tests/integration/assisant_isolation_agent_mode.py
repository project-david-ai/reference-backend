import os

from config_orc_fc import config
from dotenv import load_dotenv
from projectdavid import Entity

load_dotenv()

ASSISTANT_ID = config.get("assistant_id")


# ------------------------------------------------------------------
# 1.  With first API key  (owner — should succeed)
# ------------------------------------------------------------------
print("\n--- Test 1: Owner API key ---")
try:
    client = Entity(
        base_url=os.getenv("BASE_URL", "http://localhost:9000"),
        api_key="ea_Y4OIjjbHMluwjT0lcjGSRT-SsFjNt1oxi4YHcNp8vE4",
    )

    update_assistant = client.assistants.update_assistant(
        assistant_id=ASSISTANT_ID,
        agent_mode=False,
        decision_telemetry=False,
        web_access=False,
        deep_research=False,
        engineer=False,
    )

    thread = client.threads.create_thread()
    run = client.runs.create_run(thread_id=thread.id, assistant_id=ASSISTANT_ID)

    print(f"User ID      : {run.user_id}")
    print(f"agent_mode   : {update_assistant.agent_mode}")
    print(f"telemetry    : {update_assistant.decision_telemetry}")
    print(f"web_access   : {update_assistant.web_access}")
    print(f"deep_research: {update_assistant.deep_research}")
    print(f"assistant_id : {update_assistant.id}")
    print(f"engineer     : {update_assistant.engineer}")

except Exception as e:
    print(f"[FAILED] Test 1 raised an unexpected error: {e}")


# ------------------------------------------------------------------
# 2.  With second API key  (non-owner — should be rejected with 403)
# ------------------------------------------------------------------
print("\n--- Test 2: Non-owner API key (expecting 403) ---")
try:
    client = Entity(
        base_url=os.getenv("BASE_URL", "http://localhost:9000"),
        api_key="ea_T1CphyVjo2ahhnWrVsGyYh03tbguKac7gPc4Dz8C66k",
    )

    update_assistant = client.assistants.update_assistant(
        assistant_id=ASSISTANT_ID,
        agent_mode=False,
        decision_telemetry=False,
        web_access=False,
        deep_research=False,
        engineer=False,
    )

    # If we reach here the ownership guard is NOT working — flag it loudly.
    thread = client.threads.create_thread()
    run = client.runs.create_run(thread_id=thread.id, assistant_id=ASSISTANT_ID)

    print(f"User ID      : {run.user_id}")
    print(f"agent_mode   : {update_assistant.agent_mode}")
    print(f"telemetry    : {update_assistant.decision_telemetry}")
    print(f"web_access   : {update_assistant.web_access}")
    print(f"deep_research: {update_assistant.deep_research}")
    print(f"assistant_id : {update_assistant.id}")
    print(f"engineer     : {update_assistant.engineer}")
    print("\n[WARNING] Test 2 succeeded — ownership guard may not be active yet.")

except Exception as e:
    print(f"[EXPECTED] Test 2 was rejected: {e}")
