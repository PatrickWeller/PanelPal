"""
This module provides functionality for fetching gene transcript data, 
extracting exon information, generating BED files, and merging genomic regions 
using bedtools. It is designed to work with Variant Validator's API to 
retrieve gene-to-transcript mapping data, which is outputted in BED format.

Functions
---------
- get_gene_transcript_data
    Fetches gene transcript data from the Variant Validator API.
- extract_exon_info
    Extracts exon-related information from the fetched gene transcript data.
- generate_bed_file
    Generates a BED file from a list of genes and their exon data.
- bedtools_merge
    Sorts and merges overlapping regions in a BED file using bedtools.

Dependencies
------------
- requests
    For making HTTP requests to the Variant Validator API.
- subprocess
    For executing bedtools commands to sort and merge BED files.
- time
    For handling retry logic and wait times between requests.
- logging
    For logging the progress and errors in the operations.

Example Usage
-------------
>>> gene_list = ["BRCA1", "BRCA2", "XRCC2"]
>>> panel_name = "R207"
>>> panel_version = "4"
>>> genome_build = "GRCh38"
>>> generate_bed_file(gene_list, panel_name, panel_version, genome_build)
>>> bedtools_merge(panel_name, panel_version, genome_build)
"""

import requests
import time
import subprocess
import logging
from settings import get_logger

# Create a logger named after variant_validator_api_functions
logger = get_logger(__name__)


def get_gene_transcript_data(gene_name, genome_build="GRCh38", max_retries=4, wait_time=2):
    """
    Fetches the gene transcript data for a given gene from the Variant Validator API.

    Arguments:
        gene_name (str): The name of the gene to fetch transcript data for.
        genome_build (str, optional): The genome build to use (default is "GRCh38").
        max_retries (int, optional): Max number of retries when rate limit is exceeded (error 429).
        wait_time (int, optional): Fixed wait time (in seconds) between requests (default: 2).

    Returns:
        dict: The JSON response containing gene transcript information.

    Raises:
        Exception: If the request to the API fails (status code not 200).
    """
    # Base URL for the Variant Validator API endpoint
    base_url = "https://rest.variantvalidator.org/VariantValidator/tools/gene2transcripts_v2/"
    
    # Construct the URL with the given gene name and genome build
    url = f"{base_url}/{gene_name}/mane_select/refseq/{genome_build}?content-type=application%2Fjson"

    retries = 0

    while retries < max_retries:
        logging.info("Fetching data for %s (Attempt %d)", gene_name, retries + 1)

        # Send the GET request to the Variant Validator API
        response = requests.get(url)

        if response.status_code == 200:  # success
            logging.info("Data for %s fetched successfully.", gene_name)
            return response.json()  # return JSON content from API response

        elif response.status_code == 429:  # Rate limit exceeded
            backoff_time = 2 ** retries  # Exponential backoff for retries
            logging.warning("Rate limit exceeded for %s. Retrying in %d seconds.", gene_name, backoff_time)
            time.sleep(backoff_time)
            retries += 1

        else:  # Other errors
            logging.error("Failed to fetch gene data for %s: %d", gene_name, response.status_code)
            raise Exception(f"HTTP {response.status_code}: Failed to fetch data for {gene_name}.")

        # Fixed wait between requests to reduce likelihood of hitting rate limits
        logging.info("Waiting for %d seconds before the next request.", wait_time)
        time.sleep(wait_time)

    # Exception if max retries are exceeded
    logging.error("Max retries reached for %s. The number of retries may need increasing.", gene_name)
    raise Exception(f"Max retries reached for {gene_name}. Terminating.")


def extract_exon_info(gene_transcript_data):
    """
    Extracts exon information from the gene transcript data.

    Args:
        gene_transcript_data (dict): The JSON response containing the gene transcript data.

    Returns:
        list: A list containing exon data.
    """
    exon_data = []  # Initialize an empty list to store exon data as dictionaries

    # Loop through each gene in the transcript data
    for gene_data in gene_transcript_data:        
        # Loop through each transcript associated with the gene
        for transcript in gene_data['transcripts']:
            # Extract chromosome information from the transcript
            chromosome = transcript['annotations'].get('chromosome', 'Unknown')

            # Extract the reference transcript information
            transcript_reference = transcript.get('reference', 'Unknown')

            # Extract the gene symbol
            gene_symbol = gene_data.get('current_symbol', 'Unknown')

            # Loop through the genomic spans in the transcript (exon structures)
            for genomic_span_key, genomic_span in transcript['genomic_spans'].items():
                if 'exon_structure' in genomic_span:  # Ensure 'exon_structure' exists before accessing it
                    for exon in genomic_span['exon_structure']:
                        # Extract exon-specific information such as exon number, start, and end positions
                        exon_number = exon.get('exon_number', None)
                        exon_start = exon.get('genomic_start', None)
                        exon_end = exon.get('genomic_end', None)

                        # Store the extracted exon data in a dictionary
                        exon_info = {
                            "chromosome": chromosome,
                            "exon_start": exon_start,
                            "exon_end": exon_end,
                            "exon_number": exon_number,
                            "reference": transcript_reference,
                            "gene_symbol": gene_symbol
                        }
                        
                        # Append the exon data to the list of exon_data
                        exon_data.append(exon_info)

    logging.info("Extracted %d exons for the gene.", len(exon_data))

    # Return the complete list of exon data
    return exon_data


