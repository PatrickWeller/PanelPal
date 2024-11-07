#!/usr/bin/env python

import subprocess
import logging

# Configure logging
logging.basicConfig(
    filename="logs/bedtools_merge.log", # Log file name
    filemode="a", # Append mode
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    level=logging.INFO # Minimum logging level to capture
)

# Create a logger
logger = logging.getLogger()


def bedtools_merge(exon_dict, panel_id, panel_version):
    """
    Converts an exon dictionary to a sorted and merged BED file.

    Parameters:
    - exon_dict (list of dict): List of exons with chromosome, start, and end positions.
    - panel_id (str): Identifier for the genomic panel.
    - panel_version (str): Version of the genomic panel.

    Outputs:
    - A sorted and merged BED file eg. R59_v2_merged.bed

    Dependencies:
    - Requires bedtools (available in PanelPal conda environment)
    """
    
    # Sort the exon dictionary by chromosome name and start/end positions
    sorted_exons = sorted(exon_dict, key=lambda exon: (exon["chr"], exon["start"], exon["end"]))
    
    # Convert exon dictionary into bed format and write a temporary file (to be deleted later)
    bed_file = f"{panel_id}_{panel_version}.bed"
    with open(bed_file, 'w') as file:
        for exon in sorted_exons:
            exon["start"] -= 1  # Subtract 1 to zero-index the start position
            file.write(f"{exon['chr']}\t{exon['start']}\t{exon['end']}\n")
    
    # Try running bedtools merge
    try:
        merged_bed_file = f"{panel_id}_{panel_version}_merged.bed"
        merge_command = f"bedtools merge -i {bed_file} > {merged_bed_file}"
        subprocess.run(merge_command, shell = True, check = True)
        logger.info(f"Successfully wrote sorted exons to {bed_file}")
    
    # If an error is encountered log the error
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running bedtools merge: {e}")
    
    # Remove un-merged bed file (commented out as not sure if we will need to keep this)
    # subprocess.run(f"rm {bed_file}", shell = True)


def main():
    
    # Create a mini exon dictionary for testing
    exon_dict = [
        {"chr": "chr1", "start": 10, "end": 100},
        {"chr": "chr1", "start": 300, "end": 360},
        {"chr": "chr1", "start": 320, "end": 904},
        {"chr": "chr1", "start": 101, "end": 152},
        {"chr": "chr4", "start": 100, "end": 700}
    ]

    # Set panel id and version
    panel_id = "R59"
    panel_version = "v2"
    
    # Convert exon dictionary to merged bed file
    bedtools_merge(exon_dict, panel_id, panel_version)


if __name__ == "__main__":
    main()