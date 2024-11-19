import logging

# Set up the basic configuration for the logger


# Set this flag to True to enable console logging, False to disable it
ENABLE_CONSOLE_LOGGING = True

# Always log to a file
handlers = [logging.FileHandler('app.log')]

# Optionally log to the console if the above is set to True
if ENABLE_CONSOLE_LOGGING:
    handlers.append(logging.StreamHandler())

# Set up the logger configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)

# Create a logger instance
logger = logging.getLogger(__name__)