#!/usr/bin/env python

"""
Script to check and retrieve panel information from the PanelApp API.

This script allows users to query panel information based on a panel ID.
It validates the panel ID, formats it, and then fetches information from the
PanelApp API. The retrieved data includes the panel's clinical indication and version.
Error handling is implemented for network failures, invalid input, and unexpected responses.
"""

import argparse
import re
import time
import logging
import requests
import sys
from accessories.panel_app_api_functions import get_response, get_name_version
from settings import get_logger


def parse_arguments():
    """
    Parse the panel ID argument from the command line.

    Returns
    -------
    argparse.Namespace
        Parsed arguments with the 'panel_id' attribute.
    """
    parser = argparse.ArgumentParser(
        description="Check and retrieve panel information."
    )
    parser.add_argument(
        "--panel_id",
        type=str,
        help="The ID of the panel to query (e.g., R59).",
        required=True,
    )
    return parser.parse_args()


def is_valid_panel_id(input_id):
    """
    Validate the panel ID format (e.g., 'R59').

    Parameters
    ----------
    input_id : str
        The panel ID to check.

    Returns
    -------
    bool
        True if the ID is valid, False otherwise.
    """
    return re.fullmatch(r"R\d+$", input_id) is not None


def format_panel_id(input_id):
    """
    Format and validate the panel ID (e.g., "59" → "R59").

    Parameters
    ----------
    input_id : str
        The panel ID to format.

    Returns
    -------
    str
        The correctly formatted panel ID.

    Raises
    ------
    ValueError
        If the ID format is invalid.
    """
    panel_id = input_id.strip().upper()
    if not panel_id.startswith("R"):
        panel_id = "R" + panel_id
    if not is_valid_panel_id(panel_id):
        raise ValueError("Panel ID must be 'R' followed by digits (e.g., 'R59').")
    return panel_id


def fetch_panel_info(formatted_id, retries=3, delay=10):
    """
    Fetch panel information (name and version) from the API with retry logic.

    Parameters
    ----------
    formatted_id : str
        The formatted panel ID (e.g., "R59").
    retries : int, optional
        Number of retry attempts (default is 3).
    delay : int, optional
        Delay between retries in seconds (default is 10).

    Returns
    -------
    dict
        A dictionary containing the panel's 'name' and 'version'.

    Raises
    ------
    RuntimeError
        If the API request fails after retries.
    KeyError
        If expected keys ('name', 'version') are missing in the response.
    """
    for attempt in range(1, retries + 1):
        try:
            response = get_response(formatted_id)
            panel_info = get_name_version(response)

            missing_keys = [key for key in ["name", "version"] if key not in panel_info]
            if missing_keys:
                raise KeyError

            return panel_info

        except requests.exceptions.ConnectionError:
            logging.warning(
                "ConnectionError: Unable to reach API for panel %s, retrying in %d seconds...",
                formatted_id,
                delay,
            )
            if attempt < retries:
                time.sleep(delay)
            else:
                logging.error(
                    "ConnectionError: Unable to reach API for panel %s after max retries. "
                    "Please check your network connection.",
                    formatted_id,
                )
                return {}

        except requests.exceptions.RequestException:
            logging.warning(
                "Attempt %d/%d: Encountered an issue with the API for panel %s, "
                + "retrying in %d seconds...",
                attempt,
                retries,
                formatted_id,
                delay,
            )
            if attempt < retries:
                time.sleep(delay)
            else:
                logging.error(
                    "RequestException: API request failed for panel %s. "
                    + "Check the network or API status.",
                    formatted_id,
                )
                return {}

        except KeyError:
            logging.error(
                "Unexpected API response for panel %s: Missing expected fields.",
                formatted_id,
            )
            return {}

    return {}


def main(panel_id=None):
    """
    Retrieve and display information for the given panel ID.

    If no `panel_id` is provided, the script parses it from command-line arguments.

    Parameters
    ----------
    panel_id : str, optional
        The panel ID to check. If not provided, it is parsed from arguments.

    Raises
    ------
    ValueError
        If the panel ID is invalid or doesn't follow the correct format.
    KeyError
        If the API response is missing expected keys ('name' or 'version').
    RuntimeError
        If the API request fails after multiple attempts or encounters network issues.
    Exception
        For any other unexpected errors.
    """

    # Create a logger, named after this module, e.g. check_panel
    logger = get_logger(__name__)

    if panel_id is None:
        args = parse_arguments()
        panel_id = args.panel_id

    try:
        formatted_id = format_panel_id(panel_id)
        logger.debug("Formatted Panel ID: %s", formatted_id)

        panel_info = fetch_panel_info(formatted_id)

        print(
            f"Panel ID: {formatted_id}\n"
            f"Clinical Indication: {panel_info['name']}\n"
            f"Latest Version: {panel_info['version']}"
        )

    except Exception:
        sys.exit()


if __name__ == "__main__":  # pragma: no cover
    main()
