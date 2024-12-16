import argparse
import json
import re
from datetime import datetime
from DB.panelpal_db import Session, Patient, BedFile, PanelInfo
from PanelPal.settings import get_logger


logger = get_logger(__name__)


def patient_info_prompt():
    """
    Prompts the user to optionally provide patient information to be added to the database.
    If user chooses to proceed, patient information is collected and returned as a dictionary.
    Otherwise it returns None and no data will be requested. 

    Returns
    -------
    dict or None
        A dictionary containing patient information if the user agrees, 
        otherwise None.
    """

    # Prompt the user to decide whether to record patient information
    store_info = input(
        "Add patient to database? (Default = 'yes', type 'n' to skip): "
    ).strip().lower()  # this would make a capital N lowercase

    # If the user opts out, return None
    if store_info == 'n':
        return None

    # Validation functions for the user input (ensures inputs are correctly formatted)
    def validate_nhs_number(nhs_number):
        """Validates the NHS number to ensure it is a 10-digit numeric string."""
        return nhs_number.isdigit() and len(nhs_number) == 10

    def validate_name(name):
        """Validates that the name is non-empty and contains only letters and spaces."""
        return bool(re.match(r"^[a-zA-Z\s]+$", name))

    def validate_dob(dob):
        """Validates the date of birth format (DD-MM-YYYY)."""
        try:
            return datetime.strptime(dob, "%d-%m-%Y").date()
        except ValueError:
            return None

    # Collect and validate patient information
    while True:
        patient_id = input("Patient ID (NHS number, 10 digits): ").strip()
        if validate_nhs_number(patient_id):
            break
        print("Invalid NHS number. It must be a 10-digit numeric string.")

    while True:
        patient_name = input("Patient name: ").strip()
        if validate_name(patient_name):
            break
        print("Invalid name. It must contain only letters and spaces.")

    while True:
        dob = input("Patient's date of birth (DD-MM-YYYY): ").strip()
        dob_valid = validate_dob(dob)
        if dob_valid:
            break
        print("Invalid date format. Please use DD-MM-YYYY.")

    return {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "dob": dob_valid
    }


def add_patient_to_db(patient_info):
    """
    Inserts the patient information given in patient_info_prompt() into the database.
    Accepts a dictionary (gathered by patient_info_prompt) described below. 

    Parameters
    ----------
    patient_info : dict
        Dictionary containing patient information with keys:
        - "patient_id": str
        - "patient_name": str
        - "dob": datetime.date
    """
    # open a new session
    session = Session()
    try:
        # Insert patient info into the patients table
        new_patient = Patient(
            nhs_number=patient_info["patient_id"],
            patient_name=patient_info["patient_name"],
            dob=patient_info["dob"]
        )
        session.add(new_patient)
        # commit the patient info to the DB
        session.commit()

        logger.info(
            f"Patient {patient_info['patient_name']} added to database.")
    except Exception as e:
        logger.error(f"Failed to add patient data: {e}")
        # roll back any changes if there's been an error
        session.rollback()
    finally:
        # close the session after info has been added
        session.close()


def bed_file_info_prompt(
        patient_id, panel_name, panel_version, genome_build=None):

    while True:
        # ask for user input on analysis date
        analysis_date = input("Enter analysis date (DD-MM-YYYY):").strip()
        try:
            # Validate date format
            analysis_date = datetime.strptime(analysis_date, "%d-%m-%Y").date()
            break
        except ValueError:
            print("Invalid date format. Please use DD-MM-YYYY.")

    # Store names of bed & merged bed file so user can locate them
    bed_file_name = f"{panel_name}_v{panel_version}_{genome_build}.bed"

    merged_bed_file_name = (
        f"{panel_name}_v{panel_version}_{genome_build}_merged.bed")

    return {
        "patient_id": patient_id,
        "analysis_date": analysis_date,
        "bed_file": bed_file_name,
        "merged_bed_file": merged_bed_file_name
    }


def add_bed_file_to_db(bed_file_info):
    """
    Inserts the bed file information into the database.

    Parameters
    ----------
    bed_file_info : dict
        Dictionary containing bed file information with keys:
        - "patient_id": str
        - "analysis_date": datetime.date
        - "bed_file_path": str
        - "merged_bed_path": str
    """
    session = Session()
    try:
        # Insert bed file info into the bed_files table
        new_bed_file = BedFile(
            analysis_date=bed_file_info["analysis_date"],
            bed_file_path=bed_file_info["bed_file"],
            merged_bed_path=bed_file_info["merged_bed_file"],
            patient_id=bed_file_info["patient_id"]
        )
        session.add(new_bed_file)
        session.commit()

        logger.info(f"Bed file for patient {
                    bed_file_info['patient_id']} added to database.")

    except Exception as e:
        logger.error(f"Failed to add bed file data: {e}")
        session.rollback()
    finally:
        session.close()


def add_panel_data_to_db(panel_data_info):
    """
    Inserts the panel data information into the database.

    Parameters
    ----------
    panel_data_info : dict
        Dictionary containing panel data information with keys:
        - "bed_file_id": int
        - "panel_data": dict (JSON)
    """
    session = Session()
    try:
        # Insert panel data into the panel_info table
        new_panel_info = PanelInfo(
            bed_file_id=panel_data_info["bed_file_id"],
            panel_data=panel_data_info["panel_data"]
        )
        session.add(new_panel_info)
        session.commit()

        logger.info(f"Panel data added to database for bed_file_id {
                    panel_data_info['bed_file_id']}.")
    except Exception as e:
        logger.error(f"Failed to add panel data: {e}")
        session.rollback()
    finally:
        session.close()
