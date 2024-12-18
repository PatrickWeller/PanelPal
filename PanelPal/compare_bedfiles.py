"""
This script compares two BED files and writes the differences to an output file.

The script takes two BED files as input, compares them, and identifies the entries 
that are present in one file but not the other. The differences are then written 
to an output file. Each entry in the output is tagged with whether it was found 
in the first or second file.

The script expects two command-line arguments: the paths to the first and second 
BED files. The comparison results are saved in a predefined folder called 
'PanelPal/bedfile_comparisons', with the output file name reflecting the input 
files.

Functions
---------
parse_arguments() :
    Parses command-line arguments for the script.
main() :
    Main entry point of the script. Parses arguments and calls the compare_bed_files 
    function to compare the BED files.

Raises
------
FileNotFoundError :
    If one or both of the input files do not exist.
"""

import sys
import os
import argparse
from PanelPal.settings import get_logger
from PanelPal.accessories.bedfile_functions import compare_bed_files
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logger = get_logger(__name__)

def parse_arguments():
    """
    Parses command-line arguments for the script.
    """
    parser = argparse.ArgumentParser(
        description="Compare two BED files and find the differences between them."
    )
    parser.add_argument(
        'file1',
        type=str,
        help="Path to the first BED file."
    )
    parser.add_argument(
        'file2',
        type=str,
        help="Path to the second BED file."
    )
    return parser.parse_args()

def main():
    """
    Compare two BED files and write the differences to an output file.
    Outputs BED entries present only in either file1 or file2.
    Each entry will be tagged with whether it was found in file1 or file2.

    Parameters
    ----------
    file1 : str
        Path to the first BED file.
    file2 : str
        Path to the second BED file.

    Raises
    ------
    FileNotFoundError
        If one or both of the input files do not exist.
    """
    # Parse command-line arguments
    args = parse_arguments()

    logger.info("Comparing BED files: %s and %s", args.file1, args.file2)

    compare_bed_files(args.file1, args.file2)

    logger.info("BED file comparison completed successfully.")

if __name__ == "__main__":
    main()
