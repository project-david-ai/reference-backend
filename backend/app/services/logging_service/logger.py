import json
import logging
import os
from logging.handlers import RotatingFileHandler


# Load environment variables
gpt4_turbo_sentinel_drone_id = os.getenv("OPENAI_ASSISTANT_GPT4_TURBO_SENTINEL_DRONE")
openai_api_key = os.getenv("OPENAI_API_KEY")
TECH_SUPPORT = os.getenv("TECH_SUPPORT")


def show_json(obj):
    """Prints JSON representation of an object."""
    json_str = json.dumps(obj, indent=4)
    print(json_str)


class LoggingUtility:
    def __init__(self, app=None, enable_file_logging=False):
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # Set base logging level to capture all messages

        # Set up formatter
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Configure console handler
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)

        # Initialize file handler (but do not add it by default)
        self.file_handler = None
        self.enable_file_logging = enable_file_logging
        self._setup_file_handler()

        # Set the handler attribute (default to console handler)
        self.handler = self.console_handler

        # Set the level attribute
        self.level = logging.INFO

        if app is not None:
            self.init_app(app)

    def _setup_file_handler(self):
        """Set up the file handler if file logging is enabled."""
        if self.enable_file_logging:
            log_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, 'app.log')
            self.file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                delay=True  # Delay file creation until the first write
            )
            self.file_handler.setLevel(logging.INFO)
            self.file_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.file_handler)

    def toggle_file_logging(self, enable=True):
        """Enable or disable logging to a file."""
        if enable:
            if self.file_handler is None:
                self._setup_file_handler()
            if self.file_handler not in self.logger.handlers:
                self.logger.addHandler(self.file_handler)
            self.info("File logging enabled.")
        else:
            if self.file_handler and self.file_handler in self.logger.handlers:
                self.logger.removeHandler(self.file_handler)
            self.info("File logging disabled.")

    def init_app(self, app):
        """Integrate LoggingUtility with Flask app."""
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
        """Custom logic for error logs (e.g., notify admin)."""
        print("Intercepted Error Log:")
        print(message % args)

    def intercept_critical_log(self, message, *args, **kwargs):
        """Custom logic for critical logs (e.g., activate alert system)."""
        print("Intercepted Critical Log:")
        print(message % args)


if __name__ == "__main__":
    error = "ValueError: OpenAI API key, GPT-4 Turbo Assistant ID, or GPT-3 Turbo Assistant ID is not defined. Please check your environment variables"
    logging_utility = LoggingUtility()

    # Log messages without file logging (default)
    logging_utility.info("File logging is off by default.")

    # Enable file logging
    logging_utility.toggle_file_logging(enable=True)
    logging_utility.error(error)  # Log an error

    # Disable file logging again
    logging_utility.toggle_file_logging(enable=False)
    logging_utility.info("File logging has been disabled.")