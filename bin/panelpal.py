#!/usr/bin/env python

import re
import pandas as pd


def main():
    
    # TO DO: This will be handled by an API query to ensure list of available panels is always up to date
    # But for now, load panel information from file
    panel_data = pd.read_csv("resources/panel_info.txt", delimiter="\t", header=None, names=["panel_id", "indication"])


    # Print a welcome message
    print("######################################################")
    print("Welcome to PanelPal!")
    print("######################################################")
    print("")
    

    while True:
        # Prompt user for a panel id (using strip to remove any trailing whitespaces and upper to convert to upper case)
        panel_id = input("Please enter panel ID (e.g., R59, r59, or 59): ").strip().upper()

        # Validate the panel ID format
        if re.match(r"^R?\d+$", panel_id):
            # Ensure the panel ID starts with "R"
            if not panel_id.startswith("R"):
                panel_id = "R" + panel_id

            # Check the panel exists
            if panel_id in panel_data["panel_id"].values:
                # Get the clinical indication from panel_data
                indication = panel_data.loc[panel_data["panel_id"] == panel_id, "indication"].values[0]
                
                # Print the panel ID and indication to screen
                print("")
                print(f"Panel ID: {panel_id}")
                print(f"Clinical indication: {indication}")
                print("")

                # Ask the user if the panel ID is correct
                confirmation = input("Is this correct? (yes/no): ").strip().lower()
                print("")

                # If user confirms panel is correct proceed with that panel
                if confirmation == "yes" or confirmation == "y":
                    print("Proceeding with the selected panel.")
                    break  # Exit the loop if confirmed

                else:
                    print("Let's try again.") # Try again
                    print("")

            else: 
                print("Panel ID not found. Please try again.")
                print("")

        else:
            print("")
            print("Invalid panel ID format. Please enter in the format R12, r12, or 12.")
            print("")

if __name__ == "__main__":
    main()
