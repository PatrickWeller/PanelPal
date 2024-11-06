import requests


def get_gene_transcript_data(gene_name, genome_build="GRCh38"):
    """
    Fetches the gene transcript data for a given gene from the Variant Validator API.

    Args:
        gene_name (str): The name of the gene to fetch transcript data for.
        genome_build (str): The genome build to use (default is "GRCh38").

    Returns:
        dict: The JSON response containing gene transcript information.

    Raises:
        Exception: If the request to the API fails (status code not 200).
    """
    # Base URL for the Variant Validator API endpoint
    base_url = "https://rest.variantvalidator.org/VariantValidator/tools/gene2transcripts_v2/"
    
    # Construct the URL with the given gene name and genome build
    url = f"{base_url}/{gene_name}/mane_select/refseq/{genome_build}?content-type=application%2Fjson"
    
    # Send the GET request to the Variant Validator API
    response = requests.get(url)
    
    # Check if the response status code is 200 (OK)
    if response.status_code != 200:
        # Raise an exception if the API call was unsuccessful
        raise Exception(f"Failed to fetch data for gene '{gene_name}': {response.status_code}")
  
    # Return the JSON content from the API response
    return response.json()

def extract_exon_info(gene_transcript_data):
    """
    Extracts exon information from the gene transcript data.

    Args:
        gene_transcript_data (dict): The JSON response containing the gene transcript data.

    Returns:
        list: A list of dictionaries, each containing exon data (chromosome, exon start, exon end, etc.).
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
    
    # Return the complete list of exon data
    return exon_data

def generate_bed_file(gene_list, panel_name, genome_build):
    """
    Generates a BED file containing exon data for a list of genes.

    Args:
        gene_list (list): A list of gene names for which exon data is to be extracted.
        panel_name (str): The name of the panel, used to name the output BED file.

    Returns:
        None: This function does not return anything, it directly writes to a BED file.
    """
    # Define the name of the output BED file based on the panel name and genome build
    output_file = f"{panel_name}_{genome_build}.bed"

    # Open the BED file for writing (or create it if it doesn't exist)
    with open(output_file, 'w') as bed_file:
        # Iterate over the list of genes to fetch and process their transcript data
        for gene in gene_list:
            # Fetch the transcript data for the current gene using the API
            gene_transcript_data = get_gene_transcript_data(gene, genome_build)
            
            # Extract the exon information from the retrieved transcript data
            exon_data = extract_exon_info(gene_transcript_data)
            
            # Write the extracted exon information to the BED file
            for exon in exon_data:
                # Each line in the BED file corresponds to an exon and its relevant details
                bed_file.write(f"{exon['chromosome']}\t{exon['exon_start']}\t{exon['exon_end']}\t"
                               f"{exon['exon_number']}\t{exon['reference']}\t{exon['gene_symbol']}\n")

        # Print a message indicating the BED file has been successfully saved
        print(f"Data saved to {output_file}")
    

def function2():
    ...
    

def function3():
    ...