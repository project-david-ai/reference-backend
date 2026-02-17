# backend/app/utils/create_default_assistant.py
import os
import sys

import ollama

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import Assistant, LocalUser
from backend.app.services.logging_service.logger import LoggingUtility

logging_utility = LoggingUtility()
client = ollama.OllamaClient()


def create_default_assistant(user_id):
    try:
        app = create_app()
        with app.app_context():
            assistant_record = Assistant.query.filter_by(user_id=user_id).first()
            if not assistant_record:
                assistant = client.assistant_service.create_assistant(
                    name="Mathy",
                    description="My helpful maths tutor",
                    model="llama3.1",
                    instructions="Be as kind, intelligent, and helpful",
                    tools=[{"type": "code_interpreter"}],
                )
                assistant_id = assistant.id
                logging_utility.info(
                    "Created default assistant: %s with assistant ID: %s",
                    assistant,
                    assistant_id,
                )

                new_assistant_record = Assistant(
                    user_id=user_id, assistant_id=assistant_id
                )
                db.session.add(new_assistant_record)
                db.session.commit()
                return new_assistant_record
            else:
                logging_utility.info(
                    "Default assistant already exists for user ID: %s", user_id
                )
                return assistant_record
    except Exception as e:
        logging_utility.error("Error in create_default_assistant: %s", str(e))
        db.session.rollback()
        raise
