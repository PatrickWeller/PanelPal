#!/usr/bin/env python

"""
Generate a list of genes in a panel from PanelApp API.

This script fetches panel data from PanelApp using the provided panel ID and version.
It extracts the list of genes from the panel data based on the specified confidence status
(default = green genes only). The gene list is then written to a file in TSV format.

Command-Line Arguments
----------------------
-p, --panel_id : str
    The ID of the panel to fetch data for (e.g., "R207").
-v, --panel_version : float
    The version of the panel to fetch data for (e.g., "4.0").
--confidence_status : str
    Filter genes by minimum confidence status. Choices are 'red', 'amber', 'green', or 'all'.
    Defaults to 'green'.

Example Usage
-------------
Run the script from the command line:
>>> python gene_to_panels.py --panel_id R207 --panel_version 1.2 --confidence_status green

Logging
-------
Logs are written to `panelpal/logging/panelpal.log`.
settings.py can be modified to also write logs to the stream.

Notes
-----
- This script assumes that the user has valid access to PanelApp API.
- The gene list is written to a file in the current working directory.
- The gene list file is named as `panel_id_version_confidence_genes.tsv`.
- The gene list file contains one gene per line.
- The gene list file is overwritten if it already exists.
"""


import argparse
from PanelPal.accessories import panel_app_api_functions
from PanelPal.settings import get_logger
from PanelPal.check_panel import is_valid_panel_id

# Set up logger
logger = get_logger(__name__)


def parse_arguments():
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed arguments.
    """

    # Define the parser
    parser = argparse.ArgumentParser(
        description="Get a list of genes in a panel",
        epilog="Example usage: python gene_to_panels.py --panel_id R207 --panel_version 1.2 "
        "--confidence_status green",
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

    # Define the confidence_status argument
    parser.add_argument(
        "--confidence_status",
        type=str,
        default="green",
        choices=["red", "amber", "green", "all"],
        help=(
            "Filter panels by confidence status. Choices are 'green', 'amber', or 'red'. "
            "Defaults to 'green'."
        ),
    )

    # Return the parsed arguments
    return parser.parse_args()


def write_genes_to_file(gene_list, output_file):
    """
    Write the list of genes to a file in TSV format.

    Parameters
    ----------
    gene_list : list
        List of genes to write to the file.
    output_file : str
        Path to the output file.
    """

    # Write the gene list to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        for gene in gene_list:
            f.write(f"{gene}\n")

    # Log the gene list written to file
    logger.info("Gene list written to file: %s", output_file)


def main(panel_id=None, panel_version=None, confidence_status="green"):
    """
    Main function to fetch and process gene panel data from PanelApp.
    Parameters
    ----------
    panel_id : str, optional
        The ID of the panel to fetch data for. If not provided, it will
        be parsed from command line arguments.
    panel_version : str, optional
        The version of the panel to fetch data for. If not provided, it
        will be parsed from command line arguments.
    confidence_status : str, optional
        The confidence status filter for genes. Default is 'green'.
    Raises
    ------
    ValueError
        If the provided panel_id is invalid.
    KeyError
        If there is an issue with accessing data in the response.
    IOError
        If there is an issue with file operations.
    Exception
        For any other unexpected errors.
    Notes
    -----
    This function logs various stages of execution and errors using the logger.
    It fetches panel data from PanelApp, extracts gene information based on the
    specified confidence status, and writes the gene list to a file.
    """

    try:
        # Accesses values from the command line through argument parsing if
        # not passed directly from PanelPal main() function
        if panel_id is None or panel_version is None:
            args = parse_arguments()
            panel_id = args.panel_id
            panel_version = args.panel_version
            confidence_status = args.confidence_status

        # Log the commands executed
        logger.info(
            "Command executed: panel-genes --panel_id %s --panel_version %s "
            "--confidence_filter %s",
            panel_id,
            panel_version,
            confidence_status,
        )

        # Check if the panel_id is valid. If not, log and raise a ValueError
        if not is_valid_panel_id(panel_id):
            logger.error(
                "Invalid panel_id '%s'. Panel ID must start with 'R' followed "
                "by digits (e.g., 'R207').",
                panel_id,
            )
            raise ValueError(
                f"Invalid panel_id '{panel_id}'. Panel ID must start with "
                "'R' followed by digits (e.g., 'R207')."
            )

        # Fetch the panel data from PanelApp using the panel_id
        logger.debug("Requesting panel data for panel_id=%s", panel_id)
        panelapp_data = panel_app_api_functions.get_response(panel_id)
        logger.info("Panel data fetched successfully for panel_id=%s", panel_id)

        # Get panel primary key to extract data by version
        logger.debug("Extracting panel primary key for panel_version=%s", panel_version)
        panel_pk = panelapp_data.json().get("id", "N/A")
        logger.info(
            "Panel primary key (%s) extracted successfully for panel_id=%s using panel_version=%s",
            panel_pk,
            panel_id,
            panel_version,
        )

        # Request panel data for the specified panel version
        logger.debug("Requesting panel data for panel_pk=%s", panel_pk)
        panelapp_v_data = panel_app_api_functions.get_response_old_panel_version(
            panel_pk, panel_version
        )
        logger.info(
            "Panel data fetched successfully for panel_id=%s, panel_pk=%s, "
            "panel_version=%s",
            panel_id,
            panel_pk,
            panel_version,
        )

        # Extract the list of genes from the panel data
        logger.debug(
            "Extracting gene list from panel data for panel_id=%s, confidence_status=%s",
            panel_id,
            confidence_status,
        )
        gene_list = panel_app_api_functions.get_genes(
            panelapp_v_data, confidence_status
        )
        logger.info(
            "Gene list extracted successfully for panel_id=%s, panel_version=%s. "
            "Total genes found: %d",
            panel_id,
            panel_version,
            len(gene_list),
        )

        # Save gene list to file
        outfile = f"{panel_id}_v{panel_version}_{confidence_status}_genes.tsv"
        write_genes_to_file(gene_list, outfile)

    # Catch and log specific exceptions
    except ValueError as ve:
        logger.error("ValueError: %s", str(ve))
        raise
    except KeyError as ke:
        logger.error("KeyError: %s", str(ke))
        raise
    except IOError as ioe:
        logger.error("IOError: %s", str(ioe))
        raise

    # Catch and log any other exceptions
    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))
        raise


if __name__ == "__main__":
    main()
