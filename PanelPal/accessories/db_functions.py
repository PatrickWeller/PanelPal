"""
Query DB
A suite of commands to quickly query the DB without needing SQL commands.

"""

from PanelPal.settings import get_logger
from DB.panelpal_db import Session, Patient, BedFile, PanelInfo
from DB.create_db import create_database
from sqlalchemy.exc import OperationalError
from datetime import datetime

# Initialize logger
logger = get_logger(__name__)


def add_patient(nhs_number, dob, patient_name):
    """
    Adds a new patient to the database.

    Parameters
    ----------
    nhs_number : str
        The NHS number of the patient.
    dob : datetime
        The patient's date of birth.
    patient_name : str
        The name of the patient.
    """
    session = Session()
    try:
        # Create a new Patient instance
        new_patient = Patient(nhs_number=nhs_number,
                              dob=dob, patient_name=patient_name)

        # Add the patient to the session
        session.add(new_patient)

        # Commit the transaction to save it
        session.commit()

        logger.info(f"Patient {patient_name} added to database.")
    except Exception as e:
        logger.error(f"Error adding patient: {e}")
        session.rollback()
    finally:
        session.close()


def fetch_patient_by_nhs_number(nhs_number):
    """
    Fetches a patient's information by NHS number.

    Parameters
    ----------
    nhs_number : str
        The NHS number of the patient.

    Returns
    -------
    Patient or None
        The patient object if found, otherwise None.
    """
    session = Session()
    try:
        patient = session.query(Patient).filter_by(
            nhs_number=nhs_number).first()
        return patient
    except Exception as e:
        logger.error(f"Error fetching patient by NHS number {nhs_number}: {e}")
        return None
    finally:
        session.close()


def add_bed_file(patient_nhs_number, bed_file_path, analysis_date):
    """
    Adds a bed file record for a specific patient.

    Parameters
    ----------
    patient_nhs_number : str
        The NHS number of the patient.
    bed_file_path : str
        The path to the bed file.
    analysis_date : datetime
        The date the analysis was performed.
    """
    session = Session()
    try:
        # Fetch the patient by NHS number
        patient = session.query(Patient).filter_by(
            nhs_number=patient_nhs_number).first()

        if not patient:
            logger.error(f"Patient with NHS number {
                         patient_nhs_number} not found.")
            return

        # Create a new BedFile instance
        new_bed_file = BedFile(
            patient_id=patient_nhs_number,
            bed_file_path=bed_file_path,
            analysis_date=analysis_date
        )

        # Add the bed file to the session
        session.add(new_bed_file)

        # Commit the transaction to save it
        session.commit()

        logger.info(f"Bed file for patient {
                    patient_nhs_number} added to database.")
    except Exception as e:
        logger.error(f"Error adding bed file for patient {
                     patient_nhs_number}: {e}")
        session.rollback()
    finally:
        session.close()

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