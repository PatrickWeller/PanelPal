"""
Compare Panel Versions

This script compares two versions of a gene panel to identify differences 
in gene composition between them. Specifically, it outputs lists of genes 
that have been added or removed from one panel version to the next.

Parameters
----------
-p, --panel : str
    The unique identifier for the gene panel (e.g., "R123").
-v, --versions : float, float
    Two version numbers for the panel, in order to compare changes 
    between them (e.g., 1.0 and 2.0). The script determines which 
    version is older based on the numbers provided.
-f, --status_filter : 'green', 'amber', 'all'
    The option for filtering between keeping just green genes,
    or green and amber, or all genes.

Example
-------
Run the following command in the terminal:
    $ python compare_gene_lists.py -p R123 -v 1.0 2.0

This will compare version 1.0 with version 2.0 of the R123 panel and 
output any genes that have been added or removed.
"""

import argparse
import sys
from PanelPal.accessories.panel_app_api_functions import (
    get_response, get_name_version, get_response_old_panel_version, get_genes,
)
from PanelPal.accessories.panel_app_api_functions import PanelAppError
from PanelPal.settings import get_logger

logger = get_logger(__name__)

def main(panel=None, versions=None, status_filter='green'):
    """
    Compares gene lists between two versions of a genetic panel from PanelApp.

    This function:
    1. Parses command-line arguments to retrieve the panel R number and versions.
    2. Sends API requests to fetch data for the specified panel and its versions.
    3. Compares the gene lists of the two panel versions to identify differences.
    4. Prints the lists of added and removed genes between the versions.

    Parameters
    ----------
    panel : str, optional
        The panel ID to compare. If None, will be parsed from command-line arguments.
    versions : list, optional
        List of two version numbers to compare.
        If None, will be parsed from command-line arguments.
    status_filter : str, optional
        Filter option for gene status. Defaults to 'green'.

    Raises
    ------
    PanelAppError
        If the specified panel or panel versions do not exist in the PanelApp database.

    Exits
    -----
    The program will terminate with an error message in the following cases:
    - The panel name is incorrect.
    - A specified panel version does not exist.

    Notes
    -----
    - Uses `determine_order` to ensure proper chronological comparison of versions.
    - Relies on helper functions such as `get_response`, `get_genes`, and `get_removed_genes`.

    Examples
    --------
    Run the script with appropriate arguments:
    >>> python compare_panel_versions.py -p R1234 -v 1.0 2.0 -f green

    Output:
    Removed genes: ['BRCA1', 'TP53']
    Added genes: ['BRCA2', 'MEF2C']
    """

    # Accesses values from the command line through argument parsing
    if panel is None or versions is None:
        args = argument_parser()
        panel = args.panel
        versions = args.versions
        status_filter = args.status_filter

    # Works out which version number is older than the other
    older_version, newer_version = determine_order(versions)

    # Send API request for the panel provided
    try:
        panel_json = get_response(panel)
    # Exit the program if that panel does not exist
    except PanelAppError:
        logger.error("Panel %s is incorrect", panel)
        sys.exit(1)

    # Access and store the primary key of that panel from the Panel APP database
    panel_info = get_name_version(panel_json)
    panel_pk = panel_info["panel_pk"]

    # Send API request for the older panel version
    try:
        older_version_json = get_response_old_panel_version(panel_pk, older_version)
    # Exit the program if that version does not exist
    except PanelAppError:
        logger.error("Panel %s v%s may not exist, please check and try again", panel, older_version)
        sys.exit(1)
    # Send API request for the newer panel version
    try:
        newer_version_json = get_response_old_panel_version(panel_pk, newer_version)
    # Exit the program if that version does not exist
    except PanelAppError:
        logger.error("Panel %s v%s may not exist, please check and try again", panel, newer_version)
        sys.exit(1)

    # Get the list of genes for each panel version
    older_version_genes = get_genes(older_version_json, status_filter=status_filter)
    newer_version_genes = get_genes(newer_version_json, status_filter=status_filter)

    # Compare the 2 versions for removed or added genes
    removed = get_removed_genes(older_version_genes, newer_version_genes)
    added = get_added_genes(older_version_genes, newer_version_genes)

    # Print the differences in gene lists
    print("Removed genes:", removed)
    print("Added genes:", added)


def validate_panel(panel):
    """
    Checks that a panel is in the format R21, otherwise raises ArgumentTypeError and ends program
    """
    # Checks that panel starts with R and is followed by digits
    if panel.startswith('R') and panel[1:].isdigit():
        return panel
    # Raises an error if the panel is the wrong format
    raise argparse.ArgumentTypeError("Panel must be an R number in format 'R21'.")


