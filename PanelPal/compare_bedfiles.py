import os
import argparse
from PanelPal.settings import get_logger
from PanelPal.accessories.compare_bed_functions import read_bed_file, compare_bed_files

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

    compare_bed_files(args.file1, args.file2)
    
if __name__ == "__main__":
    main()