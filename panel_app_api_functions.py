"""
Module for interacting with the PanelApp API to extract gene information and generate BED files.

This module provides functions to interact with the PanelApp API, retrieve panel information, and generate
a BED file that represents the location of genes in a given panel. The flow includes fetching data from the
API, extracting relevant details like gene names, versions, and chromosomal locations, and saving the result 
in a standard BED file format.

Functions:
    - get_response(panel_id): Fetches JSON data from the PanelApp API for a given panel ID.
    - get_name_version(response): Extracts the name and version of the panel from the API response.
    - get_genes(response): Extracts a list of gene symbols from the API response.
    - create_locus_dictionary(response, build): Generates a dictionary of gene Ensembl IDs and their chromosomal locations.
    - generate_bed(location_dict, panel_name): Generates a BED file from a dictionary of gene locations.

Example Usage:

    # Fetch the panel data for a given panel ID (e.g., 'R293')
    response = get_response('R293')
    
    # Extract the panel name and version from the response
    panel_info = get_name_version(response)
    
    # Extract the list of genes from the panel
    genes = get_genes(response)
    
    # Generate a locus dictionary mapping Ensembl gene IDs to chromosomal locations
    location_dict = create_locus_dictionary(response, 'GRCh37')
    
    # Generate the BED file from the locus dictionary
    generate_bed(location_dict, 'R293_panel')
    
This module requires the `requests` library to fetch data from the PanelApp API and interact with the response.
"""

import requests


def get_response(panel_id):
    """
    Fetches JSON data for a given panel ID from the PanelApp API.

    Parameters: 
    panel_id (str) – e.g., 'R293'.
    
    Returns: 
    dict – JSON data if successful.
    
    Raises: 
    Exception – if request fails.
    """
    url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response
    elif response.status_code == 404:
        raise Exception(f"Error: Panel {panel_id} not found.")
    elif response.status_code == 500:
        raise Exception("Server error: The server failed to process the request.")
    elif response.status_code == 503:
        raise Exception("Service unavailable: Please try again later.")
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")
    
    
def get_name_version(response):
    """
    Extracts the panel name and version from the given API response.

    Parameters: 
    response (requests.Response) – The response object returned from the PanelApp API.

    Returns: 
    dict – A dictionary containing the panel's 'name' and 'version'. If the data is missing, it returns 'N/A' for both.

    Raises:
    requests.exceptions.RequestException – If the response indicates a failure (e.g., 404, 500), the exception is raised.
    """
    try:
        # Ensure the response is successful (status code 200)
        response.raise_for_status()
        
        # Parse the JSON content from the response
        data = response.json()
        
        # Extract the 'name' and 'version' from the data, defaulting to 'N/A' if not found
        panel_name = data.get("name", "N/A")  # Default to 'N/A' if 'name' is missing
        panel_version = data.get("version", "N/A")  # Default to 'N/A' if 'version' is missing

        # Return a dictionary containing the extracted name and version
        return {
            "name": panel_name,
            "version": panel_version
        }

    except requests.exceptions.RequestException as e:
        # Catch any exceptions related to the request (e.g., network issues, invalid status codes)
        print(f"Error: {e}")
        
        # Return None if an error occurred, indicating failure to fetch or parse the data
        return None



def get_genes(response):
    """
    Extracts a list of gene symbols from the given API response.

    Parameters: 
    response (requests.Response) – The response object returned from the PanelApp API.

    Returns: 
    list – A list of gene symbols (strings). If no genes are found or an error occurs, an empty list is returned.

    Raises:
    requests.exceptions.RequestException – If the response indicates a failure (e.g., 404, 500), the exception is raised.
    """
    try:
        # Ensure the response is successful (status code 200)
        response.raise_for_status()

        # Parse the JSON content from the response
        data = response.json()

        # Extract gene symbols from the 'genes' field, defaulting to an empty list if 'genes' is missing
        genes = [gene["gene_data"]["gene_symbol"] for gene in data.get("genes", [])]

        # Return the list of gene symbols
        return genes

    except requests.exceptions.RequestException as e:
        # Catch any exceptions related to the request (e.g., network issues, invalid status codes)
        print(f"Error: {e}")
        
        # Return an empty list if an error occurred, indicating failure to fetch or parse the data
        return []



