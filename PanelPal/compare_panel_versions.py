"""
Compare Gene Lists

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

Example
-------
Run the following command in the terminal:
    $ python compare_gene_lists.py -p R123 -v 1.0 2.0

This will compare version 1.0 with version 2.0 of the R123 panel and 
output any genes that have been added or removed.
"""

import argparse
import sys
from accessories.panel_app_api_functions import get_response, get_name_version, get_response_old_panel_version, get_genes
from accessories.panel_app_api_functions import PanelAppError
from settings import get_logger


def main():
    logger = get_logger(__name__)
    
    # Accesses values from the command line
    args = argument_parser()

    # Assigns command line arguments to variables
    panel = args.panel # single str
    versions = args.versions # list of 2 versions
    
    # Works out which version number is older than the other
    older_version, newer_version = determine_order(versions)

    # Send API request for the panel provided
    try:
        panel_json = get_response(panel)
    # Exit the program if that panel does not exist
    except PanelAppError:
        logger.error(f"Panel {panel} is incorrect")
        sys.exit(1)

    # Access and store the primary key of that panel from the Panel APP database
    panel_info = get_name_version(panel_json)
    panel_pk = panel_info["panel_pk"]

    # Send API request for the older panel version
    try:
        older_version_json = get_response_old_panel_version(panel_pk, older_version)
    # Exit the program if that version does not exist
    except PanelAppError:
        print(f"Panel {panel} v{older_version} may not exist, please check and try again")
        sys.exit(1)
    # Send API request for the newer panel version
    try:
        newer_version_json = get_response_old_panel_version(panel_pk, newer_version)
    # Exit the program if that version does not exist
    except PanelAppError:
        logger.error(f"Panel {panel} v{newer_version} may not exist, please check and try again")
        sys.exit(1)

    # Get the list of genes for each panel version
    older_version_genes = get_genes(older_version_json)
    newer_version_genes = get_genes(newer_version_json)

    # Compare the gene lists for each version to identify the differences
    removed_genes = get_removed_genes(older_version_genes, newer_version_genes)
    added_genes = get_added_genes(older_version_genes, newer_version_genes)

    # Print the two lists to show the difference in panel versions
    print("Removed genes:", removed_genes)
    print("Added genes:", added_genes)
    

def validate_panel(panel):
    """Checks that a panel is in the format R21, otherwise raises ArgumentTypeError and ends program"""
    # Checks that panel starts with R and is followed by digits
    if panel.startswith('R') and panel[1:].isdigit():
        return panel
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
        
    Example
    -------

    """
    argument_parser = argparse.ArgumentParser(
        description='A script to compare the genes on two versions of an NGS panel'
    )
    
    argument_parser.add_argument(
        '-p', '--panel',
        type=validate_panel,
        help='R number. Include the R',
        required=True)

    argument_parser.add_argument(
        '-v', '--versions',
        type=float,
        help='Two panel versions. E.g. 1.1 or 69.23',
        nargs=2,
        required=True)

    argument_parser.add_argument(
        '-f', '--filter',
        choices=["green", "amber", "all"],
        help='Filter by gene status. Green only; green and amber; or all',
        nargs=1,
        default='green')
    
    return argument_parser.parse_args()


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
    if versions[0] < versions[1]:
        older_version, newer_version = versions[0], versions[1]
    else:
        older_version, newer_version = versions[1], versions[0]
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
    >>> query_gene_against_list(gene, gene_list)
    True
    """
    if gene not in gene_list:
        return True
    else:
        return False

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
    filtered_list = filter(lambda item: is_gene_absent(item, newer_panel), older_panel)
    removed_genes = []
    for gene in filtered_list:
        removed_genes.append(gene)
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
    filtered_list = filter(lambda item: is_gene_absent(item, older_panel), newer_panel)
    added_genes = []
    for gene in filtered_list:
        added_genes.append(gene)
    return added_genes


if __name__ == "__main__":
    main()