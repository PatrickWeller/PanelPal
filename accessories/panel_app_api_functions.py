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

get_old_gene_list(response)
    Extracts the HGNC symbols from the genes list in the API response.
    Raises PanelAppError if there is an error parsing the response JSON or
    accessing required data, and KeyError if the expected data structure is
    not found in the response.

Example Usage
-------------
>>> response = get_response('R293')
>>> panel_info = get_name_version(response)
>>> genes = get_genes(response)

Notes
-----
This module requires the `requests` library to fetch data from the PanelApp API.
"""
import logging
import requests

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PanelAppError(Exception):
    """Custom exception for PanelApp errors."""
    pass


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
        If the request fails or if a specific error occurs (404, 500, etc.).
    """
    url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_id}"
    
    try:
        # Send the GET request to the API
        response = requests.get(url)
        
        # Raise an exception for any non-2xx HTTP status codes
        response.raise_for_status()
        
        # If the request was successful, return the response object
        return response

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP error codes
        if response.status_code == 404:
            raise PanelAppError(f"Panel {panel_id} not found.") from e
        elif response.status_code == 500:
            raise PanelAppError("Server error: The server failed to process the request.") from e
        elif response.status_code == 503:
            raise PanelAppError("Service unavailable: Please try again later.") from e
        else:
            # For other non-successful status codes, raise a general error
            raise PanelAppError(f"Error: {response.status_code} - {response.text}") from e
            
    except requests.exceptions.RequestException as e:
        # Log any other request-related exceptions
        logging.error(f"Request failed: {e}")
        # Raise a custom PanelAppError with a more descriptive message
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
        return {
            "name": data.get("name", "N/A"),
            "version": data.get("version", "N/A"),
            "panel_pk": data.get("id", "N/A")
        }

    except ValueError as e:
        # Log any errors encountered while parsing the JSON data
        logging.error(f"Error parsing JSON: {e}")
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
        A list of gene symbols (strings).

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
        return [gene["gene_data"]["gene_symbol"] for gene in data.get("genes", [])]

    except ValueError as e:
        # Log any errors encountered while parsing the JSON data
        logging.error(f"Error parsing JSON: {e}")
        # Raise a custom PanelAppError with a more descriptive message
        raise PanelAppError("Failed to parse gene data.") from e

    except requests.exceptions.HTTPError as e:
        # Log any errors encountered during the request
        logging.error(f"Error fetching genes: {e}")
        # Re-raise the exception, as it will be handled further up the call stack
        raise


def get_response_old_panel_version(panel_pk, version):
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
        If the request fails or returns an error status code.
    """
    url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_pk}/?version={version}"
    
    try:
        # Send the GET request to the API
        response = requests.get(url)
        
        # Raise an exception for any non-2xx HTTP status codes
        response.raise_for_status()
        
        # If the request was successful, return the response object
        return response

    except requests.exceptions.RequestException as e:
        # Log any errors encountered during the request
        logging.error(f"Error fetching old panel version: {e}")
        # Raise a custom PanelAppError with a more descriptive message
        raise PanelAppError(f"Failed to retrieve version {version} of panel {panel_pk}.") from e


def get_old_gene_list(response):
    """
    Extracts the HGNC symbols from the genes list in the API response.

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
        If there is an error parsing the response JSON or accessing required data.
    KeyError
        If the expected data structure is not found in the response.
    """
    try:
        # Parse the JSON data from the response
        data = response.json()
        
        # Extract the HGNC symbols from the 'genes' data
        return [gene['gene_data']['hgnc_symbol'] for gene in data["genes"]]

    except ValueError as e:
        # Log any errors encountered while parsing the JSON data
        logging.error(f"Error parsing gene list JSON: {e}")
        # Raise a custom PanelAppError with a more descriptive message
        raise PanelAppError("Failed to parse gene list data.") from e
        
    except KeyError as e:
        # Log any missing required data in the response
        logging.error(f"Missing required data in response: {e}")
        # Raise a custom PanelAppError with a more descriptive message
        raise PanelAppError("Response missing required gene data.") from e


def main():
    response = get_response_old_panel_version(562, 1.6)
    print(get_old_gene_list(response))

if __name__ == "__main__":
    main()