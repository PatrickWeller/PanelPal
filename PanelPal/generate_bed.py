import argparse
import panel_app_api_functions
import variant_validator_api_functions
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # logging level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logging/generate_bed.log"),  # store logging output here
        logging.StreamHandler()  # also print to console
    ]
)

# Get the logger instance
logger = logging.getLogger()

def main(panel_id, panel_version, genome_build):
    """
    Main function that processes the panel data and generates the BED file.
    
    Args:
        panel_id (str): The ID of the panel (e.g., "R207").
        panel_version (str): The version of the panel (e.g., "4").
        genome_build (str): The genome build (e.g., "GRCh38").

    Example: python generate_bed.py -p R207 -v 4 -g GRCh38
    """
    logging.info("Starting main process for panel_id=%s, panel_version=%s, genome_build=%s", panel_id, panel_version, genome_build)
    
    try: 
        # Fetch the panel data using the panel_id
        logging.debug("Requesting panel data for panel_id=%s", panel_id)
        panelapp_data = panel_app_api_functions.get_response(panel_id)
        logging.info("Panel data fetched successfully for panel_id=%s", panel_id)
        
        # Extract the list of genes from the panel data
        logging.debug("Extracting gene list from panel data for panel_id=%s", panel_id)
        gene_list = panel_app_api_functions.get_genes(panelapp_data)
        logging.info("Gene list extracted successfully for panel_id=%s. Total genes found: %d", panel_id, len(gene_list))

        # Generate the BED file using the gene list, panel ID, panel version, and genome build
        logging.debug("Generating BED file for panel_id=%s, panel_version=%s, genome_build=%s", panel_id, panel_version, genome_build)
        variant_validator_api_functions.generate_bed_file(gene_list, panel_id, panel_version, genome_build)
        logging.info("BED file generated successfully for panel_id=%s", panel_id)
        
        # Perform bedtools merge with the provided panel details
        logging.debug("Starting bedtools merge for panel_id=%s, panel_version=%s, genome_build=%s", panel_id, panel_version, genome_build)
        variant_validator_api_functions.bedtools_merge(panel_id, panel_version, genome_build)
        logging.info("Bedtools merge completed successfully for panel_id=%s", panel_id)

        logging.info("Process completed successfully for panel_id=%s", panel_id)

    except Exception as e:
        logging.error("An error occurred in the BED file generation process for panel_id=%s: %s", panel_id, e, exc_info=True)
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
    logging.debug("Parsed command-line arguments: panel_id=%s, panel_version=%s, genome_build=%s", args.panel_id, args.panel_version, args.genome_build)

    # Call the main function with the parsed arguments
    main(args.panel_id, args.panel_version, args.genome_build)
