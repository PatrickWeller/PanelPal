#!/usr/bin/env python

"""
Script to query PanelApp for gene information and retrieve associated panels.

Parameters
---------- 
hgnc_symbol : str
    The HGNC symbol of the gene to query (e.g., BRCA1).
confidence_status : str
    Filter for panels by confidence status. Defaults to "green".
show_all_panels : bool
    Whether to include panels without R codes. Defaults to False.

Example
-------
Run the script from the command line:
    $ python gene_to_panels.py --hgnc_symbol BRCA1 --confidence_status green  --show_all_panels

This will return a list of panels containing the gene BRCA1 with a confidence status of 'green'.

"""

import argparse
import re
import requests
import pandas as pd
from .settings import get_logger
from .accessories.panel_app_api_functions import get_response_gene


def parse_arguments():
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Query PanelApp for gene information and retrieve associated panels.",
        epilog="Example usage: python gene_to_panels.py --hgnc_symbol BRCA1 "
        "--confidence_status green",
    )
    parser.add_argument(
        "--hgnc_symbol",
        type=str,
        help="The HGNC symbol of the gene to query (e.g., BRCA1). This is a required argument.",
        required=True,
    )
    parser.add_argument(
        "--confidence_status",
        type=str,
        default="green",
        choices=["red", "amber", "green", "all", "green,amber"],
        help=(
            "Filter panels by confidence status. Choices are 'red', 'amber', "
            "'green', 'all', or 'green,amber'. Defaults to 'green'."
        ),
    )
    parser.add_argument(
        "--show_all_panels",
        action="store_true",
        help="Include panels without R codes in the output.",
    )
    return parser.parse_args()


def confidence_to_colour(level):
    """
    Convert numerical confidence levels to colour codes.

    Parameters
    ----------
    level : int or str
        Confidence level as an integer or string.

    Returns
    -------
    str
        Corresponding colour code: 'red', 'amber', or 'green'.
    """
    mapping = {
        "1": "red",
        "2": "amber",
        "3": "green",
    }
    # Default to 'unknown' for unexpected values
    return mapping.get(str(level), "unknown")


