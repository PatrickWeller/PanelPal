#!/usr/bin/env python

import argparse
import re
import requests
import pandas as pd
from settings import get_logger  # Ensure this exists or use a fallback.
from accessories.panel_app_api_functions import get_response_gene


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
    return parser.parse_args()


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
            panels.append(
                {
                    "PanelApp ID": panel_id,
                    "Panel Name": panel_name,
                    "Relevant Disorders": relevant_disorders,
                }
            )
    return pd.DataFrame(panels)


def extract_r_codes(disorders):
    """
    Extract R codes from the relevant disorders string.

    Parameters
    ----------
    disorders : str or None
        A string containing the relevant disorders information, or None.

    Returns
    -------
    str
        A comma-separated string of extracted R codes, or "N/A" if no R codes are found.
    """
    if not disorders:
        return "N/A"
    r_codes = re.findall(r"R\d+", str(disorders))
    return ", ".join(r_codes) if r_codes else "N/A"


def extract_r_codes_from_disorders(panels_df):
    """
    Add an 'R Code' column to the panels DataFrame by extracting R codes.

    Parameters
    ----------
    panels_df : pd.DataFrame
        The DataFrame containing panel information with a 'Relevant Disorders' column.

    Returns
    -------
    pd.DataFrame
        A DataFrame with an added 'R Code' column where extracted R codes are listed.
    """
    panels_df["R Code"] = panels_df["Relevant Disorders"].apply(extract_r_codes)
    return panels_df


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


def write_panels(hgnc_symbol, df):

    # Define name of output file
    output_file = f"panels_containing_{hgnc_symbol}.csv"
    
    # Write dataframe to output file
    df.to_csv(
        output_file, 
        columns = ["PanelApp ID","Panel Name"],
        header = ["panelapp_id","panel_name"],
        index = False
    )


def main(hgnc_symbol=None):
    """
    Main function to query PanelApp for gene information and display associated panels.

    Parameters
    ----------
    hgnc_symbol : str, optional
        The HGNC symbol of the gene to query (e.g., BRCA1). If not provided, the function
        parses command-line arguments to retrieve it.

    Returns
    -------
    None
        Prints panel information, including PanelApp IDs, R codes, and panel names, to the console.

    Notes
    -----
    - This function interacts with the PanelApp API to retrieve gene-panel associations.
    - If no panels are found for the specified gene, an appropriate message is displayed.
    - Any HTTP or file errors encountered during execution are logged and printed.
    """

    # Create a logger, named after this module, e.g., check_panel
    logger = get_logger(__name__)

    # Parse arguments / set parameters
    if hgnc_symbol is None:
        args = parse_arguments()
        hgnc_symbol = args.hgnc_symbol
    
    # Log the command and flags executed
    logger.info(f"Command executed: gene-panels --hgnc_symbol {hgnc_symbol}")
    print(f"Command executed: gene-panels --hgnc_symbol {hgnc_symbol}\n")

    try:
        # Load R codes file
        # r_codes_df = load_r_codes()

        # Get response from PanelApp API
        logger.info(f"Querying PanelApp API for gene: {hgnc_symbol}")
        response = get_response_gene(hgnc_symbol)
        response_json = response.json()

        # Extract panel data
        panels_df = extract_panels(response_json)
        if panels_df.empty:
            logger.info(f"No panels found for gene {hgnc_symbol}.")
            print(f"No panels found for gene {hgnc_symbol}.")
            return

        # Extract R codes
        panels_with_r_codes = extract_r_codes_from_disorders(panels_df)
        panels_with_r_codes.replace("N/A", "-", inplace=True)

        print(f"Panels associated with gene {hgnc_symbol}:\n")
        print(f"{'PanelApp ID':<15}{'R Code':<15}{'Panel Name'}")
        print("-" * 100)

        # --------------------------------------------------------------
        
        # Add message recording command executed "gene-panels" and flags 

        # --------------------------------------------------------------

        for _, row in panels_with_r_codes.iterrows():
            panel_id = row["PanelApp ID"]
            r_code = row["R Code"]
            panel_name = row["Panel Name"]
            print(f"{panel_id:<15}{r_code:<15}{panel_name:}")

        # Write list of panels to file
        logger.info(f"Writing panel list to: panels_containing_{hgnc_symbol}.csv")
        write_panels(hgnc_symbol,panels_with_r_codes)
        print(f"\nPanel list saved to: panels_containing_{hgnc_symbol}.csv")

    except requests.RequestException as e:
        logger.error(f"Error querying the API: {e}")
        print(f"Error querying the API: {e}")
    except ValueError as ve:
        logger.error(ve)
        print(ve)


if __name__ == "__main__":
    main()



## To do:
# get_response_gene() moved to panel_app_api_funtions.py - will need to write unit test for this
# record gene confidence status within a panel and display
# default to green only status?? option to also retrieve amber and red