def create_locus_dictionary(response, build):
    """
    Creates a dictionary mapping gene Ensembl IDs to their chromosomal locations for a specific genome build.

    Parameters: 
    response (requests.Response) – The response object containing JSON data from the PanelApp API.
    build (str) – The chromosome build (e.g., 'GRCh37') used to extract the gene locations.

    Returns: 
    dict – A dictionary where keys are Ensembl gene IDs, and values are lists containing:
            [chromosome, start position, end position].
            Example:
            {
                'ENSG00000087460': ['20', '57414773', '57486247'],
                'ENSG00000113448': ['5', '58264865', '59817947']
            }

    Raises:
    requests.exceptions.RequestException – If the response indicates a failure (e.g., 404, 500), the exception is raised.
    """
    try:
        # Ensure the response is successful (status code 200)
        response.raise_for_status()
    
        # Parse the JSON content from the response
        data = response.json()
        
        # Extract the list of genes from the data
        genes = data.get("genes", [])
        
        # Initialize an empty dictionary to store gene locations
        location_dict = {}
        
        # Iterate over the list of genes to extract relevant information
        for gene in genes:
            # Retrieve the gene version for the given build (e.g., GRCh37)
            gene_version = gene["gene_data"]["ensembl_genes"].get(build, {})
            
            # If the version information is missing, skip this gene
            if not gene_version:
                continue
            
            # Retrieve the first available release for the gene version
            release = list(gene_version.keys())[0]  # Assumes the first release is the desired one
            
            # Extract the gene version data for the selected release
            gene_version = gene_version[release]
            
            # Split the location string (e.g., '20:57414773-57486247') into chromosome and position range
            chrom, position = gene_version["location"].split(":")
            start, end = position.split("-")
            
            # Store the gene's chromosomal coordinates in the dictionary
            coordinates = [chrom, start, end]
            location_dict[gene_version["ensembl_id"]] = coordinates
        
        # Return the dictionary of gene loci
        return location_dict
    
    except requests.exceptions.RequestException as e:
        # Print the error message if an exception occurs during the request
        print(f"Error: {e}")
        
        # Return an empty list as a fallback (indicating failure)
        return []



def generate_bed(location_dict, panel_name):
    """
    Generates a BED file from a dictionary of gene locations.

    Parameters:
    location_dict (dict) – A dictionary where keys are Ensembl gene IDs and values are lists containing:
                            [chromosome, start position, end position].
                            Example:
                            {
                                'ENSG00000087460': ['20', '57414773', '57486247'],
                                'ENSG00000113448': ['5', '58264865', '59817947']
                            }
    panel_name (str) – The name of the panel used for naming the output BED file.

    Returns:
    None – The function writes a BED file to disk with the given panel name.
    
    Output format:
    The generated BED file will contain tab-separated values with the following columns:
    - chromosome (e.g., 'chr20')
    - start position (0-based)
    - end position (1-based)
    - gene ID (e.g., Ensembl gene ID like 'ENSG00000087460')
    """
    
    # Create a filename for the BED file using the panel name
    output_file = panel_name + ".bed"
    
    try:
        # Open the output file for writing
        with open(output_file, 'w') as bed_file:
            # Iterate through the gene-location dictionary
            for gene_id, position in location_dict.items():
                # Extract chromosome and positions, adjusting start position to 0-based
                chromosome = "chr" + position[0]  # Add 'chr' prefix to chromosome
                start = int(position[1]) - 1  # Convert start position to 0-based indexing
                end = position[2]  # End position remains 1-based
                
                # Write each gene's data in BED format (tab-separated)
                bed_file.write(f"{chromosome}\t{start}\t{end}\t{gene_id}\n")
        
        # Print a success message with the output file's name
        print("BED file generated:", output_file)
    
    except IOError as e:
        # Handle any issues that arise while opening or writing to the file
        print(f"Error writing to file {output_file}: {e}")
