#!/usr/bin/env python

import argparse
import re
import requests
import logging
import sys
import time
import json
from accessories.panel_app_api_functions import get_response, get_name_version


def setup_logging(log_file="logging/check_panel.log"):
	"""
	Set up logging configuration.

	This function configures the logging system to write logs to a file and also
	outputs warnings and above to the console. The log file is specified by the
	`log_file` argument (default is "logging/check_panel.log").

	Args:
	    log_file (str): Path to the log file. Defaults to "logging/check_panel.log".

	Returns:
	    logging.Logger: The configured logger object.

	"""

	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)

	file_handler = logging.FileHandler(log_file)
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(
		logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
	)

	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.WARNING)
	console_handler.setFormatter(
		logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
	)

	logger.addHandler(file_handler)
	logger.addHandler(console_handler)
	return logger


def parse_arguments():
	"""Parse command-line arguments."""
	argument_parser = argparse.ArgumentParser(
		description="Format a given panel ID."
	)
	argument_parser.add_argument(
		"--panel_id", help="Panel ID e.g. R59, r59, or 59", required=True
	)
	return argument_parser.parse_args()


def is_valid_panel_id(input_id):
	"""
	Check if the input panel ID is valid.

	   Valid panel IDs must match the pattern 'R' followed by one or more digits (e.g., "R59").

	   Args:
	       input_id (str): The panel ID to check.

	   Returns:
	       bool: True if the input ID is valid, False otherwise.

	   Example:
	       is_valid_panel_id("R59")  # Returns True
	       is_valid_panel_id("59")   # Returns True
	       is_valid_panel_id("r59")  # Returns True
	       is_valid_panel_id("XYZ")  # Returns False

	"""
	return re.fullmatch(r"R\d+$", input_id) is not None


def format_panel_id(input_id: str) -> str:
	"""
	Format the input panel ID to ensure it follows the correct format.

	The function strips any surrounding whitespace, converts the ID to uppercase,
	and ensures that the ID starts with 'R' followed by one or more digits.
	If the input doesn't meet this format, it raises a `ValueError`.

	Args:
	    input_id (str): The panel ID to format (e.g., "59", "r59", or "R59").

	Returns:
	    str: The correctly formatted panel ID (e.g., "R59").

	Raises:
	    ValueError: If the input panel ID is not in a valid format.

	Example:
	    formatted_id = format_panel_id("r59")
	    print(formatted_id)  # Output: "R59"

	"""

	panel_id = input_id.strip().upper()
	if not panel_id.startswith("R"):
		panel_id = "R" + panel_id
	if not is_valid_panel_id(panel_id):
		raise ValueError(
			"Panel ID must be 'R' followed by digits (e.g., 'R59')."
		)
	return panel_id


def fetch_panel_info(
	formatted_id: str, retries: int = 3, delay: int = 10
) -> dict:
	"""
	Fetch the panel information from the API with retry logic.

	This function attempts to retrieve the panel name and version from the API. If the request
	fails due to network issues, it will retry up to a specified number of times.

	Args:
	    formatted_id (str): The formatted panel ID (e.g., "R59").
	    retries (int, optional): The number of retry attempts in case of failure. Defaults to 3.
	    delay (int, optional): The delay in seconds between retries. Defaults to 10.

	Returns:
	    dict: A dictionary containing the panel's name and version:
	        - 'name': The clinical indication or description of the panel.
	        - 'version': The version of the panel.

	Raises:
	    requests.exceptions.RequestException: If the API request fails after the specified retries.
	    KeyError: If the response does not contain the expected keys ('name' or 'version').

	Example:
	    panel_info = fetch_panel_info("R59")
	    print(panel_info["name"], panel_info["version"])
	"""
	
	for attempt in range(1, retries + 1):
		try:
			response = get_response(formatted_id)
			panel_info = get_name_version(response)
			if "name" not in panel_info or "version" not in panel_info:
				raise KeyError("Missing 'name' or 'version' in response.")
			return panel_info
		except requests.exceptions.RequestException as e:
			if attempt < retries:
				logging.warning(
					"Attempt %d/%d: Unable to reach API, reattempting connection in %d seconds...",
					attempt,
					retries,
					delay,
				)
				time.sleep(delay)
			else:
				# Log a specific message for the final attempt failure
				logging.error(
					"Final attempt (%d/%d) failed: Unable to reach the API. Please check your connection.",
					attempt,
					retries,
				)


def main():
	"""
	Main entry point of the script.

	   This function sets up the logger, parses the command-line arguments for the panel ID,
	   formats the panel ID, retrieves panel information from the API, and prints the result.
	   It also handles exceptions and logs errors accordingly.

	"""

	# Set up logger
	logger = setup_logging()

	# Gather command-line arguments
	args = parse_arguments()
	logger.debug("Parsed command-line arguments: panel_id=%s", args.panel_id)

	try:
		formatted_id = format_panel_id(args.panel_id)
		panel_info = fetch_panel_info(formatted_id)

		print(f"Panel ID: {formatted_id}")
		print(f"Clinical Indication: {panel_info['name']}")
		print(f"Latest Version: {panel_info['version']}")

	except ValueError as e:
		# Log the ValueError
		logger.error("ValueError: %s", e)
		sys.exit(1)

	except KeyError as e:
		# Log the missing field error
		logger.error("Unexpected API response: Missing expected fields.")
		sys.exit(3)

	except Exception as e:
		# Log any other errors
		logger.error(e)
		sys.exit(99)


if __name__ == "__main__":
	main()
