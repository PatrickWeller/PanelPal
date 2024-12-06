import os
import argparse
from PanelPal.settings import get_logger
from PanelPal.accessories.compare_bed_functions import read_bed_file

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

    try:
        # Read the BED files
        bed_file1 = read_bed_file(args.file1)
        bed_file2 = read_bed_file(args.file2)

        # Specify output folder
        output_folder = "PanelPal/bedfile_comparisons"

        # Create folder if does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Specify output file path
        output_file = os.path.join(output_folder,
                                   f"comparison_{os.path.basename(args.file1)}_"
                                   f"{os.path.basename(args.file2)}.bed")

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
            out_file.write(header)
            # Add a separator line for readability
            out_file.write("=" * (col_widths["entry"] + col_widths["comment"]) + "\n")

            # Write differences
            for entry in diff_file1:
                out_file.write(f"{entry.ljust(col_widths['entry'])}# Present in "
                               f"{args.file1} only\n")
            for entry in diff_file2:
                out_file.write(f"{entry.ljust(col_widths['entry'])}# Present in "
                               f"{args.file2} only\n")

        logger.info(f"Comparison complete. Differences saved in {output_file}")

    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()