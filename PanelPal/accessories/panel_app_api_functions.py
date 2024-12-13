"""
Module for interacting with the PanelApp API to extract gene information.

This module provides functions to interact with the PanelApp API, retrieve panel
information, and extract relevant details like gene names, panel names, and
versions. The module handles errors gracefully by raising custom exceptions
and providing detailed error messages.

Functions
---------
get_response(panel_id)
    Fetches JSON data from the PanelApp API for a given panel ID.
    Raises PanelAppError if the request fails or a specific error occurs.

get_name_version(response)
    Extracts the name, version, and primary key of the panel from the API
    response. Raises PanelAppError if there is an issue parsing the response.

get_genes(response)
    Extracts a list of gene symbols from the API response.
    Raises PanelAppError if there is an error parsing the response JSON or
    requests.exceptions.HTTPError if the response contains an error status code.

get_response_old_panel_version(panel_pk, version)
    Fetches the response from the PanelApp API for a specific panel and version.
    Raises PanelAppError if the request fails or returns an error status code.

Example Usage
-------------
>>> response = get_response('R293')
>>> panel_info = get_name_version(response)
>>> genes = get_genes(response)
OR
>>> response = get_response_old_panel_version(panel_pk, version)
>>> panel_info = get_name_version(response)
>>> genes = get_genes(response)

Notes
-----
This module requires the `requests` library to fetch data from the PanelApp API.
"""
import requests
from PanelPal.settings import get_logger

# Create a logger named after panel_app_api_functions
logger = get_logger(__name__)


class PanelAppError(Exception):
    """Custom exception for PanelApp errors."""


def get_response(panel_id):
    """
    Fetches JSON data for a given panel ID from the PanelApp API.

    Parameters
    ----------
    panel_id : str
        The ID of the panel, e.g., 'R293'.

    Returns
    -------
    requests.Response
        Response object from the API request.

    Raises
    ------
    PanelAppError
        If the request fails, times out, or if a specific error occurs (404, 500, etc.).
    """
    url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_id}"

    try:
        # Send the GET request to the API
        logger.info("Sending request to Panel App API for Panel %s", panel_id)
        response = requests.get(url, timeout=10)

        # Raise an exception for any non-2xx HTTP status codes
        response.raise_for_status()

        # If the request was successful, return the response object
        logger.info("Panel App API response successful for Panel %s", panel_id)
        return response

    # Handle errors if the API request times out
    except requests.exceptions.Timeout as e:
        # Log error if the API request times out
        logger.error("Request timed out while fetching panel data for Panel %s.", panel_id)
        # Raise a custom PanelAppError with a descriptive message
        raise PanelAppError(f"Timeout: Panel {panel_id} request exceeded the time limit. "
                            "Please try again.") from e

    except requests.exceptions.HTTPError as e:
        logger.error("HTTP Error occurred while fetching panel data for Panel %s: %s", panel_id, e)
        # Handle specific HTTP error codes
        if response.status_code == 404:
            # Raise a HTTP Error if 404 only - as this is likely user input error.
            raise requests.exceptions.HTTPError(f"404 Error: Panel {panel_id} not found.") from e
        else:
            # For other non-successful status codes, raise a general error
            raise PanelAppError(f"HTTP Error: {response.status_code} - {response.text}") from e

    except requests.exceptions.ConnectionError as e:
        # Catch connection errors
        logger.error("Connection Error while fetching panel data for Panel %s: %s", panel_id, e)
        # Reraise the error
        raise PanelAppError(f"Connection error retrieving data for panel {panel_id}.") from None

    except requests.exceptions.RequestException as e:
        # Catch all other types of request exceptions (network errors, etc.)
        logger.error("Error occurred while fetching panel data for Panel %s: %s", panel_id, e)
        # Raise a custom PanelAppError
        raise PanelAppError(f"Failed to retrieve data for panel {panel_id}.") from e
    


