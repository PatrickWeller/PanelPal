import re
from datetime import datetime
from DB.panelpal_db import Session, Patient, BedFile, PanelInfo
from PanelPal.settings import get_logger
from PanelPal.accessories.panel_app_api_functions import (
    get_response,
    get_name_version,
    get_genes
)


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
        patient_id, panel_name, panel_version, genome_build):

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

        logger.info(f"Bed file metadata for patient {
                    bed_file_info['patient_id']} added to database.")

    except Exception as e:
        logger.error(f"Failed to add bed file data: {e}")
        session.rollback()
    finally:
        session.close()


def add_panel_data_to_db(panel_id, bed_file_id):
    """
    Inserts the panel data information into the database.

    Parameters
    ----------
    panel_id : str
        The unique ID of the panel being processed.
    bed_file_id : str
        The file path for the BED file to associate with the panel data.
    """
    session = Session()
    try:
        # check BED file ID exists (i.e. the name of the BED file)
        if not bed_file_id:
            raise ValueError(
                "BED file ID is missing from bed_file_info list.")

        # Fetch panel data from PanelApp API
        panel_response = get_response(panel_id)

        # Extract panel metadata and gene list
        panel_metadata = get_name_version(panel_response)
        gene_list = get_genes(panel_response)

        # Create panel data as a JSON object that can be stored
        panel_data_json = {
            "panel_id": panel_id,
            "panel_name": panel_metadata["name"],
            "panel_version": panel_metadata["version"],
            "panel_pk": panel_metadata["panel_pk"],
            "genes": gene_list,
        }

        # Add the JSON to the PanelInfo table
        # (it is passed as a dict, but will be automatically serialised # into JSON as the DB expects a JSON input.)

        panel_info = PanelInfo(
            bed_file_id=bed_file_id,
            panel_data=panel_data_json,
        )

        session.add(panel_info)
        session.commit()

        logger.info(
            "Panel data successfully added to the database for panel_id=%s", panel_id)

    except Exception as e:
        logger.error(
            "Failed to add panel data to database for panel_id=%s: %s", panel_id, e)
        session.rollback()
        raise
