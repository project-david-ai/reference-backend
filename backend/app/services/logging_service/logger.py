# logging_service/logger.py
import json
import logging
import os
from logging.handlers import RotatingFileHandler


gpt4_turbo_sentinel_drone_id = os.getenv("OPENAI_ASSISTANT_GPT4_TURBO_SENTINEL_DRONE")
openai_api_key = os.getenv("OPENAI_API_KEY")
TECH_SUPPORT = os.getenv("TECH_SUPPORT")


def show_json(obj):
    # Convert the object to a JSON string
    json_str = json.dumps(obj, indent=4)
    # Print the JSON string
    print(json_str)


class LoggingUtility:
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Configure console handler
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)

        # Configure file handler
        log_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app.log')
        self.file_handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=5)
        self.file_handler.setLevel(logging.INFO)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

        # Set the handler attribute
        self.handler = self.console_handler

        # Set the level attribute
        self.level = logging.INFO

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.logger = self.logger

    def debug(self, message, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)
        self.intercept_error_log(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self.logger.critical(message, *args, **kwargs)
        self.intercept_critical_log(message, *args, **kwargs)

    def exception(self, message, *args, **kwargs):
        self.logger.exception(message, *args, **kwargs)

    def intercept_error_log(self, message, *args, **kwargs):
        # Perform actions or send notifications for error logs
        print("Intercepted Error Log:")
        print(message % args)
        # Add your custom logic here

    def intercept_critical_log(self, message, *args, **kwargs):
        # Perform actions or send notifications for critical logs
        print("Intercepted Critical Log:")
        print(message % args)
        #self.activate_sentinel_drone(message % args)


if __name__ == "__main__":
    error = "ValueError: OpenAI API key, GPT-4 Turbo Assistant ID, or GPT-3 Turbo Assistant ID is not defined. Please check your environment variables"
    logging_utility = LoggingUtility()
    #logging_utility.activate_sentinel_drone(the_error=error)