def extract_panels(response_json, confidence_filter="green"):
    """
    Extract panel IDs and names from the API response JSON, filtered by confidence status.

    Parameters
    ----------
    response_json : dict
        The parsed JSON response from the API.
    confidence_filter : str
        Filter for confidence level ('red', 'amber', 'green', 'all').

    Returns
    -------
    pd.DataFrame
        A DataFrame containing panel information filtered by confidence level.
    """
    panels = []
    for result in response_json.get("results", []):
        panel = result.get("panel")
        confidence = result.get("confidence_level")
        confidence_colour = confidence_to_colour(confidence)

        # Apply confidence filter if not 'all'
        if confidence_filter not in {"all", confidence_colour}:
            continue

        if panel:
            panel_id = panel.get("id")
            panel_name = panel.get("name")
            relevant_disorders = panel.get("relevant_disorders")
            panels.append(
                {
                    "PanelApp ID": panel_id,
                    "Panel Name": panel_name,
                    "Relevant Disorders": (
                        ", ".join(relevant_disorders)
                        if isinstance(relevant_disorders, list)
                        else relevant_disorders
                    ),
                    "Gene Status": confidence_colour,
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


def extract_r_codes_from_disorders(panels_df, show_all_panels=False):
    """
    Add an 'R Code' column to the panels DataFrame by extracting R codes.

    Parameters
    ----------
    panels_df : pd.DataFrame
        The DataFrame containing panel information with a 'Relevant Disorders' column.
    show_all_panels : bool, optional
        Whether to include panels without R codes. Defaults to False.

    Returns
    -------
    pd.DataFrame
        A DataFrame with an added 'R Code' column where extracted R codes are listed.
    """
    panels_df = panels_df.copy()  # Ensure we are working with a copy
    panels_df["R Code"] = panels_df["Relevant Disorders"].apply(extract_r_codes)
    if not show_all_panels:
        panels_df = panels_df[panels_df["R Code"] != "N/A"]
    return panels_df


def write_panels(hgnc_symbol, confidence_status, df):
    """
    Write panel data to a CSV file.

    Parameters
    ----------
    hgnc_symbol : str
        The queried gene symbol.
    df : pd.DataFrame
        The DataFrame containing panel information.

    Returns
    -------
    None
    """
    confidence_status = confidence_status.replace(",", "_")
    output_file = f"panels_containing_{hgnc_symbol}_{confidence_status}.tsv"
    df.to_csv(
        output_file,
        columns=["PanelApp ID", "R Code", "Panel Name", "Gene Status"],
        header=["panelapp_id", "r_code", "panel_name", "gene_status"],
        index=False,
        sep="\t",
    )
    print(f"\nPanel list saved to: {output_file}")


def process_panels(response_json, confidence_statuses, show_all_panels):
    """
    Process the panels from the API response JSON.

    Parameters
    ----------
    response_json : dict
        The parsed JSON response from the API.
    confidence_statuses : list of str
        List of confidence statuses to filter the panels.
    show_all_panels : bool
        Whether to include panels without R codes.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the processed panels.
    """
    panels_df_list = [
        extract_panels(response_json, confidence_filter=status)
        for status in confidence_statuses
    ]
    panels_df = pd.concat(panels_df_list).drop_duplicates().reset_index(drop=True)
    if panels_df.empty:
        return pd.DataFrame()

    panels_with_r_codes = extract_r_codes_from_disorders(panels_df, show_all_panels)
    panels_with_r_codes["R Code"] = panels_with_r_codes["R Code"].replace("N/A", "-")
    return panels_with_r_codes


def log_and_print_command(hgnc_symbol, confidence_status, show_all_panels):
    """
    Log and print the executed command.

    Parameters
    ----------
    hgnc_symbol : str
        The HGNC symbol of the gene to query.
    confidence_status : str
        The confidence status filter.
    show_all_panels : bool
        Whether to include panels without R codes.

    Returns
    -------
    None
    """
    command_executed = (
        f"Command executed: gene-panels --hgnc_symbol {hgnc_symbol} "
        f"--confidence_status {confidence_status} --show_all_panels {show_all_panels}"
    )
    logger = get_logger(__name__)
    logger.info(command_executed)
    print(f"{command_executed}\n")


def log_and_print_no_panels(hgnc_symbol, confidence_status):
    """
    Log and print the message when no panels are found.

    Parameters
    ----------
    hgnc_symbol : str
        The HGNC symbol of the gene to query.
    confidence_status : str
        The confidence status filter.

    Returns
    -------
    None
    """
    logger = get_logger(__name__)
    logger.info(
        "No panels found for gene %s with confidence: %s.",
        hgnc_symbol,
        confidence_status,
    )
    print(
        f"No panels found for gene {hgnc_symbol} with confidence: {confidence_status}."
    )


def display_panels(hgnc_symbol, panels_with_r_codes):
    """
    Display the panels associated with the gene.

    Parameters
    ----------
    hgnc_symbol : str
        The HGNC symbol of the gene to query.
    panels_with_r_codes : pd.DataFrame
        DataFrame containing the panels with R codes.

    Returns
    -------
    None
    """
    print(f"Panels associated with gene {hgnc_symbol}:\n")
    print(f"{'PanelApp ID':<15}{'R Code':<15}{'Panel Name':<75}{'Gene Status'}")
    print("-" * 120)

    for _, row in panels_with_r_codes.iterrows():
        panel_id = row["PanelApp ID"]
        r_code = row["R Code"]
        panel_name = row["Panel Name"]
        status = row["Gene Status"]
        print(f"{panel_id:<15}{r_code:<15}{panel_name:<75}{status}")


def main(hgnc_symbol=None, confidence_status="green", show_all_panels=False):
    """
    Main function to query PanelApp for gene information and display associated panels.

    Parameters
    ----------
    hgnc_symbol : str, optional
        The HGNC symbol of the gene to query (e.g., BRCA1). If not provided, the function
        parses command-line arguments to retrieve it.
    confidence_status : str, optional
        Filter for panels by confidence status. Defaults to "green".
    show_all_panels : bool, optional
        Whether to include panels without R codes. Defaults to False.

    Returns
    -------
    None
    """
    logger = get_logger(__name__)

    if hgnc_symbol is None:
        args = parse_arguments()
        hgnc_symbol = args.hgnc_symbol
        confidence_status = args.confidence_status
        show_all_panels = args.show_all_panels

    log_and_print_command(hgnc_symbol, confidence_status, show_all_panels)

    if confidence_status == "green,amber":
        confidence_statuses = ["green", "amber"]
    else:
        confidence_statuses = [confidence_status]

    try:
        logger.info("Querying PanelApp API for gene: %s", hgnc_symbol)
        response = get_response_gene(hgnc_symbol)
        response_json = response.json()

        panels_with_r_codes = process_panels(
            response_json, confidence_statuses, show_all_panels
        )
        if panels_with_r_codes.empty:
            log_and_print_no_panels(hgnc_symbol, confidence_status)
            return

        display_panels(hgnc_symbol, panels_with_r_codes)
        write_panels(hgnc_symbol, confidence_status, panels_with_r_codes)

    except requests.RequestException as e:
        logger.error("Error querying the API: %s", e)
        print(f"Error querying the API: {e}")
    except KeyError as ke:
        logger.error("Key error: %s", ke)
        print(f"Key error: {ke}")
        print(ke)


if __name__ == "__main__":
    main()
