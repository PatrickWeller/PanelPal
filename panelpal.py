#!/usr/bin/env python

import re
import pandas as pd
import sys
import api_functions
import api_query


def load_panel_data(file_path):
    """Load panel information from a specified file."""
    return pd.read_csv(file_path, delimiter="\t", header=None, names=["panel_id", "indication"])


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
    

## TO DO: update to use api query function from Ray - this will ensure we are always querying the most up to date version
def check_panel_existence(panel_id, panel_data):
    """Check if the panel ID exists in the panel data."""
    return panel_id in panel_data["panel_id"].values


def confirm_panel_selection():
    """Ask the user to confirm their panel selection."""
    confirmation = input("Is this correct? (yes/no): ").strip().lower()
    return confirmation in ["yes", "y"]


def main():
    panel_data = load_panel_data("resources/panel_info.txt")
    
    # Print a welcome message
    print("######################################################")
    print("Welcome to PanelPal!")
    print("######################################################")
    print("")

    while True:
        panel_id = get_panel_id()
        if panel_id is None:
            continue  # Retry if the panel ID was invalid

        if check_panel_existence(panel_id, panel_data):
            
            # TO DO: build in handling of error when R number does not exist
            # currently this produces an error         
            panel_info = api_query.get_name_version(panel_id)
            indication = panel_info['name']

            print(f"\nPanel ID: {panel_id}")
            print(f"Clinical indication: {indication}\n")

            if confirm_panel_selection():
                print(f"\nProceeding with the selected panel.")

                # Get API response
                response = api_functions.get_response(panel_id)

                # Create a locus dictionary
                locus_dict = api_functions.create_locus_dictionary(response, "GRch38")

                # Generate bed file
                api_functions.generate_bed(locus_dict, panel_id)

                break  # Exit the loop if confirmed
            else:
                print("Let's try again.\n")
        else:
            print("Panel ID not found. Please try again.\n")


if __name__ == "__main__":
    main()
