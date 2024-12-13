"""
Generate BED Files from PanelApp Data.

This script retrieves gene panel data from the PanelApp API and extracts 
the list of genes included in the panel It then uses the VariantValidator 
API to obtain exon information for each gene using either GRCh37 or GRCh38
and generates a BED-like file. It then merges overlapping exon regions 
for a simplified BED file output.

Key Features
------------
1. Fetches panel data based on a given panel ID and panel version.
2. Extracts associated genes and exon informaiton
3. Converts exon data into BED file format.
4. Merges overlapping regions in the BED file.

Command-Line Arguments
----------------------
-p, --panel_id : str
    The ID of the panel (e.g., "R207").
-v, --panel_version : str
    The version of the panel (e.g., "4").
-g, --genome_build : str
    The genome build to be used (e.g., "GRCh38").

Example
-------
Run the script from the command line:
>>> python generate_bed.py -p R207 -v 4 -g GRCh38

Logging
-------
Logs are written to `panelpal/logging/panelpal.log`.
settings.py can be modified to also write logs to the stream

Notes
-----
- This script assumes that the user has valid access to PanelApp and VariantValidator APIs.

"""

from DB.panelpal_db import Session, Patient
from PanelPal.settings import get_logger
from PanelPal.accessories import panel_app_api_functions
from PanelPal.accessories import variant_validator_api_functions
import argparse
import sys
import os
import re
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up logger
logger = get_logger(__name__)


def parse_arguments():
    """
    Parses command-line arguments for the script.

     Parameters
    ----------
    panel_id : str
        The ID of the panel (e.g., "R207").
    panel_version : str
        The version of the panel (e.g., "4").
    genome_build : str
         The genome build to be used (e.g., "GRCh38").
    """
    # Set up argument parsing for the command-line interface (CLI)
    parser = argparse.ArgumentParser(
        description="Generate a BED file and perform merge using panel details."
    )

    # Define the panel_id argument
    parser.add_argument(
        "-p",
        "--panel_id",
        type=str,
        required=True,
        help='The ID of the panel, (e.g., "R207").',
    )

    # Define the panel_version argument
    parser.add_argument(
        "-v",
        "--panel_version",
        type=str,
        required=True,
        help='The version of the panel (e.g., "4").',
    )

    # Define the genome_build argument
    parser.add_argument(
        "-g",
        "--genome_build",
        type=str,
        required=True,
        help="The genome build (e.g., GRCh38).",
        choices=["GRCh37", "GRCh38"],
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Log the parsed arguments
    logger.debug(
        "Parsed command-line arguments: panel_id=%s, panel_version=%s, genome_build=%s",
        args.panel_id,
        args.panel_version,
        args.genome_build,
    )

    return args


def patient_info_prompt():
    """
    Prompts the user to optionally add patient information to the database.
    If user chooses to proceed, patient information is collected and returned.

    Returns
    -------
    dict or None
        A dictionary containing patient information if the user agrees, 
        otherwise None.
    """

    # Validation functions for user input
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

    # Prompt the user to decide whether to record patient information
    store_info = input(
        "Add patient to database? (Default = 'yes', press 'n' to skip): "
    ).strip().lower()

    # If the user opts out, return None
    if store_info == 'n':
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
        "dob": dob_valid,
    }


