import requests
import time
import logging

# set up logging
logging.basicConfig(
    level=logging.DEBUG, # logging level
    format='%(asctime)s - %(levelname)s - %(message)s', handlers=[ # log format (time, logging level, and log message)
    logging.FileHandler("logging/api_functions.log"), # store logging output here
    logging.StreamHandler()    
])


def get_gene_transcript_data(gene_name, genome_build="GRCh38", max_retries=4):
    """
    Fetches the gene transcript data for a given gene from the Variant Validator API.

    Args:
        gene_name (str): The name of the gene to fetch transcript data for.
        genome_build (str, optional): The genome build to use (default is "GRCh38").
        max_retries (int, optional): The maximum number of retries in case rate limit is exceeded (error 429). 
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

        logging.info(f"Fetching data for {gene_name} (Attempt {retries+1})")

        # Send the GET request to the Variant Validator API
        response = requests.get(url)

        if response.status_code == 200: # success
            logging.info(f"Data for {gene_name} fetched successfully.")
            return response.json() # return JSON content from API response
        
        # run a number of retries if request times out
        elif response.status_code == 429:
            wait_time = 2 ** retries # the time delay between requests exponentially increases for each new retry
            logging.warning(f"Rate limit exceeded for {gene_name}. Retrying in {wait_time} seconds.")
            time.sleep(wait_time) 
            retries += 1
        else:
            logging.error(f"Failed to fetch gene data for {gene_name}: {response.status_code}")
            raise Exception(f"{response.status_code}. Terminating.")
    
    # exception for when every attempt to fetch gene data fails
    logging.error(f"Max retries reached for {gene_name}. The number of tries may need increasing.")
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
            chromosome = transcript['annotations']['chromosome']
            
            # Extract the reference transcript information
            transcript_reference = transcript['reference']
            
            # Extract the gene symbol
            gene_symbol = gene_data['current_symbol']
            
            # Loop through the genomic spans in the transcript (exon structures)
            for genomic_span_key, genomic_span in transcript['genomic_spans'].items():
                for exon in genomic_span['exon_structure']:
                    # Extract exon-specific information such as exon number, start, and end positions
                    exon_number = exon['exon_number']
                    exon_start = exon['genomic_start']
                    exon_end = exon['genomic_end']
                    
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
    
    logging.info(f"Extracted {len(exon_data)} exons for the gene.")
    
    # Return the complete list of exon data
    return exon_data


def generate_bed_file(gene_list, panel_name, genome_build="GRCh38"):
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
    output_file = f"{panel_name}_{genome_build}.bed"
    logging.info(f"Creating BED file: {output_file}")

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
                    # Each line in the BED file corresponds to an exon and its relevant details
                    bed_file.write(f"{exon['chromosome']}\t{exon['exon_start']}\t{exon['exon_end']}\t"
                                f"{exon['exon_number']}\t{exon['reference']}\t{exon['gene_symbol']}\n")

                # log addition of exon data for each gene    
                logging.info(f"Added exon data for {gene} to the BED file.")
            
            except Exception as e:
                logging.error(f"Error processing {gene}: {e}")

        # log message indicating that BED file has been successfully saved
        logging.info(f"Data saved to {output_file}")
    



####### TEST VARIABLES #######
gene_list = ["PRKAR1A", "PDE4D", "GNAS"]
panel_name = "R293"

generate_bed_file(gene_list, panel_name)
