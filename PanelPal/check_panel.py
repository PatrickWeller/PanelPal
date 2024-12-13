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
from PanelPal.accessories.panel_app_api_functions import get_response, get_name_version
from PanelPal.accessories.panel_app_api_functions import PanelAppError
from PanelPal.settings import get_logger


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
    # Use regex to ensure the ID starts with 'R' followed by one or more digits
    # ^ start of string, R is literal 'R', \d+ means one or more digits, $ end of string
    return re.fullmatch(r"^R\d+$", input_id) is not None


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
    # Remove any leading/trailing white space, and convert to upper case
    panel_id = input_id.strip().upper()
    # Add R prefix if not already present
    if not panel_id.startswith("R"):
        panel_id = "R" + panel_id
    # Validate the formatted panel ID
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
        A dictionary containing the panel's 'name' and 'version',
        or an empty dictionary if retrieval fails after all retry attempts.

    Notes
    -----
    - Handles various API request exceptions with retry mechanism
    - Logs warnings and errors for different failure scenarios
    - Returns an empty dictionary if:
      - Connection errors persist
      - Request exceptions occur
      - Expected keys are missing in the response
    """
    # Attempt to fetchpanel information with try mechanism
    for attempt in range(1, retries + 1):
        try:
            # Retrieve API response
            response = get_response(formatted_id)
            # Extract name and version from response
            panel_info = get_name_version(response)

            # Validate that both 'name' and 'version' are present
            # Change this to be more strict about returning an empty dict
            if not panel_info or not all(key in panel_info for key in ["name", "version"]):
                logging.error(
                    "Incomplete panel information for panel %s",
                    formatted_id
                )
                return {}
            # Return the successfully retrieved panel information
            return panel_info

        except requests.exceptions.ConnectionError:
            # Log network connectivity issues
            logging.warning(
                "ConnectionError: Unable to reach API for panel %s, retrying in %d seconds...",
                formatted_id,
                delay,
            )
            # Retry if attempts remain, otherwise log error and return empty dictionary
            if attempt < retries:
                time.sleep(delay)
            else:
                logging.error(
                    "ConnectionError: Unable to reach API for panel %s after max retries. "
                    "Please check your network connection.",
                    formatted_id,
                )
                return {}

        except requests.exceptions.HTTPError:
            logging.error("404 Error: Panel with R code %s not found.", formatted_id)
            sys.exit(1)

        except (requests.exceptions.RequestException):
            # Handle other request-related exceptions (e.g. timeout)
            logging.warning(
                "Attempt %d/%d: Encountered an issue with the API for panel %s, "
                + "retrying in %d seconds...",
                attempt,
                retries,
                formatted_id,
                delay,
            )
            # Retry if attempts remain, otherwise log error and return empty dict
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
            # Handle cases where response is missing expected fields
            logging.error(
                "Unexpected API response for panel %s: Missing expected fields.",
                formatted_id,
            )
            # Return an empty dictionary
            return{}

    # If all retry attempts fail, return an empty dictionary
    raise PanelAppError from None


def main(panel_id=None):
    """
    Retrieve and display information for the given panel ID.

    If no `panel_id` is provided, the script parses it from command-line arguments.

    Parameters
    ----------
    panel_id : str, optional
        The panel ID to check. If not provided, it is parsed from arguments.

    """

    # Create a logger, named after this module, e.g. check_panel
    logger = get_logger(__name__)

    # Use command-line arguments if called from command-line.
    if panel_id is None:
        args = parse_arguments()
        panel_id = args.panel_id

    try:
        # Format panel ID to ensure correct format
        formatted_id = format_panel_id(panel_id)
        logger.debug("Formatted Panel ID: %s", formatted_id)

        # Fetch panel information
        panel_info = fetch_panel_info(formatted_id)

        # Print panel details if information is retrieved
        print(
            f"Panel ID: {formatted_id}\n"
            f"Clinical Indication: {panel_info['name']}\n"
            f"Latest Version: {panel_info['version']}"
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":  # pragma: no cover
    main()
