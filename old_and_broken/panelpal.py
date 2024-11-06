#!/usr/bin/env python

import re
import panel_app_api_functions
import logging
from settings import logger 


def get_panel_id():
    """Prompt the user for a panel ID and validate the input."""
    panel_id = input("Please enter panel ID (e.g., R59, r59, or 59): ").strip().upper()
    if re.match(r"^R?\d+$", panel_id):
        # If panel_id does not start with R add it 
        if not panel_id.startswith("R"):
            panel_id = "R" + panel_id
        return panel_id
    else:
        print("\nInvalid panel ID format. Please enter in the format R12, r12, or 12.\n")
        return None
    
    
def confirm_panel_selection():
    """Ask the user to confirm their panel selection."""
    confirmation = input("Is this correct? (yes/no): ").strip().lower()
    return confirmation in ["yes", "y"]


def main():
    
    # Print a welcome message
    print("######################################################")
    print("Welcome to PanelPal!")
    print("######################################################")
    print("")
    logger.debug("Test")

    while True:
        panel_id = get_panel_id()
        if panel_id is None:
            continue  # Retry if the panel ID was invalid

        # Try to get panel information from panelapp api
        try:
            panel_info = panel_app_api_functions.get_name_version(panel_id)
            indication = panel_info['name']
            print(f"\nPanel ID: {panel_id}")
            print(f"Clinical indication: {indication}\n")

            if confirm_panel_selection():
                    print(f"\nProceeding with the selected panel.\n")

                    # Get API response
                    response = panel_app_api_functions.get_response(panel_id)

                    # Create a locus dictionary
                    locus_dict = panel_app_api_functions.create_locus_dictionary(response, "GRch38")

                    # Generate bed file
                    panel_app_api_functions.generate_bed(locus_dict, panel_id)

                    # Exit the loop if confirmed
                    break
            else:
                print("Let's try again.\n")

        except Exception as e:
                # Handle 404 client error when R code does not exist
                print("Panel ID not found. Please try again.\n")

if __name__ == "__main__":
    main()
