import requests

def main():
    panel_id = "R293"
    build = "GRch37"
    
    response = get_response(panel_id)
    print(create_locus_dictionary(response, build))
    

def get_response(panel_id):
    """
    Input a panel id, e.g. R293 or 293.
    Submits an API request, and returns a JSON
    """
    url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}"

def create_locus_dictionary(api_response, build):
    """
    Input a valid API response JSON and a chr build (e.g. GRch37)
    Outputs a list of chromosomal locatins in that panel
    """
    genes = api_response["genes"]
    location_dict = {}
    for gene in genes:
        gene_version = gene["gene_data"]["ensembl_genes"][f"{build}"]["82"]
        location_dict[gene_version["ensembl_id"]] = gene_version["location"]
    return location_dict


if __name__ == "__main__":
    main()