Logging Guidelines
Introduction

This document outlines the guidelines for implementing logging in our application. Proper logging is essential for debugging, monitoring, and analyzing the application's behavior. By following these guidelines, we can ensure consistency, maintainability, and security in our logging practices.
Objectives

    Standardize the logging approach across the codebase.
    Provide clear guidance on what to log and at what log levels.
    Ensure sensitive information is not logged inadvertently.
    Enable effective analysis and debugging by logging relevant information.

Guidelines

    Use the LoggingUtility Class Use the LoggingUtility class from the backend.app.services.logging_service.logger module for all logging operations. This class encapsulates the logging functionality and ensures consistent configuration across the application.
    Replace Print Statements Replace all print statements with appropriate logging statements using the LoggingUtility instance (logging_utility).
    Choose Log Levels Appropriately Use the following log levels based on the nature of the information being logged:
        info: For informational messages, such as incoming request data, model selection, and response handling.
        warning: For non-critical issues, such as an invalid model selection.
        error: For exceptions and error situations.
        debug: For detailed debug messages (use sparingly to avoid cluttering the logs).
        critical: For critical errors that may cause the application to fail or crash.
    Avoid Logging Sensitive Information Never log sensitive information such as user passwords, system passwords, API keys, or any other sensitive data. If you need to log sensitive information for debugging purposes, obfuscate or redact the sensitive parts.
    Log Relevant Information for Analysis and Debugging Log information that can be useful for analyzing trends, debugging issues, and understanding the application's behavior. This may include incoming request data, model selection, response handling, exceptions, and other relevant contextual information.
    Use Appropriate Log Message Formatting Use appropriate formatting for log messages to ensure readability and clarity. Provide relevant context and avoid excessive logging of unnecessary data.
    Handle Exceptions Properly In exception handling blocks, log the exception message using the logging_utility.error or logging_utility.exception method, depending on the level of detail required.
    Review and Maintain Logging Practices Regularly review the logging practices and ensure that the logging guidelines are followed consistently throughout the codebase. Remove unnecessary or redundant logging statements to maintain log clarity and performance.

Example Usage

python

from backend.app.services.logging_service.logger import LoggingUtility

# ...

def some_function(param1, param2):
    logging_utility.info("Entering some_function with param1=%s, param2=%s", param1, param2)

    try:
        # Some logic that may raise an exception
        result = perform_operation(param1, param2)
        logging_utility.info("Operation completed successfully. Result: %s", result)
    except Exception as e:
        logging_utility.error("An error occurred during the operation: %s", str(e))

    return result