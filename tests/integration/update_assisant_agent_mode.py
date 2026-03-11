import os

from config_orc_fc import config
from dotenv import load_dotenv
from projectdavid import Entity

# ------------------------------------------------------------------
# 0.  With first API key
# ------------------------------------------------------------------
load_dotenv()

client = Entity(
    base_url=os.getenv("BASE_URL", "http://localhost:9000"),
    api_key="ea_Y4OIjjbHMluwjT0lcjGSRT-SsFjNt1oxi4YHcNp8vE4",
)

update_assistant = client.assistants.update_assistant(
    assistant_id=config.get("assistant_id"),
    agent_mode=False,
    decision_telemetry=False,
    web_access=False,
    deep_research=False,
    engineer=False,
)

# -----------------------------------------------------------
# Create thread and run so I can retrieve user details
# ----------------------------------------------------

thread = client.threads.create_thread()
run = client.runs.create_run(
    thread_id=thread.id,
    assistant_id=config.get("assistant_id"),
)


print(f"The user ID is {run.user_id}")


print(update_assistant.agent_mode)
print(update_assistant.decision_telemetry)
print(update_assistant.web_access)
print(update_assistant.deep_research)
print(update_assistant.id)
print(update_assistant.engineer)


# ------------------------------------------------------------------
# 0.  With second API key
# ------------------------------------------------------------------
load_dotenv()

client = Entity(
    base_url=os.getenv("BASE_URL", "http://localhost:9000"),
    api_key="ea_T1CphyVjo2ahhnWrVsGyYh03tbguKac7gPc4Dz8C66k",
)

update_assistant = client.assistants.update_assistant(
    assistant_id=config.get("assistant_id"),
    agent_mode=False,
    decision_telemetry=False,
    web_access=False,
    deep_research=False,
    engineer=False,
)

# -----------------------------------------------------------
# Create thread and run so I can retrieve user details
# ----------------------------------------------------

thread = client.threads.create_thread()
run = client.runs.create_run(
    thread_id=thread.id,
    assistant_id=config.get("assistant_id"),
)


print(f"The user ID is {run.user_id}")
print(update_assistant.agent_mode)
print(update_assistant.decision_telemetry)
print(update_assistant.web_access)
print(update_assistant.deep_research)
print(update_assistant.id)
print(update_assistant.engineer)
