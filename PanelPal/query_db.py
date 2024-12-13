"""
Query DB
A suite of commands to quickly query the DB without needing SQL commands.

"""

from PanelPal.settings import get_logger
from DB.panelpal_db import Session, Patient, BedFile, PanelInfo
from DB.create_db import create_database
from sqlalchemy.exc import OperationalError
from datetime import datetime

logger = get_logger(__name__)

#### ACCESSORY FUNCTIONS ####

def setup_db(force=False):
    """
    Ensures the database is set up. If not, it calls create_database from DB.create_db.
    """
    try:
        # Create a session only when needed (on explicit call)
        with Session() as session:
            session.query(Patient).first()  # Attempt a simple query
            logger.info("Database is already set up.")
    except OperationalError:
        logger.error("Database not found or connection failed.")
        if force:
            logger.info("Force setup is enabled. Creating database.")
            create_database()
        else:
            logger.info("Please set up the database first using 'setup-db'.")

def query_patient(patient_name):
    """
    Fetches and displays conjoined data from all three tables 
    (patients, bed_files, panel_info) based on the patient's name.

    Parameters
    ----------
    patient_name : str
        The name of the patient to search for.
    """
    # Ensure the patient_name is a single string
    if isinstance(patient_name, list):
        patient_name = " ".join(patient_name)
    
    # Automatically wrap the name in quotes if not already done
    patient_name = patient_name.strip('"')

    try:
        # Create session
        with Session() as session:
            # Query database to get the 3 tables
            results = session.query(Patient, BedFile, PanelInfo).join(
                BedFile, BedFile.patient_id == Patient.nhs_number).join(
                PanelInfo, PanelInfo.bed_file_id == BedFile.id).filter(
                    Patient.patient_name == patient_name).all()

            # Check if patient was found, return None if no patient record exists
            if not results:
                logger.info(f"No patient found with the name: {patient_name}")
                return None

            # Format and display the results
            for patient, bed_file, panel_info in results:
                print(f"Patient Name: {patient.patient_name}")
                print(f"Patient ID: {patient.nhs_number}")
                print(f"Date of Birth: {patient.dob}")
                print(f"Analysis Date: {bed_file.analysis_date}")
                print(f"BED File Path: {bed_file.bed_file_path}")
                print(f"Panel Data: {panel_info.panel_data}")
                print("-" * 40)

    except Exception as e:
        logger.error(f"Failed to retrieve patient information for {patient_name}: {e}")


#### MAIN (to be imported into main.py) ####

def main():
    """
    interacting with DB
    
    Parameters
    ----------
    
    Raises
    ------

    Exits
    -----

    Notes
    -----

    Examples
    --------
    """

def argument_parser():
    pass