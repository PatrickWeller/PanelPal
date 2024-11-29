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
import requests
from accessories.panel_app_api_functions import get_response, get_name_version, get_response_old_panel_version, get_genes

def main():
    # Accesses values from the command line
    args = argument_parser()
    
    # Assigns command line arguments to variables
    panel = args.panel # single str
    versions = args.versions # list of 2 versions
    
    # Works out which version number is older than the other
    # older_version, newer_version = which_is_older(versions)
    if versions[0] < versions[1]:
        older_version, newer_version = versions[0], versions[1]
    else:
        older_version, newer_version = versions[1], versions[0]


    panel_json = get_response(panel)

    panel_info = get_name_version(panel_json)
    panel_pk = panel_info["panel_pk"]


    older_version_json = get_response_old_panel_version(panel_pk, older_version)
    newer_version_json = get_response_old_panel_version(panel_pk, newer_version)

    older_version_genes = get_genes(older_version_json)
    newer_version_genes = get_genes(newer_version_json)

    removed_genes = get_removed_genes(older_version_genes, newer_version_genes)
    added_genes = get_added_genes(older_version_genes, newer_version_genes)

    print(removed_genes)
    print(added_genes)
    

    
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
    #
    #######
    ### Not done with this
    ### Is 1 a valid version, or is 1.0 or 1.1 always the first?
    ####### 
    #
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-p', '--panel', type=str, help='R number. Include the R', required=True)
    argument_parser.add_argument('-v', '--versions', type=float, help='Panel versions. E.g. 1.1, you must provide 2 values', nargs=2, required=True)
    return argument_parser.parse_args()


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
    removed_genes = 'Removed Genes: '
    for gene in filtered_list:
        if removed_genes == 'Removed Genes: ':
            removed_genes += gene
        else:
            removed_genes += ', ' + gene
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
    added_genes = 'Added Genes: '
    for gene in filtered_list:
        if added_genes == 'Added Genes: ':
            added_genes += gene
        else:
            added_genes += ', ' + gene
    return added_genes


if __name__ == "__main__":
    main()