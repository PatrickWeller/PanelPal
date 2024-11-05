import requests


def get_response(panel_id):
    """
    Input: A panel id, e.g. R293
    Output: A JSON from Panel App API with end point panels/{id}
    """
    url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}"


def create_locus_dictionary(api_response, build):
    """
    Input: A valid API response JSON from a panel, and a chr build (e.g. GRch37)
    Output: A dictionary of genes and their chromosomal locations in that panel
    E.g.
    {'ENSG00000087460': ['20', '57414773', '57486247'],
     'ENSG00000113448': ['5', '58264865', '59817947']}
    """
    genes = api_response["genes"]
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