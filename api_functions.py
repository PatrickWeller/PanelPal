import requests

def main():
    panel_id = "R293"
    response = get_response(panel_id)
    print(create_locus_dictionary(response))
    

def get_response(panel_id):
    url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}"

def create_locus_dictionary(api_response):
    genes = api_response["genes"]
    location_list = []
    for gene in genes:
        location_list.append(gene["gene_data"]["ensembl_genes"]["GRch37"]["82"]["location"])
    return location_list


if __name__ == "__main__":
    main()