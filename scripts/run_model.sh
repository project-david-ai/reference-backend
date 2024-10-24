#!/bin/bash

# This script will execute the command to pull the model in the ollama container
# and restart upon failure

COMMAND="docker exec -it ollama ollama run llama3.1:70b"

while true; do
    echo "Running command: $COMMAND"
    $COMMAND
    if [ $? -eq 0 ]; then
        echo "Command completed successfully."
        break
    else
        echo "Command failed. Restarting..."
        sleep 5  # Wait for 5 seconds before retrying
    fi
done
