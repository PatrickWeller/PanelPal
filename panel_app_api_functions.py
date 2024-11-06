import requests


def get_response(panel_id):
    """
    Fetches JSON data for a given panel ID from the PanelApp API.

    Parameters: panel_id (str) – e.g., 'R293'.
    Returns: dict – JSON data if successful.
    Raises: Exception – if request fails.
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
    
    
### function to get panel name and version
def get_name_version(response):
    try:
        # Ensure the response is successful
        response.raise_for_status()
        
        # Extract relevant info ("N/A" returned if value doesn't exist)
        data = response.json()
        panel_name = data.get("name", "N/A")
        panel_version = data.get("version", "N/A")

        return {
            "name": panel_name,
            "version": panel_version
        }

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def get_genes(response):
    try:
        # Ensure the response is successful
        response.raise_for_status()

        # Extract the list of genes
        data = response.json()
        genes = [gene["gene_data"]["gene_symbol"] for gene in data.get("genes", [])]

        return genes

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []


def create_locus_dictionary(response, build):
    """
    Input: A valid API response JSON from a panel, and a chr build (e.g. GRch37)
    Output: A dictionary of genes and their chromosomal locations in that panel
    E.g.
    {'ENSG00000087460': ['20', '57414773', '57486247'],
     'ENSG00000113448': ['5', '58264865', '59817947']}
    """
    try:
        # Ensure the response is successful
        response.raise_for_status()
    
        data = response.json()
        genes = data["genes"]
        location_dict = {}
        for gene in genes:
            gene_version = gene["gene_data"]["ensembl_genes"][f"{build}"]
            release = list(gene_version.keys())[0]  # Release may change? Just taking the first release in this instance
            gene_version = gene_version[release]
            chrom, position = gene_version["location"].split(":")
            start, end = position.split("-")
            coordinates = [chrom, start, end]
            location_dict[gene_version["ensembl_id"]] = coordinates
        return location_dict
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []


def generate_bed(location_dict, panel_name):
    """
    Generate a BED file from a PanelApp JSON object

    api_data (dict): The JSON data from Panel App.
    panel_name (str): The name of the panel for saving the bed file.
    """

    # Create a filename
    output_file = panel_name + ".bed"

    # Open the output file for writing
    with open(output_file, 'w') as bed_file:
        # Iterate through the genes in the JSON to extract data
        for gene_id, position in location_dict.items():
            # Extract data from the list
            chromosome = "chr" + position[0]  # Add 'chr' prefix
            start = int(position[1]) - 1
            end = position[2]
            
            # Write the data in tab-seperated BED format
            bed_file.write(f"{chromosome}\t{start}\t{end}\t{gene_id}\n")

    print("Bed file generated: " + output_file)
