"""
Triggers the creation of a database. Running the script will
initialise SQLite database and create all three tables
(patients, bed_files and panel_info) if they don't 
already exist. 
"""
from DB.panelpal_db import create_database

# Initialize the database and create necessary tables
create_database()
