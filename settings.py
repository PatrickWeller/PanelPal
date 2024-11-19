import logging

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
    # Create a logger specific to this module
    logger = get_logger(__name__)

    # Use the logger
    logger.info("This is the message contents)

    # Output
    2024-11-19 12:00:00,000 - CheckPanel - INFO - Sending request to Panel App API
    """
    return logging.getLogger(module_name)
