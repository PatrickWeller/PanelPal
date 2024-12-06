import os
from variant_validator_api_functions import generate_bed_file

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
    with open(filename, 'r') as file:
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
    Outputs BED entries present in either file1 or file2 but not both.
    Each entry will be tagged with whether it was found in file1 or file2.
    """

    # Read the BED files, ignoring header lines
    bed_file1 = read_bed_file(file1)
    bed_file2 = read_bed_file(file2)

    # Specify output folder 
    output_folder = "bedfile_comparisons"

    # Create folder if does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Specify output file path
    output_file = os.path.join(output_folder, f"comparison_{file1}_{file2}_.bed")


    # Find the differences
    diff_file1 = sorted(set(bed_file1) - set(bed_file2))
    diff_file2 = sorted(set(bed_file2) - set(bed_file1)) 

    # Column widths for formatting output
    col_widths = {
        "entry": 60, 
        "comment": 40
    }

    # Write the differences to the output file
    with open(output_file, 'w') as out_file:
        header = f"{'Entry'.ljust(col_widths['entry'])}{'Comment'.ljust(col_widths['comment'])}\n"
        out_file.write(header)
        # Add a separator line for readability
        out_file.write("=" * (col_widths["entry"] + col_widths["comment"]) + "\n")

        # Write differences
        for entry in diff_file1:
            out_file.write(f"{entry.ljust(col_widths['entry'])}# Present in {file1} only\n")
        for entry in diff_file2:
            out_file.write(f"{entry.ljust(col_widths['entry'])}# Present in {file2} only\n")

    print(f"Comparison complete. Differences saved in {output_file}")

