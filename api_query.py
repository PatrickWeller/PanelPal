import requests

# check ID is an integer 
def is_integer(id): 
    return isinstance(id, int)

def get_name_version_genes(id):

    if not is_integer(id): 
        raise ValueError("The panel ID must be an integer.")

    url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{id}/"

    try:
        # send request
        response = requests.get(url)
        response.raise_for_status()
        
        # extract relevant info ("N/A" returned if value doesn't exist)
        data = response.json()
        panel_name = data.get("name","N/A")
        panel_version = data.get("version","N/A")
        genes = [gene["gene_data"]["gene_symbol"] for gene in data.get("genes",[])]

        return {
            "name": panel_name,
            "version": panel_version,
            "genes": genes
        }

    except requests.exeptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":

    ### EXAMPLE PANEL ID - CAN BE SET DYNAMICALLY
    id = 1 

    results = {}

    # Fetch panel information
    panel_read_info = get_name_version_genes(id)
    if "error" not in panel_read_info:
        results["panel_id"] = id
        results["name"] = panel_read_info["name"]
        results["version"] = panel_read_info["version"]
        results["genes"] = panel_read_info["genes"]
    else:
        results["error"] = panel_read_info["error"]

