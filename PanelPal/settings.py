"""
Application Settings

This file contains settings and configuration for the application. It is designed to centralize 
important options, such as logging, environment-specific variables, and other global settings.

Sections:
---------
1. Logging Settings:
   - Configures logging to both console and rotating log files.
   - Supports toggling console logging with the `ENABLE_CONSOLE_LOGGING` flag.
   - Rotates logs automatically when `app.log` exceeds 5 MB, keeping up to 5 backups.
"""

import logging
import logging.handlers
import os
import inspect

#############################
# Logging Settings
#############################


# Set this flag to True to enable console logging, False to disable it
ENABLE_CONSOLE_LOGGING = True


# Create a handler for outputting logging to a file
file_handler = logging.handlers.RotatingFileHandler(
    filename='app.log', # app.log will always be the most recent log file
    maxBytes=5 * 1024 * 1024, # 5 MB
    backupCount=5)  # 5 backup log files, from app.log (newest) to app.log.4 (oldest)
# Can toggle the level logged to a file between DEBUG, INFO, WARNING etc. during development
file_handler.setLevel(logging.DEBUG)


# Always log to app.log files
handlers = [file_handler]


# Create a handler for outputting logging to the console
stream_handler = logging.StreamHandler()
# Can toggle the level logged to the console between DEBUG, INFO, WARNING etc. during development
stream_handler.setLevel(logging.INFO)


# Optionally log to the console if the above is set to True
if ENABLE_CONSOLE_LOGGING:
    handlers.append(stream_handler)


# Set up the logger configuration
logging.basicConfig(
    level=logging.DEBUG, # Do not toggle
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S", # custom date format which omits milliseconds
    handlers=handlers
)


def get_logger(module_name):
    """
    Returns a logger configured with the module's name.
    
    This should be called at the top of every script to ensure that
    log messages are associated with the correct module name.

    Parameters
    ----------
    module_name : str
        The name of the module requesting the logger.

    Returns
    -------
    logging.Logger
        A logger instance.

    Usage
    -----
    Create a logger specific to a module
    
    >>> from settings import get_logger
    >>> logger = get_logger(__name__)
    >>> logger.info("This is the message contents")

    # Output
    2024-11-19 12:00:00,000 - CheckPanel - INFO - This is the message contents
    """
    # Determine which script is being executed as the main script
    if not module_name or module_name == "__main__":
        # Retrieve the call stack, and get the frame that called 'get_logger'
        caller_frame = inspect.stack()[1]
        # Extract the file path of the script
        script_path = caller_frame.filename
        # Remove the file extension and path to be left with just the file name
        module_name = os.path.splitext(os.path.basename(script_path))[0]
    # Return a logger instance that will tag logs with the module/script name
    return logging.getLogger(module_name)