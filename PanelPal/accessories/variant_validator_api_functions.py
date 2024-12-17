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
import sys
import os
import time
import subprocess
import requests
from PanelPal.settings import get_logger

logger = get_logger(__name__)

# Define directory to store bed files in
BED_DIRECTORY = "bed_files"
# Create directory if it doesn't exist
if not os.path.exists(BED_DIRECTORY):
    os.makedirs(BED_DIRECTORY)


def get_gene_transcript_data(
    gene_name, genome_build="GRCh38", max_retries=6, wait_time=2
):
    """
    Fetches the gene transcript data for a given gene from the Variant Validator API.

    Parameters
    ----------
    gene_name : str
        The name of the gene to fetch transcript data for.
    genome_build : str, optional
        The genome build to use (default is "GRCh38").
    max_retries : int, optional
        Max number of retries when rate limit is exceeded (error 429).
    wait_time : int, optional
        Fixed wait time (in seconds) between requests (default is 2).

    Returns
    -------
    dict
        The JSON response containing gene transcript information.

    Raises
    ------
    Exception
        If the request to the API fails (status code not 200).
    """
    # Base URL for the Variant Validator API endpoint
    base_url = (
        "https://rest.variantvalidator.org/VariantValidator/tools/gene2transcripts_v2/"
    )

    if genome_build not in ["GRCh37", "GRCh38", "all"]:
        logger.error(
            "Genome build %s is not valid input. Please use GRCh37 or GRCh38", genome_build
        )
        raise ValueError(
            f"{genome_build} is not a valid genome build. Use GRCh37 or GRCh38.")

    # Construct the URL with the given gene name and genome build
    url = (
        f"{base_url}/{gene_name}/mane_select/refseq/{genome_build}"
        "?content-type=application%2Fjson"
    )

    retries = 0

    while retries < max_retries:
        logger.info("Fetching data for %s (Attempt %d)",
                    gene_name, retries + 1)

        # Send the GET request to the Variant Validator API
        response = requests.get(url, timeout=20)

        # Raise HTTPError if the response code is 4xx or 5xx
        response.raise_for_status()

        if response.status_code == 200:  # success
            logger.info("Data for %s fetched successfully.", gene_name)
            return response.json()  # return JSON content from API response

        if response.status_code == 429:  # Rate limit exceeded
            backoff_time = 2**retries  # Exponential backoff for retries
            logger.warning(
                "Rate limit exceeded for %s. Retrying in %d seconds.",
                gene_name,
                backoff_time,
            )
            time.sleep(backoff_time)
            retries += 1

        else:  # Other errors
            logger.error(
                "Failed to fetch gene data for %s: %d", gene_name, response.status_code
            )
            raise requests.exceptions.RequestException(
                f"HTTP {response.status_code}: Failed to fetch data for {
                    gene_name}."
            )

        # Fixed wait between requests to reduce likelihood of hitting rate limits
        logger.info(
            "Waiting for %d seconds before the next request.", wait_time)
        time.sleep(wait_time)

    # Exception if max retries are exceeded
    logger.error(
        "Max retries reached for %s. The number of retries may need increasing.",
        gene_name,
    )
    raise requests.exceptions.RequestException(
        f"Max retries reached for {gene_name}. Terminating."
    )


def extract_exon_info(gene_transcript_data):
    """
    This function extracts exon data from genomic spans associated with transcripts. It assumes
    the presence of specific fields such as "exon_structure" in the input data.

    Parameters
    ----------
    gene_transcript_data : dict
        The JSON response containing the gene transcript data.

    Returns
    -------
    list
        A list containing exon data. Each entry is a dictionary with the following keys:
        - "chromosome" : str
            The chromosome of the exon.
        - "exon_start" : int or None
            The start position of the exon.
        - "exon_end" : int or None
            The end position of the exon.
        - "exon_number" : int or None
            The exon number.
        - "reference" : str
            The reference transcript.
        - "gene_symbol" : str
            The gene symbol.

    """
    exon_data = []  # Initialize an empty list to store exon data as dictionaries

    # Loop through each gene in the transcript data
    for gene_data in gene_transcript_data:
        # Loop through each transcript associated with the gene
        for transcript in gene_data["transcripts"]:
            # Extract chromosome information from the transcript
            chromosome = transcript["annotations"].get("chromosome", "Unknown")

            # Extract the reference transcript information
            transcript_reference = transcript.get("reference", "Unknown")

            # Extract the gene symbol
            gene_symbol = gene_data.get("current_symbol", "Unknown")

            # Loop through the genomic spans in the transcript (exon structures)
            for genomic_span in transcript["genomic_spans"].items():
                if (
                    # Ensure 'exon_structure' exists before accessing it
                    # Access the value part of the tuple, containing exon_structure
                    "exon_structure"
                    in genomic_span[1]
                ):
                    for exon in genomic_span[1]["exon_structure"]:
                        # Extract exon-specific information: EX number, start, and end positions
                        exon_number = exon.get("exon_number", None)
                        exon_start = exon.get("genomic_start", None)
                        exon_end = exon.get("genomic_end", None)

                        # Store the extracted exon data in a dictionary
                        exon_info = {
                            "chromosome": chromosome,
                            "exon_start": exon_start,
                            "exon_end": exon_end,
                            "exon_number": exon_number,
                            "reference": transcript_reference,
                            "gene_symbol": gene_symbol,
                        }

                        # Append the exon data to the list of exon_data
                        exon_data.append(exon_info)

    logger.info("Extracted %d exons for the gene.", len(exon_data))

    # Return the complete list of exon data
    return exon_data


