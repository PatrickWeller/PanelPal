import logging
import os
import inspect

# Set up the basic configuration for the logger


# Set this flag to True to enable console logging, False to disable it
ENABLE_CONSOLE_LOGGING = True

# Always log to a file, called app.log
handlers = [logging.FileHandler('app.log')]

# Optionally log to the console if the above is set to True
if ENABLE_CONSOLE_LOGGING:
    handlers.append(logging.StreamHandler())

# Set up the logger configuration
logging.basicConfig(
    # Can toggle between DEBUG, INFO, ERROR etc. during development
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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
    
    >>> logger = get_logger(__name__)
    >>> logger.info("This is the message contents")

    # Output
    2024-11-19 12:00:00,000 - CheckPanel - INFO - This is the message contents
    """
    if not module_name or module_name == "__main__":
        # Determine the name of the script that called this function
        caller_frame = inspect.stack()[1]
        script_path = caller_frame.filename
        module_name = os.path.splitext(os.path.basename(script_path))[0]
    return logging.getLogger(module_name)