def add_patient_to_db(patient_info, bed_file_info, panel_info_data):
    """
    Inserts the patient information and related bed_file and panel_info into the database.

    Parameters
    ----------
    patient_info : dict
        Dictionary containing patient information with keys:
        - "patient_id": str
        - "patient_name": str
        - "dob": datetime.date
    bed_file_info : dict
        Dictionary containing bed file information with keys:
        - "analysis_date": str
        - "bed_file_path": str
        - "patient_id": str
    panel_info_data : dict
        Dictionary containing panel info data with keys:
        - "bed_file_id": int
        - "panel_data": dict (JSON)
    """
    session = Session()
    try:
        # Insert patient information
        new_patient = Patient(
            nhs_number=patient_info["patient_id"],
            patient_name=patient_info["patient_name"],
            dob=patient_info["dob"]
        )
        session.add(new_patient)
        session.commit()

        # Insert bed file information
        new_bed_file = BedFile(
            analysis_date=bed_file_info["analysis_date"],
            bed_file_path=bed_file_info["bed_file_path"],
            patient_id=bed_file_info["patient_id"]
        )
        session.add(new_bed_file)
        session.commit()

        # Insert panel info data
        new_panel_info = PanelInfo(
            bed_file_id=new_bed_file.id,
            panel_data=panel_info_data["panel_data"]
        )
        session.add(new_panel_info)
        session.commit()

        logger.info(f"Patient and related data for {
                    patient_info['patient_name']} added to database.")
    except Exception as e:
        # Log and rollback in case of errors
        logger.error(f"Failed to add patient and related data: {e}")
        session.rollback()
    finally:
        session.close()


def main(panel_id=None, panel_version=None, genome_build=None):
    """
    Main function that processes the panel data and generates the BED file.

    Parameters
    ----------
    patient_info: dict
        The patient information being added to the database (optional)
    panel_id : str
        The ID of the panel (e.g., "R207").
    panel_version : str
        The version of the panel (e.g., "4").
    genome_build : str
         The genome build to be used (e.g., "GRCh38").

    Raises
    ------
    Exception
        If an error occurs during any part of the BED file generation process.
    """

    # Accesses values from the command line through argument parsing if
    # not passed directly from PanelPal main()
    if panel_id is None or panel_version is None or genome_build is None:
        args = parse_arguments()
        panel_id = args.panel_id
        panel_version = args.panel_version
        genome_build = args.genome_build

    # Log the start of the BED generation process
    logger.info(
        "Command executed: generate-bed --panel_id %s, --panel_version %s "
        "--genome_build %s",
        panel_id,
        panel_version,
        genome_build
    )

    try:
        # Prompt for patient information
        patient_info = patient_info_prompt()
        if patient_info:  # If patient info is provided
            add_patient_to_db(patient_info)

        # Fetch the panel data from PanelApp using the panel_id
        logger.debug("Requesting panel data for panel_id=%s", panel_id)
        panelapp_data = panel_app_api_functions.get_response(panel_id)
        logger.info("Panel data fetched successfully for panel_id=%s", panel_id)

        # Extract the list of genes from the panel data
        logger.debug(
            "Extracting gene list from panel data for panel_id=%s", panel_id)
        gene_list = panel_app_api_functions.get_genes(panelapp_data)
        logger.info(
            "Gene list extracted successfully for panel_id=%s. Total genes found: %d",
            panel_id,
            len(gene_list),
        )

        # Generate the BED file using the gene list, panel ID, panel version, and genome build
        logger.debug(
            "Generating BED file for panel_id=%s, panel_version=%s, genome_build=%s",
            panel_id,
            panel_version,
            genome_build,
        )
        variant_validator_api_functions.generate_bed_file(
            gene_list, panel_id, panel_version, genome_build
        )
        logger.info("BED file generated successfully for panel_id=%s", panel_id)

        # Perform bedtools merge with the provided panel details
        logger.debug(
            "Starting bedtools merge for panel_id=%s, panel_version=%s, genome_build=%s",
            panel_id,
            panel_version,
            genome_build,
        )
        variant_validator_api_functions.bedtools_merge(
            panel_id, panel_version, genome_build
        )
        logger.info(
            "Bedtools merge completed successfully for panel_id=%s", panel_id)

        # Log completion of the process
        logger.info("Process completed successfully for panel_id=%s", panel_id)

    except Exception as e:
        # Reraise the exception after logging it for further handling if needed
        logger.error(
            "An error occurred in the BED file generation process for panel_id=%s: %s",
            panel_id,
            e,
            exc_info=True,
        )
        raise


if __name__ == "__main__":
    main()