def argument_parser():
    """
    Creates and configures an argmuent parser for the command line interface
    for running compare_gene_lists.py
    
    Parameters
    ----------
    None
    
    Returns
    -------
    argparse.Namespace
        An object containing the parser command-line arguments.

    Examples
    --------
    Run the script from the command line:
    
    >>> python compare_panel_versions.py -p R1234 -v 1.0 2.0 -f green

    This will parse the arguments into a namespace object:
    
    >>> args = argument_parser()
    >>> print(args)
    Namespace(panel='R1234', versions=[1.0, 2.0], status_filter='green')
    """
    # Create an argument parser object
    parser = argparse.ArgumentParser(
        description='A script to compare the genes on two versions of an NGS panel'
    )

    # Add the panel argument (AKA the R number)
    parser.add_argument(
        '-p', '--panel',
        type=validate_panel,
        help='R number. Include the R',
        required=True)

    # Add the versions argument for the panel
    parser.add_argument(
        '-v', '--versions',
        type=float,
        help='Two panel versions. E.g. 1.1 or 69.23',
        nargs=2,
        required=True)

    # Add the status_filter argument, which is optional for filtering genes of differing status
    parser.add_argument(
        '-f', '--status_filter',
        choices=["green", "amber", "red", "all"],
        help='Filter by gene status. Green only; green and amber; or all',
        default='green')

    # Return the name space object for use of the arguments
    return parser.parse_args()


def determine_order(versions):
    """
    Checks which of 2 version numbers is older and which is newer

    Parameters
    ----------
    versions: list of float
        A list of 2 version numbers

    Returns
    -------
    older_version
        The earlier version of the two numbers
    newer_version
        The newer version of the two numbers

    Example
    -------
    >>> versions = [2.3, 1.0]
    >>> determine_order(versions)
    1.0, 2.3
    """
    # If the first 'versions' argument is lower, name this as the older version.
    if versions[0] < versions[1]:
        older_version, newer_version = versions[0], versions[1]
    # if the latter 'versions' argument is lower, name this as the older version.
    else:
        older_version, newer_version = versions[1], versions[0]
    # Return these ordered values
    return older_version, newer_version


def is_gene_absent(gene, gene_list):
    """
    Checks whether a gene is absent from a list of genes
    (i.e. the list of genes in certain panel version)
    
    Parameters
    ----------
    gene: str
        A HGNC ID for a gene to be checked in a list
    gene_list: list
        A list of all HGNC IDs within a version of a panel
    
    Returns
    -------
    bool
        True if the gene is absent in that version of the panel; otherwise False
    
    Example
    -------
    >>> gene = "MYC"
    >>> gene_list = ["BRCA1", "BRCA2", "TP53"]
    >>> is_gene_absent(gene, gene_list)
    True
    """
    return gene not in gene_list

def get_removed_genes(older_panel, newer_panel):
    """
    Compares 2 versions of a panel, and outputs which genes have been
    removed from the newer version of the panel that were in the older version
    
    Parameters
    ----------
    older_panel: list
        HGNC IDs of genes that were in a panel of an older version than newer_panel
    newer_panel: list
        HGNC IDs of genes that are in a panel of a newer version than older_panel
    
    Returns
    -------
    list
        A List of genes that were in the older version of the panel,
        but are no longer in the newer version
    
    Example
    -------
    >>> older_panel = ["BRCA1", "BRCA2", "MYC", "TP53"]
    >>> newer_panel = ["BRCA1", "MYC", "CHEK2"]
    >>> get_removed_genes(older_panel, newer_panel)
    ["BRCA2", "TP53"]
    """
    # Filter the genes in the older panel that are not present in the newer panel
    filtered_list = filter(lambda item: is_gene_absent(item, newer_panel), older_panel)

    # Initialize an empty list to store the removed genes
    removed_genes = []

    # Iterate through the filtered genes and append them to the removed_genes list
    for gene in filtered_list:
        removed_genes.append(gene)

    # Return the list of removed genes
    logger.info("%d genes removed from this panel between these 2 versions", len(removed_genes))
    return removed_genes

def get_added_genes(older_panel, newer_panel):
    """
    Compares 2 versions of a panel, and outputs which genes have been
    added to the newer version of the panel
    
    Parameters
    ----------
    older_panel: list
        HGNC IDs of genes that were in a panel of an older version than newer_panel
    newer_panel: list
        HGNC IDs of genes that are in a panel of a newer version than older_panel
    
    Returns
    -------
    list
        A List of genes that are in the newer version of the panel
        but not the older version of the panel
    
    Example
    -------
    >>> older_panel = ["BRCA1", "MYC", "CHEK2"]
    >>> newer_panel = ["BRCA1", "BRCA2", "MYC", "TP53"]
    >>> get_removed_genes(older_panel, newer_panel)
    ["BRCA2", "TP53"]
    """
    # Filter the genes in the newer panel that are not present in the older panel
    filtered_list = filter(lambda item: is_gene_absent(item, older_panel), newer_panel)

    # Initialize an empty list to store the added genes
    added_genes = []

    # Iterate through the filtered genes and append them to the added_genes list
    for gene in filtered_list:
        added_genes.append(gene)

    # Return the list of added genes
    logger.info("%d genes added to this panel between these 2 versions", len(added_genes))
    return added_genes


if __name__ == "__main__":  # pragma: no cover
    main()
