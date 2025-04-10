import os
import logging

from dotenv import load_dotenv
from projectdavid import Entity
from projectdavid_common import UtilsInterface

# Load .env variables
load_dotenv()

# Initialize logger
logging_utility = UtilsInterface.LoggingUtility()

# Initialize entity client
client = Entity()
logging_utility.info(f"Entity initialized with base_url: {client.base_url}")

# ✅ Fix: Wrap the function schema in a dict under "function"
tool_definition = {
    "name": "get_flight_times",
    "type": "function",
    "function": {
        "function": {
            "name": "get_flight_times",
            "description": "Get the flight times between two cities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "departure": {
                        "type": "string",
                        "description": "The departure city (airport code)."
                    },
                    "arrival": {
                        "type": "string",
                        "description": "The arrival city (airport code)."
                    }
                },
                "required": ["departure", "arrival"]
            }
        }
    }
}

tool_id = "tool_yPCcO2X1LFK7AatzmBsnbc"

from projectdavid import Entity

client = Entity()


#client.tools.associate_tool_with_assistant(tool_id='tool_yPCcO2X1LFK7AatzmBsnbc',
#                                           assistant_id="default")
#

client.actions.create_action(
    run_id="run_ip6h02CIDzk8gLEaYkIR8P",
    function_args={"departure": "JFK", "arrival": "LAX"},
    tool_name="get_flight_times",
)

pending = client.actions.get_pending_actions(run_id="run_ip6h02CIDzk8gLEaYkIR8P")
print(pending)