def generate_bed_file(gene_list, panel_name, panel_version, genome_build="GRCh38"):
    """
    This function generates a BED file that includes exon data for each gene in the provided
    list. The exons are padded with 10 base pairs on either side, and additional exon details
    such as exon number, reference, and gene symbol are concatenated into one field.

    Parameters
    ----------
    gene_list : list
        A list of gene names for which exon data is to be extracted.
    panel_name : str
        The name of the panel, used to name the output BED file.
    panel_version : str
        The version of the panel, used to name the output BED file.
    genome_build : str, optional
        The genome build (default is "GRCh38"). It is used to name the output BED file.

    Returns
    -------
    None
        This function directly writes to a BED file. The output file will be named based on
        the panel name, version, and genome build.

    Raises
    ------
    requests.exceptions.RequestException
        If there is an error while fetching the transcript data for any gene.
    """
    # Define the name of the output BED file based on the panel name and genome build
    output_file = os.path.join(BED_DIRECTORY, f"{panel_name}_v{
                               panel_version}_{genome_build}.bed")
    logger.info("Creating BED file: %s", output_file)

    # Open the BED file for writing (or create it if it doesn't exist)
    with open(output_file, "w", encoding="utf-8") as bed_file:
        # Iterate over the list of genes to fetch and process their transcript data
        for gene in gene_list:

            try:
                # Fetch the transcript data for the current gene using the API
                gene_transcript_data = get_gene_transcript_data(
                    gene, genome_build)

                # Extract the exon information from the retrieved transcript data
                exon_data = extract_exon_info(gene_transcript_data)

                # Write the extracted exon information to the BED file
                for exon in exon_data:
                    # Subtract 1 to zero-index the start position
                    exon["exon_start"] -= 1

                    # Add padding of 10bp on either side
                    # Avoid negative start positions
                    exon["exon_start"] = max(0, exon["exon_start"] - 10)
                    exon["exon_end"] += 10

                    # Concatenate exon number, reference, and gene symbol in one column
                    concat_info = f"{exon['exon_number']}|{
                        exon['reference']}|{exon['gene_symbol']}"

                    # Each line in the BED file corresponds to an exon and its relevant details
                    bed_file.write(
                        f"{exon['chromosome']}\t"
                        f"{exon['exon_start']}\t"
                        f"{exon['exon_end']}\t"
                        f"{concat_info}\n"
                    )

                # log addition of exon data for each gene
                logger.info("Added exon data for %s to the BED file.", gene)

            except Exception as e:
                logger.error("Error processing %s: %s", gene, e)
                sys.exit(f"Error processing {gene}: {e}")

        # log message indicating that BED file has been successfully saved
        logger.info("Data saved to %s", output_file)


def bedtools_merge(panel_name, panel_version, genome_build):
    """
    Sorts and merges overlapping regions in a BED file generated by generate_bed_file.

    Parameters
    ----------
    panel_name : str
        The name of the genomic panel.
    panel_version : str
        The version of the genomic panel.
    genome_build : str
        The genome build identifier (e.g., "GRCh38").

    Returns
    -------
    None
        This function creates a merged BED file (e.g., `R59_v2_merged.bed`) in the same directory.

    Raises
    ------
    subprocess.CalledProcessError
        If an error occurs during the bedtools operation.

    Dependencies
    ------------
        Requires bedtools (available in PanelPal conda environment).

    """

    # Define the input and output file names based on parameters
    bed_file = os.path.join(BED_DIRECTORY, f"{panel_name}_v{
                            panel_version}_{genome_build}.bed")
    merged_bed_file = os.path.join(BED_DIRECTORY, f"{panel_name}_v{
                                   panel_version}_{genome_build}_merged.bed")

    # Try running bedtools merge
    try:
        merge_command = (
            f"bedtools sort -i {bed_file} | bedtools merge > {merged_bed_file}"
        )
        subprocess.run(merge_command, shell=True, check=True)
        logger.info("Successfully sorted and merged BED file to %s",
                    merged_bed_file)

    # If an error is encountered log the error
    except subprocess.CalledProcessError as e:
        logger.error("Error during bedtools operation: %s", e)
        raise

    return merged_bed_file
