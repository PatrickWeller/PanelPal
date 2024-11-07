import argparse
import panel_app_api_functions
import variant_validator_api_functions
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # You can add more handlers to log to a file if needed
    ]
)

def main(panel_id, panel_version, genome_build):
    """
    Main function that processes the panel data and generates the BED file.
    
    Args:
        panel_id (str): The ID of the panel (e.g., "R207").
        panel_version (str): The version of the panel (e.g., "4").
        genome_build (str): The genome build (e.g., "GRCh38").

    Example: python generate_bed.py -p "R207" -v "4" -g "GRch38"
    """
    logging.info("Starting main process for panel_id=%s, panel_version=%s, genome_build=%s", panel_id, panel_version, genome_build)
    
    try: 
        # Fetch the panel data using the panel_id
        panelapp_data = panel_app_api_functions.get_response(panel_id)
        logging.info("Panel data fetched successfully for panel_id=%s", panel_id)
        
        # Extract the list of genes from the panel data
        gene_list = panel_app_api_functions.get_genes(panelapp_data)
        logging.info("Gene list extracted successfully for panel_id=%s", panel_id)

        # Generate the BED file using the gene list, panel ID, panel version, and genome build
        variant_validator_api_functions.generate_bed_file(gene_list, panel_id, panel_version, genome_build)
        
        # Perform bedtools merge with the provided panel details
        variant_validator_api_functions.bedtools_merge(panel_id, panel_version, genome_build)

        logging.info("Process completed successfully for panel_id=%s", panel_id)

    except Exception as e:
        logging.error("An error occurred in the BED file generation process for panel_id=%s: %s", panel_id, e)
        raise  # Reraise the exception after logging it for further handling if needed


if __name__ == '__main__':
    """
    Script entry point: parses command-line arguments and calls the main function.
    """
    # Set up argument parsing for the command-line interface (CLI)
    parser = argparse.ArgumentParser(description='Generate a BED file and perform merge using panel details.')
    
    # Define the command-line arguments:
    # panel_id: The ID of the panel, e.g., "R207"
    parser.add_argument('-p', '--panel_id', type=str, required=True, help='The ID of the panel, (e.g., "R207").')

    # panel_version: The version of the panel, e.g., "4"
    parser.add_argument('-v', '--panel_version', type=str, required=True, help='The version of the panel (e.g., "4").')

    # genome_build: The genome build, e.g., "GRCh38"
    parser.add_argument('-g', '--genome_build', type=str, required=True, help='The genome build (e.g., GRCh38).')
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the main function with the parsed arguments
    main(args.panel_id, args.panel_version, args.genome_build)

# Below commented-out code is not executed when running the script via command-line arguments
# Uncomment and edit if you want to run the script with hardcoded values.

# panel_id = "R207"
# panel_version = "4"
# genome_build = "GRCh38"

# panelapp_data = panel_app_api_functions.get_response(panel_id)
# gene_list = panel_app_api_functions.get_genes(panelapp_data)

# variant_validator_api_functions.generate_bed_file(gene_list, panel_id, panel_version, genome_build)
# variant_validator_api_functions.bedtools_merge(panel_id, panel_version, genome_build)
