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