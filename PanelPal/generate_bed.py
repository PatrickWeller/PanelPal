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
3. Merges overlapping regions in the BED file.

Requirements
------------
- Python 3.x
- Access to PanelApp and VariantValidator APIs.
- bedtools installed and available in the system PATH.

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
DEBUG level logs are written to both the console and `logging/generate_bed.log`.

Notes
-----
- This script assumes that the user has valid access to PanelApp and VariantValidator APIs.

"""

import argparse
import logging
# Custom module for PanelApp API interaction
from accessories import panel_app_api_functions
# Custom module for VariantValidator API interaction
from accessories import variant_validator_api_functions

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Log all levels (DEBUG, INFO, WARNING, ERROR)
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/home/madyson/PanelPal/logging/generate_bed.log"),
        logging.StreamHandler()  # Logs also printed to console
    ]
)

# Create a logger instance for consistent usage throughout the script
logger = logging.getLogger()

def main(panel_id, panel_version, genome_build):
    """
    Main function that processes the panel data and generates the BED file.
    
    Parameters
    ----------
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
    # Log the start of the BED generation process
    logging.info(
        "Starting main process for panel_id=%s, panel_version=%s, genome_build=%s", 
        panel_id,
        panel_version,
        genome_build
        )

    try:
        # Fetch the panel data from PanelApp using the panel_id
        logging.debug(
            "Requesting panel data for panel_id=%s", 
            panel_id
            )
        panelapp_data = panel_app_api_functions.get_response(panel_id)
        logging.info(
            "Panel data fetched successfully for panel_id=%s",
            panel_id
            )

        # Extract the list of genes from the panel data
        logging.debug(
            "Extracting gene list from panel data for panel_id=%s",
            panel_id
            )
        gene_list = panel_app_api_functions.get_genes(panelapp_data)
        logging.info(
            "Gene list extracted successfully for panel_id=%s. Total genes found: %d",
            panel_id,
            len(gene_list)
            )

        # Generate the BED file using the gene list, panel ID, panel version, and genome build
        logging.debug(
            "Generating BED file for panel_id=%s, panel_version=%s, genome_build=%s",
            panel_id,
            panel_version,
            genome_build
            )
        variant_validator_api_functions.generate_bed_file(gene_list,
                                                          panel_id,
                                                          panel_version,
                                                          genome_build
                                                          )
        logging.info(
            "BED file generated successfully for panel_id=%s",
            panel_id
            )

        # Perform bedtools merge with the provided panel details
        logging.debug(
            "Starting bedtools merge for panel_id=%s, panel_version=%s, genome_build=%s",
            panel_id,
            panel_version,
            genome_build
            )
        variant_validator_api_functions.bedtools_merge(panel_id,
                                                       panel_version,
                                                       genome_build
                                                       )
        logging.info(
            "Bedtools merge completed successfully for panel_id=%s",
            panel_id
            )

        # Log completion of the process
        logging.info(
            "Process completed successfully for panel_id=%s",
            panel_id
            )

    except Exception as e:
        # Reraise the exception after logging it for further handling if needed
        logging.error(
            "An error occurred in the BED file generation process for panel_id=%s: %s",
            panel_id,
            e,
            exc_info=True
            )
        raise


if __name__ == '__main__':
    # Parses command-line arguments and calls the main function.

    # Set up argument parsing for the command-line interface (CLI)
    parser = argparse.ArgumentParser(
        description='Generate a BED file and perform merge using panel details.'
        )

    # Define the panel_id argument
    parser.add_argument('-p', '--panel_id',
                        type=str,
                        required=True,
                        help='The ID of the panel, (e.g., "R207").'
                        )

    # Define the panel_version argument
    parser.add_argument('-v', '--panel_version',
                        type=str,
                        required=True,
                        help='The version of the panel (e.g., "4").'
                        )

    # Define the genome_build argument
    parser.add_argument('-g', '--genome_build',
                        type=str,
                        required=True,
                        help='The genome build (e.g., GRCh38).'
                        )

    # Parse the command-line arguments
    args = parser.parse_args()
    logging.debug(
        "Parsed command-line arguments: panel_id=%s, panel_version=%s, genome_build=%s",
        args.panel_id,
        args.panel_version,
        args.genome_build
        )

    # Call the main function with the parsed arguments
    main(args.panel_id,
         args.panel_version,
         args.genome_build
         )