def generate_bed_file(gene_list, panel_name, panel_version, genome_build="GRCh38"):
    """
    Generates a BED file containing exon data for a list of genes.
    Uses GRCh38 by default.

    Args:
        gene_list (list): A list of gene names for which exon data is to be extracted.
        panel_name (str): The name of the panel, used to name the output BED file.
        genome_build (str): The genome build, used to name the output BED file.

    Returns:
        None: This directly writes to a BED file.
    """
    # Define the name of the output BED file based on the panel name and genome build
    output_file = f"{panel_name}_v{panel_version}_{genome_build}.bed"
    logging.info("Creating BED file: %s", output_file)

    # Open the BED file for writing (or create it if it doesn't exist)
    with open(output_file, 'w') as bed_file:
        # Iterate over the list of genes to fetch and process their transcript data
        for gene in gene_list:

            try:
                # Fetch the transcript data for the current gene using the API
                gene_transcript_data = get_gene_transcript_data(gene, genome_build)

                # Extract the exon information from the retrieved transcript data
                exon_data = extract_exon_info(gene_transcript_data)

                # Write the extracted exon information to the BED file
                for exon in exon_data:
                    # Subtract 1 to zero-index the start position
                    exon["exon_start"] -= 1

                    # Add padding of 10bp on either side
                    exon["exon_start"] = max(0, exon["exon_start"] - 10)  # Avoid negative start positions
                    exon["exon_end"] += 10

                    # Concatenate exon number, reference, and gene symbol in one column
                    concat_info = f"{exon['exon_number']}|{exon['reference']}|{exon['gene_symbol']}"

                    # Each line in the BED file corresponds to an exon and its relevant details
                    bed_file.write(f"{exon['chromosome']}\t{exon['exon_start']}\t{exon['exon_end']}\t{concat_info}\n")

                # log addition of exon data for each gene    
                logging.info("Added exon data for %s to the BED file.", gene)
        
            except Exception as e:
                logging.error("Error processing %s: %s", gene, e)

        # log message indicating that BED file has been successfully saved
        logging.info("Data saved to %s", output_file)


def bedtools_merge(panel_name, panel_version, genome_build):
    """
    Sorts and merges overlapping regions in a BED file generated by generate_bed_file.

    Args:
        panel_name (str): Name of the genomic panel.
        panel_version (str): Version of the genomic panel.
        genome_build (str): Genome build identifier (e.g., "GRCh38").

    Returns:
        None: Creates a merged BED file (e.g., `R59_v2_merged.bed`) in the same directory.

    Dependencies:
        Requires bedtools (available in PanelPal conda environment).

    """

    # Define the input and output file names based on parameters
    bed_file = f"{panel_name}_v{panel_version}_{genome_build}.bed"
    merged_bed_file = f"{panel_name}_v{panel_version}_{genome_build}_merged.bed"

    # Try running bedtools merge
    try:
        merge_command = f"bedtools sort -i {bed_file} | bedtools merge > {merged_bed_file}"
        subprocess.run(merge_command, shell=True, check=True)
        logging.info("Successfully sorted and merged BED file to %s", merged_bed_file)

    # If an error is encountered log the error
    except subprocess.CalledProcessError as e:
        logging.error("Error during bedtools operation: %s", e)


def main():
    """
    Dummy variables for testing purposes.
    """
    # Set panel id and version
    panel_name = "R207"
    panel_version = "4"
    gene_list = [
        "BRCA1","BRCA2","BRIP1","MLH1","MSH2","MSH6","PALB2","RAD51C","RAD51D","PMS2",
        "AR","ATM","BARD1","CDH1","CHEK2","EPCAM","ESR1","MUTYH","NBN","PPM1D","PTEN",
        "RAD54L","RRAS2","STK11","TP53","XRCC2"
        ]
    genome_build = "GRCh38"

    # Generate bed files
    generate_bed_file(gene_list, panel_name, panel_version, genome_build)
    bedtools_merge(panel_name, panel_version, genome_build)

if __name__ == "__main__":
    main()