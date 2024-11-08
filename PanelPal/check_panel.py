#!/usr/bin/env python

import argparse
import re
import requests
import logging
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from accessories.panel_app_api_functions import get_response, get_name_version

# Configure logging
logging.basicConfig(
	level=logging.DEBUG,  # logging level
	format="%(asctime)s - %(levelname)s - %(message)s",
	handlers=[
		logging.FileHandler("logging/check_panel.log"),  # store logging output here
	],
)

# Add a console handler for warnings and errors only
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # Set console handler to warning level
console_handler.setFormatter(
	logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logging.getLogger().addHandler(console_handler)

# Get the logger instance
logger = logging.getLogger()


def parse_arguments():
	"""Parse command-line arguments."""
	argument_parser = argparse.ArgumentParser(description="Format a given panel ID.")
	argument_parser.add_argument(
		"--panel_id", help="Panel ID e.g. R59, r59, or 59", required=True
	)
	return argument_parser.parse_args()


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
	panel_id = input_id.strip().upper()

	if not panel_id.startswith("R"):
		panel_id = "R" + panel_id

	if not re.fullmatch(r"R\d+", panel_id):
		raise ValueError("Panel ID must be 'R' followed by digits (e.g., 'R59').")

	return panel_id


def fetch_panel_info(formatted_id):
	"""
	Fetch the panel information from the API.

	Args:
		formatted_id (str): The formatted panel ID.

	Returns:
		dict: Dictionary containing panel name and version.

	Raises:
		requests.exceptions.RequestException: If there's an error making the API request.
		KeyError: If the response does not contain the expected keys.
	"""
	try:
		response = get_response(formatted_id)
		panel_info = get_name_version(response)

		# Ensure expected keys are in the response
		if "name" not in panel_info or "version" not in panel_info:
			raise KeyError(f"Response missing expected fields: 'name' or 'version'.")

		return panel_info

	except requests.exceptions.RequestException as e:
		logging.error(f"Error contacting the API: {e}")
		raise  # Re-raise exception for further handling in main()

	except KeyError as e:
		logging.error(f"API response error: {e}")
		raise  # Re-raise exception for further handling in main()


def main():
	# Gather command-line arguments
	args = parse_arguments()

	try:
		# Format the panel ID
		formatted_id = format_panel_id(args.panel_id)
		print(f"Panel ID: {formatted_id}")

		# Fetch panel information from the API
		panel_info = fetch_panel_info(formatted_id)
		indication = panel_info["name"]
		version = panel_info["version"]

		# Output the result
		print(f"Clinical indication: {indication}")
		print(f"Latest version: {version}")

	except ValueError as e:
		# Handle input format errors
		print(f"Error: {e}", file=sys.stderr)
		sys.exit(1)

	except requests.exceptions.RequestException as e:
		# Handle network issues with API
		print(
			f"Network error: Unable to reach the API. Please check your connection.",
			file=sys.stderr,
		)
		sys.exit(2)

	except KeyError as e:
		# Handle missing keys in the API response
		print(
			f"Error: Unexpected API response. Missing expected fields.", file=sys.stderr
		)
		sys.exit(3)

	except Exception as e:
		# Catch all other errors
		logging.error(f"Unexpected error: {e}")
		print(f"Unexpected error: {e}", file=sys.stderr)
		sys.exit(99)


if __name__ == "__main__":
	main()
