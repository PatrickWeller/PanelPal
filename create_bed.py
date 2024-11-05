# Example JSON data to be returned from PanelApp API
api_data = {
    "genes": [
        {
            "gene_name": "PRKAR1A",
            "chromosome": "17",
            "start": 66507921,
            "end": 66547460
        },
        {
            "gene_name": "PDE4D",
            "chromosome": "5",
            "start": 58264865,
            "end": 59817947
        },

        {
            "gene_name": "GNAS",
            "chromosome": "20",
            "start": 57414773,
            "end": 57486247
        }
    ]
}
# Example panel name 
panel_name = "R293"


def generate_bed(api_data, panel_name):
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
        for gene in api_data["genes"]:
            chromosome = "chr" + gene["chromosome"] # chr prefix needed
            start = gene["start"]
            end = gene["end"]
            gene_name = gene["gene_name"]
            
            # Write the data in tab-seperated BED format
            bed_file.write(f"{chromosome}\t{start}\t{end}\t{gene_name}\n")

    print("Bed file generated: " + output_file)


# Example usage
# Generate BED file for panel
generate_bed(api_data, "R293")