import sys
import subprocess
from unittest import mock
from pathlib import Path
import pytest
from PanelPal.compare_bedfiles import parse_arguments

# Mocking file reading function
@pytest.fixture
def mock_read_bed_file():
    '''
    Fixture for mocking read_bed_file()
    '''
    with mock.patch("PanelPal.accessories.bedfile_functions.read_bed_file") as mock_bed:
        yield mock_bed

# Test for parse_arguments function
def test_parse_arguments():
    '''
    Test the arg parser works as expected.
    '''
    test_args = ['compare_bedfiles', 'file1.bed', 'file2.bed']

    # Simulate passing arguments
    with mock.patch.object(sys, 'argv', test_args):
        args = parse_arguments()

    assert args.file1 == 'file1.bed'
    assert args.file2 == 'file2.bed'

# Test for missing arguments
def test_parse_arguments_missing():
    '''
    Test that errors are raised when an arugment is missing.
    '''
    test_args = ['compare_bedfiles', 'file1.bed']  # Missing the second file

    # Simulate passing arguments
    with mock.patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit):  # for argparse errors
            parse_arguments()


# Test for too many arguments
def test_parse_arguments_too_many():
    '''
    Test action if too many arguments are provided.
    '''
    test_args = ['compare_bedfiles', 'file1.bed', 'file2.bed', 'extra_arg']

    # Simulate passing arguments
    with mock.patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit):  # for argparse errors
            parse_arguments()


# Test for main function calling compare_bed_files
@pytest.fixture
def temp_bed_files():
    """
    Fixture to create two temporary BED files for use in testing.
    These files are created in a temporary folder and deleted after testing.
    """
    # Define temporary directory
    temp_dir = Path("tmp/")

    # Ensure the directory exists
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Define the temporary file paths
    file1_path = temp_dir / "file1.bed"
    file2_path = temp_dir / "file2.bed"

    # Create and write to file1
    with open(file1_path, 'w', encoding='utf-8') as f:
        f.write("13\t48877886\t48878185\tRB1_NM_000321.3_exon1\n")
        f.write("13\t48881415\t48881542\tRB1_NM_000321.3_exon2\n")
        f.write("13\t48916734\t48916850\tRB1_NM_000321.3_exon3\n")
        f.write("13\t48919215\t48919335\tRB1_NM_000321.3_exon4\n")

    # Create and write to file2
    with open(file2_path, 'w',encoding='utf-8') as f:
        f.write("13\t48877886\t48878185\tRB1_NM_000321.3_exon1\n")
        f.write("13\t48881415\t48881542\tRB1_NM_000321.3_exon2\n")
        f.write("13\t48916734\t48916850\tRB1_NM_000321.3_exon3\n")
        f.write("13\t48919500\t48919600\tRB1_NM_000321.3_exon5\n")  # Different

    yield file1_path, file2_path

    # Cleanup temporary files
    if file1_path.exists():
        file1_path.unlink()
    if file2_path.exists():
        file2_path.unlink()

def test_main_with_temp_files(temp_bed_files):
    """
    Test the `main` function with the temporary BED files.
    """
    # Extract the paths from the fixture
    file1, file2 = temp_bed_files

    # Run the main function (using subprocess to simulate command-line)
    result = subprocess.run(
        [
            sys.executable,
            "PanelPal/compare_bedfiles.py",
            str(file1),
            str(file2),
        ],
        capture_output=True,
        text=True,
        check=False
    )

    # Check the result of the subprocess run
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"

    # Check that the comparison output file was created
    output_folder = "bedfile_comparisons"
    output_file_name = f"comparison_{file1.name}_{file2.name}.txt"
    expected_output_file = Path(output_folder) / output_file_name
    assert expected_output_file.exists(), (
        f"Expected output file {expected_output_file} was not created."
    )

    # Check the content of the output file for correctness
    with open(expected_output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Present in tmp/file1.bed only" in content
        assert "Present in tmp/file2.bed only" in content
        assert "RB1_NM_000321.3_exon4" in content  # Present only in file1
        assert "RB1_NM_000321.3_exon5" in content  # Present only in file2

    # Clean up the output file after testing
    expected_output_file.unlink(missing_ok=True)



@pytest.fixture
def temp_identical_bed_files():
    """
    Fixture to create two identical temporary BED files for testing.
    """
    # Define temporary directory
    temp_dir = Path("tmp/")

    # Ensure the directory exists
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Define the temporary file paths
    file3_path = temp_dir / "identical_file3.bed"
    file4_path = temp_dir / "identical_file4.bed"

    # Create and write identical content to both files
    with open(file3_path, 'w', encoding='utf-8') as f:
        f.write("13\t48877886\t48878185\tRB1_NM_000321.3_exon1\n")
        f.write("13\t48881415\t48881542\tRB1_NM_000321.3_exon2\n")
        f.write("13\t48916734\t48916850\tRB1_NM_000321.3_exon3\n")
        f.write("13\t48919215\t48919335\tRB1_NM_000321.3_exon4\n")

    with open(file4_path, 'w', encoding='utf-8') as f:
        f.write("13\t48877886\t48878185\tRB1_NM_000321.3_exon1\n")
        f.write("13\t48881415\t48881542\tRB1_NM_000321.3_exon2\n")
        f.write("13\t48916734\t48916850\tRB1_NM_000321.3_exon3\n")
        f.write("13\t48919215\t48919335\tRB1_NM_000321.3_exon4\n")

    yield file3_path, file4_path

    # Cleanup temporary files
    if file3_path.exists():
        file3_path.unlink()
    if file4_path.exists():
        file4_path.unlink()


def test_identical_bed_files(temp_identical_bed_files):
    """
    Test the comparison function when both BED files are identical.
    """
    # Extract the paths from the fixture
    file3, file4 = temp_identical_bed_files


    # Run the script with the correct arguments via subprocess
    result = subprocess.run(
        [
            sys.executable,
            "PanelPal/compare_bedfiles.py", 
            str(file3),
            str(file4),
        ],
        capture_output=True,
        text=True,
        check=False
    )

    # Check the result of the subprocess run
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"

    # Check that the comparison output file was created
    output_folder = "bedfile_comparisons"
    output_file_name = f"comparison_{file3.name}_{file4.name}.txt"
    expected_output_file = Path(output_folder) / output_file_name
    assert expected_output_file.exists(), (
    f"Expected output file {expected_output_file} was not created."
    )

    # Read the content of the output file and check that no differences are reported
    with open(expected_output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Present in file3.bed only" not in content
        assert "Present in file4.bed only" not in content

    # Clean up the output file after testing
    expected_output_file.unlink(missing_ok=True)
