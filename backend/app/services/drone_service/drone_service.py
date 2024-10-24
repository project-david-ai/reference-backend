import time

from backend.app.services.logging_service.logger import LoggingUtility
import os
from dotenv import load_dotenv
import entities_api
from backend.app.extensions import db
from backend.app import create_app
from backend.app.models import LocalUser
from backend.app.services.message_parsing.message_service import MessageService

load_dotenv()

# Access the loaded variable
service_drone = os.getenv('SERVICE_DONE0')
client = entities_api.OllamaClient()
logging_utility = LoggingUtility()
app = create_app()


class ConversationService:
    def __init__(self, client):
        self.client = client

    def get_admin_user_ids(self):
        try:
            with app.app_context():
                users = LocalUser.query.all()
                admin_user_ids = [user.id for user in users if user.is_admin]
                return admin_user_ids
        except Exception as e:
            logging_utility.error(f"An error occurred while fetching admins' IDs: {str(e)}")
            return []

    def create_maintenance_thread(self, user_id):

        thread = self.client.thread_service.create_thread(participant_ids=user_id)

        return thread

    def list_messages(self, thread_id):
        messages = self.client.message_service.list_messages(thread_id=thread_id)
        return messages

    def parse_message(self, data):
        message_service = MessageService()
        latest_message = message_service.get_most_recent_message(data=data)
        return latest_message

    def create_user_message(self, thread_id, content):
        self.client.message_service.create_message(thread_id=thread_id,
                                                   content=content,
                                                   role='user',
                                                   sender_id=self.get_admin_user_ids()[0])

    def run_conversation(self, thread_id, assistant_id):
        run = self.client.run_service.create_run(thread_id=thread_id,
                                                 assistant_id=assistant_id)
        return run

    def process_chunk(self, thread_id, run_id, assistant_id):
        for chunk in self.client.runner.process_conversation(thread_id=thread_id,
                                                             run_id=run_id,
                                                             assistant_id=assistant_id):
            logging_utility.info(chunk)


conversation_service = ConversationService(client)

if __name__ == "__main__":
    thread_id_to_label = "thread_0Qe5PFQfTZ0AzHkckfVYkJ"
    messages = conversation_service.list_messages(thread_id=thread_id_to_label)
    latest_message = conversation_service.parse_message(data=messages)
    user_message = f"Write the message label for: {latest_message}"
    user_id = conversation_service.get_admin_user_ids()
    # Creates a temp thread for the maintenance run
    thread = conversation_service.create_maintenance_thread(user_id=user_id)
    conversation_service.create_user_message(thread_id=thread.id, content=user_message)
    run = conversation_service.run_conversation(thread_id=thread.id, assistant_id=service_drone)
    conversation_service.process_chunk(thread_id=thread.id, run_id=run['id'], assistant_id=service_drone)