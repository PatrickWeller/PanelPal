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
    The version of the panel as a float (e.g., "4.0").
-g, --genome_build : str
    The genome build to be used (e.g., "GRCh38").
-f, --status_filter : str
    The lowest acceptable gene status to filter by (e.g "amber").
    Default is green.

Example
-------
Run the script from the command line:
>>> python generate_bed.py -p R207 -v 4 -g GRCh38 -f amber


Logging
-------
Logs are written to `panelpal/logging/panelpal.log`.
settings.py can be modified to also write logs to the stream

Notes
-----
- This script assumes that the user has valid access to PanelApp and VariantValidator APIs.

"""
import argparse
import sys
import os
from PanelPal.db_input import (
    add_patient_to_db,
    add_bed_file_to_db,
    add_panel_data_to_db,
    patient_info_prompt,
    bed_file_info_prompt
)
from PanelPal.settings import get_logger
from PanelPal.accessories import variant_validator_api_functions
from PanelPal.accessories import panel_app_api_functions
from PanelPal.accessories.bedfile_functions import bed_file_exists, bed_head
from PanelPal.check_panel import is_valid_panel_id
from PanelPal.settings import get_logger
# Adds parent directory to python module search path
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
    status_filter : str
        The lowest acceptable gene status to filter by (e.g., "amber").
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
        type=float,
        required=True,
        help='The version of the panel (e.g., "4.0").',
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

    # Define the status_filter argument
    parser.add_argument(
        "-f",
        "--status_filter",
        choices=["green", "amber", "red", "all"],
        help='Filter by gene status. Green only; green and amber; or all',
        default='green'
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Log the parsed arguments
    logger.debug(
        "Parsed command-line arguments: panel_id=%s, panel_version=%s, "
        "genome_build=%s, status_filter=%s",
        args.panel_id,
        args.panel_version,
        args.genome_build,
        args.status_filter,
    )

    return args


def main(panel_id=None, panel_version=None, genome_build=None, status_filter='green'):
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
    status_filter : str
        The gene status to filter by (e.g., "amber").
        Default is green.

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
        status_filter = args.status_filter

    if not is_valid_panel_id(panel_id):
        logger.error(
            "Invalid panel_id '%s'. Panel ID must start with 'R' followed "
            "by digits (e.g., 'R207').", panel_id
        )
        raise ValueError(
            f"Invalid panel_id '{args.panel_id}'. Panel ID must start with "
            "'R' followed by digits (e.g., 'R207')."
        )

    logger.info(
        "Command executed: generate-bed --panel_id %s, --panel_version %s "
        "--genome_build %s, --status_filter %s",
        panel_id,
        panel_version,
        genome_build,
        status_filter
    )

    if bed_file_exists(panel_id, panel_version, genome_build):
        logger.warning(
            "Process stopping: BED file already exists for panel_id=%s, "
            "panel_version=%s, genome_build=%s.",
            panel_id,
            panel_version,
            genome_build,
        )
        print(
            f"PROCESS STOPPED: A BED file for the panel '{panel_id}' "
            f"(version {panel_version}, build {genome_build}) already exists."
        )
        return

    logger.debug("No existing BED file found. Proceeding with generation.")

    if bed_file_exists(panel_id, panel_version, genome_build):
        logger.warning(
            "Process stopping: BED file already exists for panel_id=%s, "
            "panel_version=%s, genome_build=%s.",
            panel_id,
            panel_version,
            genome_build,
        )
        print(
            f"PROCESS STOPPED: A BED file for the panel '{panel_id}' "
            f"(version {panel_version}, build {genome_build}) already exists."
        )
        return

    logger.debug("No existing BED file found. Proceeding with generation.")

    try:
        # Prompt the user for patient information
        patient_info = patient_info_prompt()

        # If patient info is provided, the dictionary returned = database input
        if patient_info:
            add_patient_to_db(patient_info)

            # Prompt user for BED file metadata if patient info was provided
            bed_file_info = bed_file_info_prompt(
                patient_id=patient_info["patient_id"],
                panel_name=panel_id,
                panel_version=panel_version,
                genome_build=genome_build
            )
            # add BED file to database
            add_bed_file_to_db(bed_file_info)

            # Retrieve BED file ID (i.e. the path to the BED file)
            bed_file_id = bed_file_info["bed_file"]

            # Fetch the panel data and add to the database
            add_panel_data_to_db(panel_id, bed_file_id)

            # Log success
            logger.info(
                "Record added to the database for patient ID: %s",
                patient_info["patient_id"])

        else:
            # If patient info is not provided, skip adding to the database
            pass

        # Fetch the panel data from PanelApp using the panel_id
        logger.debug("Requesting panel data for panel_id=%s", panel_id)
        panelapp_data = panel_app_api_functions.get_response(panel_id)
        logger.info("Panel data fetched successfully for panel_id=%s", panel_id)

        # Get panel primary key to extract data by version
        panel_pk = panelapp_data.json().get("id", "N/A")

        logger.debug("Requesting panel data for panel_pk=%s, panel_version=%s",
                     panel_pk, panel_version)
        panelapp_v_data = panel_app_api_functions.get_response_old_panel_version(
            panel_pk, panel_version)
        logger.info("Panel data fetched successfully for panel_id=%s, panel_pk=%s,"
                    "panel_version=%s",
                    panel_id, panel_pk,
                    panel_version)

        # Extract the list of genes from the panel data
        logger.debug("Extracting gene list from panel data for panel_id=%s, status_filter=%s",
                     panel_id, status_filter)
        gene_list = panel_app_api_functions.get_genes(
            panelapp_v_data, status_filter)

        logger.info(
            "Gene list extracted successfully for panel_id=%s, panel_version=%s."
            "Total genes found: %d",
            panel_id,
            panel_version,
            len(gene_list),
        )

        # Generate the BED file using the gene list, panel ID, panel version, and genome build
        logger.debug(
            "Generating BED file for panel_id=%s, panel_version=%s, "
            "genome_build=%s, status_filter=%s",
            panel_id,
            panel_version,
            genome_build,
            status_filter,
        )
        variant_validator_api_functions.generate_bed_file(
            gene_list, panel_id, panel_version, genome_build
        )
        logger.info("BED file generated successfully for panel_id=%s", panel_id)

        # Perform bedtools merge with the provided panel details
        logger.debug(
            "Starting bedtools merge for panel_id=%s, panel_version=%s, "
            "genome_build=%s, status_filter=%s",
            panel_id,
            panel_version,
            genome_build,
            status_filter
        )
        variant_validator_api_functions.bedtools_merge(
            panel_id, panel_version, genome_build
        )
        logger.info("Bedtools merge completed successfully for panel_id=%s",
                    panel_id)  # pragma: no cover

        # Add headers to both the original and merged BED files
        num_genes = len(gene_list)
        bed_name = f"bed_files/{panel_id}_v{panel_version}_{genome_build}.bed"
        merged_bed_name = f"bed_files/{panel_id}_v{
            panel_version}_{genome_build}_merged.bed"
        bed_head(panel_id, panel_version, genome_build, num_genes, bed_name)
        bed_head(panel_id, panel_version, genome_build,
                 num_genes, merged_bed_name)

        # Log completion of the process
        logger.info("Process completed successfully for panel_id=%s",
                    panel_id)  # pragma: no cover

    except Exception as e:
        # Reraise the exception after logging it for further handling if needed
        logger.error(
            "An error occurred in the BED file generation process for panel_id=%s: %s",
            panel_id,
            e,
            exc_info=True,
        )
        raise


if __name__ == "__main__":  # pragma: no cover
    main()
