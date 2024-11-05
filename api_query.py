import requests

### function to get panel name and version
def get_name_version(id):

    url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{id}/"

    try:
        # send request
        response = requests.get(url)
        response.raise_for_status()
        
        # extract relevant info ("N/A" returned if value doesn't exist)
        data = response.json()
        panel_name = data.get("name","N/A")
        panel_version = data.get("version","N/A")

        return {
            "name": panel_name,
            "version": panel_version
        }

    except requests.exceptions.RequestException as e:
        print(f"{e}")

### function to get genes list
def get_genes(id):

    try:
        url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{id}/"

        response = requests.get(url)
        data = response.json()
        genes = [gene["gene_data"]["gene_symbol"] for gene in data.get("genes",[])]

        return genes # return list, rather than dict

    except requests.exceptions.RequestException as e:
        print(f"{e}")
        return []  # return empty list on error


### Main execution block
if __name__ == "__main__":
    panel_id = "R123"
    
    # Get panel name and version
    panel_info = get_name_version(panel_id)
    print("Panel Information:", panel_info)

    # Get genes
    genes_info = get_genes(panel_id)
    print("Genes Included:", genes_info)
