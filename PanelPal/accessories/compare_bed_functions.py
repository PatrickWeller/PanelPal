"""
This module contains functions for working with BED files, including checking 
for the existence of a BED file, reading BED file contents, and comparing two 
BED files to find differences.

Functions:
----------
- bed_file_exists(panel_name, panel_version, genome_build):
    Checks if a BED file with the specified panel name, version, and genome 
    build exists.

- read_bed_file(filename):
    Reads a BED file, ignoring comment lines, and returns a sorted list of 
    unique concatenated BED entries.

- compare_bed_files(file1, file2):
    Compares two BED files and writes the differences to an output file.
    Outputs BED entries present only in either file1 or file2. Each entry 
    will be tagged with whether it was found in file1 or file2.

Example:
--------
>>> bed_file_exists("R207", "4", "GRCh38")
True

>>> read_bed_file("R207_v4_GRCh38.bed")
['chr1_100_200', 'chr2_300_400', 'chrX_500_600']

>>> compare_bed_files("file1.bed", "file2.bed")
Comparison complete. Differences saved in bedfile_comparisons/comparison_file1.bed_file2.bed.txt
"""

import os
from PanelPal.settings import get_logger

logger = get_logger(__name__)

def bed_file_exists(panel_name, panel_version, genome_build):
    """
    Check if a bed file with a certain name already exists
    """
    # Define the expected BED file name
    output_file = f"{panel_name}_v{panel_version}_{genome_build}.bed"
    # Check if the file exists
    return os.path.isfile(output_file)

def read_bed_file(filename):
    """
    Reads a BED file, ignoring header lines starting with '#'.
    Returns a set of BED entries (start, end, and any additional columns).
    """
    bed_entries = set()
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            fields = line.split('\t')
            # Concatenate all columns with underscores
            concatenated_entry = '_'.join(fields)
            bed_entries.add(concatenated_entry)

    return sorted(bed_entries)


def compare_bed_files(file1, file2):
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
    try:
        # Read the BED files
        bed_file1 = read_bed_file(file1)
        bed_file2 = read_bed_file(file2)

        # Specify output folder (hardcoded)
        output_folder = "bedfile_comparisons"

        # Create the output folder if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Generate the output file name based on input file names
        output_file = os.path.join(
            output_folder,
            f"comparison_{os.path.basename(file1)}_{os.path.basename(file2)}.txt"
            )

        # Find the differences
        diff_file1 = sorted(set(bed_file1) - set(bed_file2))
        diff_file2 = sorted(set(bed_file2) - set(bed_file1))

        # Column widths for formatting output
        col_widths = {
            "entry": 60, 
            "comment": 40
        }

        # Write the differences to the output file
        with open(output_file, 'w', encoding='utf-8') as out_file:
            header = (f"{'Entry'.ljust(col_widths['entry'])}"
                      f"{'Comment'.ljust(col_widths['comment'])}\n")

            # Header for readability
            out_file.write(header)

            # Add a separator line for readability
            out_file.write("=" * (col_widths["entry"] + col_widths["comment"]) + "\n")

            # Write differences
            for entry in diff_file1:
                out_file.write(
                    f"{entry.ljust(col_widths['entry'])}# Present in {file1} only\n"
                    )
            for entry in diff_file2:
                out_file.write(
                    f"{entry.ljust(col_widths['entry'])}# Present in {file2} only\n"
                    )

        logger.info(
            "Comparison complete. Differences saved in %s", output_file
            )

    except FileNotFoundError as e:
        logger.error(
            "Error: %s", e
            )
        raise
