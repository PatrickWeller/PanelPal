from PanelPal.DB.panelpal_db import Session, Patient, BedFile, GeneList
from PanelPal.settings import get_logger
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


def add_bed_file(patient_nhs_number, bed_file_path):
    """
    Adds a bed file record for a specific patient with the 
    current date automatically stored as the analysis date.

    Parameters
    ----------
    patient_nhs_number : str
        The NHS number of the patient.
    bed_file_path : str
        The path to the bed file.
    """
    session = Session()
    try:
        # Get the current date as the analysis date
        analysis_date = datetime.now().date()

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
                    patient_nhs_number} added to database with analysis date {analysis_date}.")
    except Exception as e:
        logger.error(f"Error adding bed file for patient {
                     patient_nhs_number}: {e}")
        session.rollback()
    finally:
        session.close()
