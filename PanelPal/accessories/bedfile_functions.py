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

- bed_head(panel_id, panel_version, genome_build, num_genes, bed_filename):
    Generates and prepends a metadata header to the specified BED file. The 
    header includes information such as the panel ID, version, genome build, 
    and the number of genes in the panel.

Example:
--------
>>> bed_file_exists("R207", "4", "GRCh38")
True

>>> read_bed_file("R207_v4_GRCh38.bed")
['chr1_100_200', 'chr2_300_400', 'chrX_500_600']

>>> compare_bed_files("file1.bed", "file2.bed")
Comparison complete. Differences saved in bedfile_comparisons/comparison_file1.bed_file2.bed.txt

>>> bed_head("R207", "4.0", "GRCh38", 200, "R207_v4_GRCh38.bed")
Header successfully added to R207_v4_GRCh38.bed
"""

import os
from datetime import datetime
from PanelPal.settings import get_logger

logger = get_logger(__name__)

def bed_file_exists(panel_name, panel_version, genome_build):
    """
    Check if a bed file with a certain name already exists
    """
    if not all([panel_name, panel_version, genome_build]):
        raise ValueError(
            "Panel name, panel version, or genome build missing."
        )
    try:
        # Define the expected BED file name
        output_bed = f"/bed_files/{panel_name}_v{panel_version}_{genome_build}.bed"
        logger.debug("Checking existence of BED file: %s", output_bed)

        # Check if the file exists
        file_exists = os.path.isfile(output_bed)

        if file_exists:
            logger.info("BED file exists: %s", output_bed)
        else:
            logger.debug("BED file does not exist: %s", output_bed)
        return file_exists

    except ValueError as e:
        logger.error("Invalid arguments provided: %s", str(e))
        raise

    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))
        raise

def read_bed_file(filename):
    """
    Reads a BED file, ignoring header lines starting with '#'.
    Returns a set of BED entries (start, end, and any additional columns).
    """
    if not os.path.isfile(filename):
        error_message = f"The file {filename} does not exist."
        logger.error("File not found: %s", error_message)
        raise FileNotFoundError(error_message)
    try:
        logger.info("Reading BED file: %s", filename)
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

        logger.info("Successfully read %d entries from file: %s",
                    len(bed_entries),
                    filename)
        return sorted(bed_entries)

    except Exception as e:
        logger.error("An unexpected error occurred while reading '%s': %s",
                    filename,
                    str(e)
                    )
        raise

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
        # Check for file existence directly and log errors
    for file in [file1, file2]:
        if not os.path.exists(file):
            logger.error("Input file does not exist: %s", file)

    # Raise an exception if one or both files do not exist
    if not os.path.exists(file1) or not os.path.exists(file2):
        raise FileNotFoundError("One or both input files do not exist.")

    try:
        # Read the BED files
        logger.info("Comparing BED files: %s and %s", file1, file2)
        bed_file1 = read_bed_file(file1)
        bed_file2 = read_bed_file(file2)

        # Specify output folder (hardcoded)
        output_folder = "bedfile_comparisons"

        # Create the output folder if it does not exist
        try:
            if not os.path.exists(output_folder):
                logger.debug("Creating output folder: %s", output_folder)
                os.makedirs(output_folder)
        except OSError as o:
            logger.error("Failed to create output folder '%s': %s", output_folder, str(o))
            raise

        # Generate the output file name based on input file names
        output_file = os.path.join(
            output_folder,
            f"comparison_{os.path.basename(file1)}_{os.path.basename(file2)}.txt"
            )

        # Find the differences
        logger.debug("Calculating differences between the BED files.")
        diff_file1 = sorted(set(bed_file1) - set(bed_file2))
        diff_file2 = sorted(set(bed_file2) - set(bed_file1))

        # Column widths for formatting output
        col_widths = {
            "entry": 60, 
            "comment": 40
        }

        # Write the differences to the output file
        try:
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

        except OSError as e:
            logger.error("Failed to write to output file '%s': %s",
                         output_file,
                         str(e)
                         )
            raise

    except Exception as e:
        logger.error(
            "Error: %s", str(e)
            )
        raise


def bed_head(panel_id, panel_version, genome_build, num_genes, bed_filename):
    """
    Generates a header for the BED file with metadata information and prepends it to the file.
    
    Parameters
    ----------
    panel_id : str
        The ID of the panel (e.g., "R207").
    panel_version : str
        The version of the panel (e.g., "4.0").
    genome_build : str
        The genome build (e.g., "GRCh38").
    num_genes : int
        The number of genes in the panel.
    bed_filename : str
        The name of the BED file being generated.
    
    Returns
    -------
    None
        This function directly modifies the BED file by prepending the header.
    """
    # Get date of creation
    date_generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the bed_filename contains "merged"
    if "merged" in bed_filename.lower():
        header = (
            f"# Merged BED file generated for panel: {panel_id} (Version: {panel_version}) "
            f"Date of creation: {date_generated}.\n"
            f"# Genome build: {genome_build}. Number of genes: {num_genes}\n"
            f"# Merged BED file: {bed_filename}\n"
            "# Columns: chrom, chromStart, chromEnd \n"
            "# Note: for exon and gene details, see the original BED file.\n"
        )
    else:
        header = (
            f"# BED file generated for panel: {panel_id} (Version: {panel_version}). "
            f"Date of creation: {date_generated}.\n"
            f"# Genome build: {genome_build}. Number of genes: {num_genes}.\n"
            f"# BED file: {bed_filename}\n"
            "# Columns: chrom, chromStart, chromEnd, exon_number|transcript|gene symbol\n"
        )

    # Prepend the header to the file
    try:
        with open(bed_filename, 'r+', encoding='utf-8') as bed_file:
            file_content = bed_file.read()  # Read the current content of the file
            bed_file.seek(0, 0)  # Move the file pointer to the beginning of the file
            bed_file.write(header + file_content)  # Write the header and then the original content

        # Log success message
        logger.info("Header successfully added to %s",
                    bed_filename
                    )

    except FileNotFoundError as fnf_error:
        # Handle file not found error
        logger.error("File %s not found: %s",
                     bed_filename,
                     fnf_error,
                     exc_info=True
                     )
        raise

    except PermissionError as perm_error:
        # Handle permission error (e.g., no read/write access to the file)
        logger.error("Permission denied when accessing %s: %s",
                     bed_filename,
                     perm_error,
                     exc_info=True
                     )
        raise

    except IOError as io_error:
        # Handle general IO errors, like read/write issues
        logger.error("IOError while processing %s: %s",
                     bed_filename,
                     io_error,
                     exc_info=True
                     )
        raise

    except Exception as e:
        # Catch any unexpected errors that don't fall into the above categories
        logger.error("Unexpected error while adding header to %s: %s",
                     bed_filename,
                     e,
                     exc_info=True
                     )
        raise
