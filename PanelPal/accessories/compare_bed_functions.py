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

Example:
--------
>>> bed_file_exists("R207", "4", "GRCh38")
True

>>> read_bed_file("R207_v4_GRCh38.bed")
['chr1_100_200', 'chr2_300_400', 'chrX_500_600']
"""

import os

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