def get_name_version(response):
    """
    Extracts the panel name and version from the given API response.

    Parameters
    ----------
    response : requests.Response
        The response object returned from the PanelApp API.

    Returns
    -------
    dict
        A dictionary containing:
            - name (str): Panel name or 'N/A' if not found
            - version (str): Panel version or 'N/A' if not found
            - panel_pk (str): Panel primary key or 'N/A' if not found

    Raises
    ------
    PanelAppError
        If there is an issue parsing the response JSON.
    """
    try:
        # Parse the JSON data from the response
        data = response.json()

        # Extract the required fields, defaulting to 'N/A' if not found
        logger.info("Extracting data from JSON")
        return {
            "name": data.get("name", "N/A"),
            "version": data.get("version", "N/A"),
            "panel_pk": data.get("id", "N/A")
        }

    except ValueError as e:
        # Log any errors encountered while parsing the JSON data
        logger.error("Error parsing JSON: %s", e)
        # Raise a custom PanelAppError with a more descriptive message
        raise PanelAppError("Failed to parse panel data.") from e


def get_genes(response):
    """
    Extracts a list of gene symbols from the given API response.

    Parameters
    ----------
    response : requests.Response
        The response object returned from the PanelApp API.

    Returns
    -------
    list
        A list of HGNC symbols for each gene in the response data.

    Raises
    ------
    PanelAppError
        If there is an error parsing the response JSON.
    requests.exceptions.HTTPError
        If the response contains an error status code.
    """
    try:
        # Raise an exception for any non-2xx HTTP status codes
        response.raise_for_status()

        # Parse the JSON data from the response
        data = response.json()

        # Extract the gene symbols from the 'genes' key
        logger.info("Extracting data from JSON")
        return [gene["gene_data"]["gene_symbol"] for gene in data.get("genes", [])]

    except ValueError as e:
        # Log any errors encountered while parsing the JSON data
        logger.error("Error parsing JSON: %s", e)
        # Raise a custom PanelAppError with a more descriptive message
        raise PanelAppError("Failed to parse gene data.") from e

    except requests.exceptions.HTTPError as e:
        # Log any errors encountered during the request
        logger.error("Error fetching genes: %s", e)
        # Re-raise the exception, as it will be handled further up the call stack
        raise


def get_response_old_panel_version(panel_pk, version, panel):
    """
    Fetches the response from the PanelApp API for a specific panel and version.

    Parameters
    ----------
    panel_pk : str
        The Panel App database primary key for that panel.
    version : str
        The version of the panel to request from the API.

    Returns
    -------
    requests.Response
        The response object from the API request.

    Raises
    ------
    PanelAppError
        If the request fails, times out, or returns an error status code.
    """
    url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_pk}/?version={version}"

    try:
        # Send the GET request to the API
        logger.info("Sending request to Panel App API for Panel %s V%s", panel, version)
        response = requests.get(url, timeout=10)

        # Raise an exception for any non-2xx HTTP status codes
        response.raise_for_status()

        # If the request was successful, return the response object
        logger.info("Request to Panel App API was successful for Panel %s V%s", panel, version)
        return response

    # Handle errors if the API request times out
    except requests.exceptions.Timeout as e:
        # Log error if the API request times out
        logger.error("Request timed out while fetching panel data for Panel %s V%s", panel, version)
        # Raise a custom PanelAppError with a descriptive message
        raise PanelAppError (f"Timeout: Panel {panel_pk} request exceeded the time limit. "
                            "Please try again") from e

    except requests.exceptions.HTTPError as e:
        logger.error("HTTP Error occurred while fetching panel data for Panel %s: %s", panel, e)
        if response.status_code == 404:
            # Raise a HTTP Error if 404 only - as this is likely user input error.
            raise requests.exceptions.HTTPError(f"404 Error: Panel {panel} or Version {version} not found.") from e
        else:
            # For other non-successful status codes, raise a general error
            raise PanelAppError(f"HTTP Error: {response.status_code} - {response.text}") from e

    except requests.exceptions.RequestException as e:
        # Log any errors encountered during the request
        logger.error("Encountered a Request Exception")
        # Raise a custom PanelAppError
        raise PanelAppError (f"Failed to retrieve version {version} of panel {panel_pk}.") from e

def main():
    get_response("R233")

main()