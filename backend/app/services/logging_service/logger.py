import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Load environment variables
gpt4_turbo_sentinel_drone_id = os.getenv("OPENAI_ASSISTANT_GPT4_TURBO_SENTINEL_DRONE")
openai_api_key = os.getenv("OPENAI_API_KEY")
TECH_SUPPORT = os.getenv("TECH_SUPPORT")


def show_json(obj):
    """Print JSON representation of an object safely."""
    try:
        json_str = json.dumps(obj, indent=4)
    except Exception:
        json_str = json.dumps({"repr": repr(obj), "type": type(obj).__name__}, indent=4)
    # Best-effort write to a robust stream without raising
    stream = getattr(sys, "__stderr__", None) or sys.stderr
    try:
        stream.write(json_str + "\n")
        stream.flush()
    except Exception:
        pass


class LoggingUtility:
    _instance = None

    def __new__(cls, app=None, enable_file_logging=False):
        if cls._instance is None:
            cls._instance = super(LoggingUtility, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, app=None, enable_file_logging=False):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self.app = app
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # capture all

        # Remove all existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Formatter
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Console handler
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)

        # File handler (optional)
        self.file_handler = None
        self.enable_file_logging = enable_file_logging
        self._setup_file_handler()

        # Defaults
        self.handler = self.console_handler
        self.level = logging.INFO

        if app is not None:
            self.init_app(app)

        # Interceptor toggle
        self._interceptors_enabled = os.getenv(
            "DISABLE_LOG_INTERCEPTORS", "0"
        ).lower() not in ("1", "true", "yes")

    # ─────────────────────────────────────────────────────────────
    # Handlers
    # ─────────────────────────────────────────────────────────────
    def _setup_file_handler(self):
        """Set up the file handler if file logging is enabled."""
        if self.enable_file_logging:
            log_dir = os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "..", "logs"
            )
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "app.log")
            self.file_handler = RotatingFileHandler(
                log_file, maxBytes=10 * 1024 * 1024, backupCount=5, delay=True
            )
            self.file_handler.setLevel(logging.INFO)
            self.file_handler.setFormatter(self.formatter)
            if self.file_handler not in self.logger.handlers:
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

    # ─────────────────────────────────────────────────────────────
    # Public logging API
    # ─────────────────────────────────────────────────────────────
    def debug(self, message, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)
        # Never let interceptors crash the app
        try:
            if self._interceptors_enabled:
                self.intercept_error_log(message, *args, **kwargs)
        except Exception:
            pass

    def critical(self, message, *args, **kwargs):
        self.logger.critical(message, *args, **kwargs)
        try:
            if self._interceptors_enabled:
                self.intercept_critical_log(message, *args, **kwargs)
        except Exception:
            pass

    def exception(self, message, *args, **kwargs):
        self.logger.exception(message, *args, **kwargs)

    # ─────────────────────────────────────────────────────────────
    # Interceptors (bulletproof)
    # ─────────────────────────────────────────────────────────────
    def _fmt(self, message, args, kwargs):
        """Defensive printf-style formatting."""
        try:
            return (message % args) if args else str(message)
        except Exception:
            return f"{message} | args={args} kwargs={kwargs}"

    def _safe_write(self, header, text):
        """Write to a robust stream; swallow I/O errors."""
        stream = getattr(sys, "__stderr__", None) or sys.stderr
        try:
            stream.write(header + "\n")
            stream.write(text + "\n")
            stream.flush()
        except Exception:
            # If even stderr is borked (e.g., Windows/IDE pipes), ignore
            pass

    def intercept_error_log(self, message, *args, **kwargs):
        """Custom logic for error logs (e.g., notify admin). Safe on Windows/WSGI."""
        formatted = self._fmt(message, args, kwargs)
        self._safe_write("Intercepted Error Log:", formatted)
        # Hook point: send to external notifier if desired
        # try: notify_admin(formatted) except: pass

    def intercept_critical_log(self, message, *args, **kwargs):
        """Custom logic for critical logs (e.g., activate alert system)."""
        formatted = self._fmt(message, args, kwargs)
        self._safe_write("Intercepted Critical Log:", formatted)


# ─────────────────────────────────────────────────────────────
# Local smoke test
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    error = (
        "ValueError: OpenAI API key, GPT-4 Turbo Assistant ID, or GPT-3 Turbo Assistant ID is not defined. "
        "Please check your environment variables"
    )
    logging_utility = LoggingUtility()

    logging_utility.info("File logging is off by default.")
    logging_utility.toggle_file_logging(enable=True)
    logging_utility.error(error)  # Log an error
    logging_utility.toggle_file_logging(enable=False)
    logging_utility.info("File logging has been disabled.")
