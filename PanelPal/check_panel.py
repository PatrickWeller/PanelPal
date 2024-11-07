#!/usr/bin/env python

import argparse
import re
import sys
from panel_app_api_functions import get_response
from panel_app_api_functions import get_name_version


def parse_arguments():
	# Create the argument parser and add arguments
	argument_parser = argparse.ArgumentParser(description="Format a given panel ID.")
	argument_parser.add_argument("--panel_id", help="Panel ID e.g. R59, r59, or 59", required=True)
	return argument_parser.parse_args()  # Return the parsed arguments


def format_panel_id(input_id):
	"""
	Formats the input panel ID by stripping whitespace, converting to uppercase,
	and ensuring it starts with 'R' followed by digits.
	
	Args:
		input_id (str): The input panel ID to format.
		
	Returns:
		str: Formatted panel ID starting with 'R' and followed by digits.
	
	Raises:
		ValueError: If the input ID is not in the expected format.
	"""
	
	# Remove whitespace and convert to uppercase
	panel_id = input_id.strip().upper()
	
	# Prepend 'R' if not already present
	if not panel_id.startswith("R"):
		panel_id = "R" + panel_id
	
	# Validate the format: 'R' followed by digits
	if not re.fullmatch(r"R\d+", panel_id):
		raise ValueError("Panel ID must be 'R' followed by digits (e.g., 'R59').")
	
	return panel_id


def main():
	# Gather command line arguments
	args = parse_arguments()
	
	try:
		# Format the panel_id and print the result
		formatted_id = format_panel_id(args.panel_id)
		print(f"Panel ID: {formatted_id}")
		
		# Make the API call and print the response
		response = get_response(formatted_id)

		# 
		panel_info = get_name_version(response)
		indication = panel_info['name']
		version = panel_info['version']

		print(f"Clinical indication: {indication}")
		print(f"Latest version: {version}")

	except ValueError as e:
		# Print error and exit if the format is incorrect
		print(f"Error: {e}", file=sys.stderr)
		sys.exit(1)


if __name__ == "__main__":
	main()