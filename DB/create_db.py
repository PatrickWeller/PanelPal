"""
Triggers the creation of a database. Running the script will
initialise SQLite database and create all three tables
(patients, bed_files and panel_info) if they don't 
already exist. 
"""
from DB.panelpal_db import create_database
from PanelPal.settings import get_logger, log_database_startup

logger = get_logger(__name__)

# Initialise the database and create tables,
# then print and log message confirming it has been set up
create_database()
log_database_startup(logger)
