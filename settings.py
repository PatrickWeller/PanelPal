import logging

# Set up the basic configuration for the logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app.log')]  # Only log to the file
)

# Create a logger instance
logger = logging.getLogger(__name__)