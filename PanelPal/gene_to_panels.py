#!/usr/bin/env python

import requests
import argparse
import pandas as pd
import re
from settings import get_logger  # Ensure this exists or use a fallback.

# Fallback for logger if settings module is not available
def get_logger(name):
    import logging
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)


def parse_arguments():
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Check and retrieve panel information."
    )
    parser.add_argument(
        "--hgnc_symbol",
        type=str,
        help="The HGNC symbol of the gene to query (e.g., BRCA1).",
        required=True,
    )
    parser.add_argument(
        "--r_codes_file",
        type=str,
        help="Path to the R_codes.txt file.",
        required=False,
    )
    return parser.parse_args()


def load_r_codes(file_path="PanelPal/resources/R_codes.txt"):
    """
    Load R codes and names from a text file into a pandas DataFrame.

    Parameters
    ----------
    file_path : str
        Path to the R_codes.txt file.

    Returns
    -------
    pd.DataFrame
        DataFrame containing R codes and their associated names.
    """
    try:
        return pd.read_csv(file_path, sep="\t")
    except Exception as e:
        raise ValueError(f"Error loading R codes file: {e}")


def get_response_gene(hgnc_symbol):
    """
    Send a GET request to the PanelApp API to retrieve information about a gene.

    Parameters
    ----------
    hgnc_symbol : str
        The HGNC symbol of the gene to query.

    Returns
    -------
    requests.Response
        The API response object.
    """
    url = f"https://panelapp.genomicsengland.co.uk/api/v1/genes/?entity_name={hgnc_symbol}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Raise an error for bad HTTP responses
    return response


def extract_panels(response_json):
    """
    Extract panel IDs and names from the API response JSON.

    Parameters
    ----------
    response_json : dict
        The parsed JSON response from the API.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing panel IDs and names.
    """
    panels = []
    for result in response_json.get("results", []):
        panel = result.get("panel")
        if panel:
            panel_id = panel.get("id")
            panel_name = panel.get("name")
            relevant_disorders = panel.get("relevant_disorders")
            if panel_id and panel_name:
                panels.append({"PanelApp ID": panel_id, "Panel Name": panel_name, "Relevant Disorders": relevant_disorders})
    return pd.DataFrame(panels)


def add_r_codes_to_panels(panels_df, r_codes_df):
    """
    Add R codes to panels by matching Panel Names.

    Parameters
    ----------
    panels_df : pd.DataFrame
        DataFrame containing Panel IDs and Names from the API.
    r_codes_df : pd.DataFrame
        DataFrame containing R codes and their associated names.

    Returns
    -------
    pd.DataFrame
        Updated DataFrame with an added 'R Code' column.
    """
    merged_df = panels_df.merge(
        r_codes_df, how="left", left_on="Panel Name", right_on="name"
    )
    merged_df.rename(columns={"r_code": "R Code"}, inplace=True)
    merged_df.drop(columns=["name"], inplace=True, errors="ignore")
    return merged_df


def main(hgnc_symbol=None):
    # Create a logger, named after this module, e.g., check_panel
    logger = get_logger(__name__)

    # Parse arguments / set parameters
    if hgnc_symbol is None:
        args = parse_arguments()
        hgnc_symbol = args.hgnc_symbol

    try:
        # Load R codes file
        r_codes_df = load_r_codes(args.r_codes_file)

        # Get response from PanelApp API
        logger.info(f"Querying PanelApp API for gene: {args.hgnc_symbol}")
        response = get_response_gene(args.hgnc_symbol)
        response_json = response.json()

        # Extract panel data
        panels_df = extract_panels(response_json)
        if panels_df.empty:
            logger.info(f"No panels found for gene {args.hgnc_symbol}.")
            print(f"No panels found for gene {args.hgnc_symbol}.")
            return
        
        #print(panels_df)

        # Add R codes
        panels_with_r_codes = add_r_codes_to_panels(panels_df, r_codes_df)

        # Display the results
        print(f"Panels associated with gene {hgnc_symbol}:\n")
        print(f"{'PanelApp ID':<15}{'R Code':<10}{'Panel Name':<50}")
        print("-" * 75)

        for _, row in panels_with_r_codes.iterrows():
            panel_id = row["PanelApp ID"]
            r_code = row["R Code"] if not pd.isna(row["R Code"]) else "-"
            panel_name = row["Panel Name"]
            print(f"{panel_id:<15}{r_code:<10}{panel_name:<50}")

    except requests.RequestException as e:
        logger.error(f"Error querying the API: {e}")
        print(f"Error querying the API: {e}")
    except ValueError as ve:
        logger.error(ve)
        print(ve)


if __name__ == "__main__":
    main()
