import json
import os

from openai import OpenAI

from backend.app import create_app
from backend.app.services.common.context_extractor import ContextExtractor
from backend.app.services.common.prompt_service import PromptService

gpt3_turbo_service_drone_id = os.getenv("OPENAI_ASSISTANT_GPT3_TURBO_SERVICE_DRONE")

openai_api_key = os.getenv("OPENAI_API_KEY")
if not gpt3_turbo_service_drone_id:
    raise ValueError("OpenAI API key, GPT-4 Turbo Assistant ID, or GPT-3 Turbo Assistant ID is not defined. Please check your environment variables.")


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "<your OpenAI API key if not set as env var>"))


def show_json(obj):
    # Convert the object to a JSON string
    json_str = json.dumps(obj, indent=4)
    # Print the JSON string
    #print(json_str)


class SummaryUpdaterService:
    def __init__(self):
        self.db_service = SessionDatabaseService()
        self.context_extractor = ContextExtractor()

    def generate_summary_with_service_drone(self, message_content):

        summary = ""

        thread = client.beta.threads.create()
        thread_id = thread.id
        instruction_service = InstructionService()
        instructed = instruction_service.get_drone_instructions()
        prompt_service = PromptService()

        prompted = prompt_service.drone_prompt_sumarise_message(data=message_content)

        message_id = create_message_without_file_attached(thread.id, prompted)

        run = create_run(thread.id, gpt3_turbo_service_drone_id, instructed)
        inner_thread_id = thread_id
        return inner_thread_id

    def get_service_drone_response(self, inner_thread_id, outer_thread_id):

        sync_cursor = client.beta.threads.messages.list(thread_id=inner_thread_id)
        messages_dict = sync_cursor.dict()

        message_service = message_service = MessageParsingService()
        response = message_service.process_messages_by_thread(messages_dict)

        response = response[inner_thread_id][0]
        text_value = response['text_value']
        summary = text_value

        self.db_service.update_session_summary(outer_thread_id, summary)

    def process_thread_with_drone(self, thread_id, user_id):
        app = create_app()
        with app.app_context():
            session = self.db_service.fetch_session_by_thread_id_and_user(thread_id, user_id)
            if session:
                messages = session.get_messages()
                if messages:
                    most_recent_message = messages[-1]  # Assuming the last message is the most recent

                    # Extract the message content from the nested structure
                    message_content = ""
                    if 'content' in most_recent_message:
                        content = most_recent_message['content']
                        for item in content:
                            if 'text' in item and 'value' in item['text']:
                                message_content += item['text']['value'] + " "
                    message_content = message_content.strip()  # Remove leading/trailing whitespace

                    return message_content

    def generate_summary(self, entities, pos_tags, dependency_parse, keywords):
        # Create a summary based on the extracted information
        summary = ""

        # Include the extracted entities in the summary
        if entities:
            entity_summary = ", ".join([f"{entity[0]} ({entity[1]})" for entity in entities])
            summary += f"Entities: {entity_summary}\n"

        # Include the extracted keywords in the summary
        if keywords:
            keyword_summary = ", ".join(keywords)
            summary += f"Keywords: {keyword_summary}\n"

        # Include a selection of POS tags in the summary
        if pos_tags:
            selected_pos_tags = [pos_tag[1] for pos_tag in pos_tags if pos_tag[1] in ["NOUN", "VERB", "ADJ"]]
            if selected_pos_tags:
                pos_tag_summary = ", ".join(selected_pos_tags)
                summary += f"POS Tags: {pos_tag_summary}\n"

        # Include a simplified representation of the dependency parse in the summary
        if dependency_parse:
            simplified_parse = [f"{token[0]} ({token[1]})" for token in dependency_parse]
            dependency_parse_summary = " ".join(simplified_parse)
            summary += f"Dependency Parse: {dependency_parse_summary}\n"

        # Truncate the summary to a maximum length of 255 characters
        summary = summary.strip()[:255]
        return summary

    def process_thread(self, thread_id, user_id):

        app = create_app()
        with app.app_context():
            session = self.db_service.fetch_session_by_thread_id_and_user(thread_id, user_id)
            if session:
                messages = session.get_messages()
                if messages:

                    most_recent_message = messages[-1]  # Assuming the last message is the most recent

                    # Extract the message content from the nested structure
                    message_content = ""
                    if 'content' in most_recent_message:
                        content = most_recent_message['content']
                        for item in content:
                            if 'text' in item and 'value' in item['text']:
                                message_content += item['text']['value'] + " "
                    message_content = message_content.strip()  # Remove leading/trailing whitespace

                    # Extract relevant information from the most recent message
                    entities = self.context_extractor.extract_entities(message_content)
                    pos_tags = self.context_extractor.tag_parts_of_speech(message_content)
                    dependency_parse = self.context_extractor.parse_dependency(message_content)
                    extracted_keywords = self.context_extractor.extract_keywords(message_content)

                    # Generate a human-readable summary from the extracted information
                    summary = self.generate_summary(entities, pos_tags, dependency_parse, extracted_keywords)

                    # Update the session summary in the database
                    self.db_service.update_session_summary(thread_id, summary)

                    print(f"Processed thread ID: {thread_id}")
                    print(f"Summary: {summary}")
                    print("---")

                else:
                    print(f"No messages found for thread ID: {thread_id}")
            else:
                print(f"No session found for thread ID: {thread_id} and user ID: {user_id}")


if __name__ == "__main__":
    # Example usage
    thread_id = "specific_thread_id"  # Replace with the actual thread ID you want to update
    user_id = "c8475de4-e267-4ef7-bf76-f51138721727"  # Replace with the actual user ID
    summary_updater_service = SummaryUpdaterService()
    summary_updater_service.process_thread(thread_id, user_id)