"""
Module for testing functions related to BED file handling in the
PanelPal package.

This module contains tests for various functions that manage and
manipulate BED files. The tests ensure the correctness of functions
that check for the existence of BED files, read BED files, and compare
the contents of two BED files.

Tested Functions:
-----------------
1. `bed_file_exists`: Tests for existence of a BED file based on panel
   name, version, and genome build.
2. `read_bed_file`: Tests for reading a BED file and parsing its content.
3. `compare_bed_files`: Tests for comparing two BED files and outputting
   their differences.
4. `bed_head`: Tests for generating and prepending a metadata header to
   a BED file, including handling different scenarios such as normal files,
   merged files, and error handling.

Classes:
--------
- `TestBedFileExists`: Contains tests for the `bed_file_exists` function.
- `TestsReadBedFile`: Contains tests for the `read_bed_file` function.
- `TestsCompareBedFunction`: Contains tests for the `compare_bed_files`
   function.
- `TestBedHeadFunction`: Contains tests for the `bed_head` function, which
   generates and adds a metadata header to a BED file.

Testing Scenarios:
------------------
- Verifying that the `bed_file_exists` function detects existing files
  and handles missing parameters.
- Testing the correct reading and parsing of a BED file with the
  `read_bed_file` function.
- Comparing the contents of two BED files using the `compare_bed_files`
  function, including handling differences and identical files.
- Handling various edge cases such as missing files, file reading errors,
  and folder creation failures.
- Verifying the correct addition of headers to normal and merged BED files
  using `bed_head`, and checking error handling for file not found,
  permission errors, IO errors, and unexpected exceptions.
"""

import os
from datetime import datetime
from unittest.mock import patch, mock_open
from pathlib import Path
import pytest
from PanelPal.accessories.bedfile_functions import (compare_bed_files,
                                                    read_bed_file,
                                                    bed_file_exists,
                                                    bed_head
                                                    )


class TestBedFileExists:
    '''
    Test for the function which checks whether a bed file exists
    '''

    def test_bed_file_exists(self):
        """
        Test bed_file_exists to verify it correctly detects existing files.
        """
        # Define temporary directory
        temp_dir = Path("tmp/")
        temp_dir.mkdir(parents=True, exist_ok=True)
        original_cwd = Path(os.getcwd())  # Save the current working directory

        try:
            # Create a temporary BED file with the expected name
            panel_name = "R207"
            panel_version = "4"
            genome_build = "GRCh38"
            bed_file = temp_dir / \
                f"{panel_name}_v{panel_version}_{genome_build}.bed"
            bed_file.write_text("dummy content")  # Writing content to the file

            os.chdir(temp_dir)  # Change to the temp directory

            # Verify the file is detected
            assert bed_file_exists(panel_name, panel_version, genome_build) is True, \
                f"Expected {bed_file} to exist but it was not detected."

            # Verify a non-existent file is not detected
            assert bed_file_exists("Nonexistent", "1", genome_build) is False, \
                "Non-existent file was incorrectly detected."

            if bed_file.exists():
                bed_file.unlink()

        finally:
            os.chdir(original_cwd)

    def test_bed_file_exists_missing_parameters(self):
        """
        Test for missing parameters in bed_file_exists
        """
        with pytest.raises(ValueError):
            bed_file_exists(None, "v1", "GRCh38")

        with pytest.raises(ValueError):
            bed_file_exists("Panel1", None, "GRCh38")

        with pytest.raises(ValueError):
            bed_file_exists("Panel1", "v1", None)

    def test_all_missing_parameters(self):
        """
        Ensure ValueError is raised when all parameters are missing.
        """
        with pytest.raises(ValueError, match="Panel name, panel version, or genome build missing."):
            bed_file_exists(None, None, None)

    @patch("PanelPal.accessories.bedfile_functions.logger")
    def test_value_error_in_try_block(self, mock_logger):
        """
        Ensure a ValueError raised inside the try block is logged and re-raised.
        """
        with patch("os.path.isfile", side_effect=ValueError("Mocked ValueError")):
            with pytest.raises(ValueError, match="Mocked ValueError"):
                bed_file_exists("Panel1", "v1", "GRCh38")

        # Verify the error was logged with the exception object
        mock_logger.error.assert_called_once_with("Invalid arguments provided: %s",
                                                  "Mocked ValueError")

    @patch("PanelPal.accessories.bedfile_functions.logger")
    def test_generic_exception_in_try_block(self, mock_logger):
        """
        Ensure a generic Exception raised inside the try block is logged
        and re-raised.
        """
        with patch("os.path.isfile", side_effect=Exception("Mocked Exception Error")):
            with pytest.raises(Exception, match="Mocked Exception Error"):
                bed_file_exists("Panel1", "v1", "GRCh38")

        # Verify the error was logged with the exception object
        mock_logger.error.assert_called_once_with("An unexpected error occurred: %s",
                                                  "Mocked Exception Error")


class TestsReadBedFile:
    '''
    Tests for the function which reads bed files.
    '''

    def test_read_bed_file(self):
        """
        Test read_bed_file to ensure it parses BED files correctly.
        """
        # Define temporary directory
        temp_dir = Path("tmp/")
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Create a temporary BED file
            bed_content = """# Header line
    chr1\t100\t200
    chr2\t150\t250
    """
            bed_file = temp_dir / "test.bed"
            bed_file.write_text(bed_content)

            # Read the file and verify the content
            expected_entries = sorted(["chr1_100_200", "chr2_150_250"])
            result = read_bed_file(str(bed_file))
            assert result == expected_entries, \
                f"Expected {expected_entries}, but got {result}"

        finally:
            # Clean up
            if bed_file.exists():
                bed_file.unlink()

    @patch("PanelPal.accessories.bedfile_functions.logger")
    @patch("os.path.isfile")
    def test_file_not_found(self, mock_isfile, mock_logger):
        """
        Test FileNotFoundError when the file does not exist.
        """
        mock_isfile.return_value = False

        with pytest.raises(FileNotFoundError,
                           match="The file non_existent.bed does not exist."):
            read_bed_file("non_existent.bed")

        mock_logger.error.assert_called_once_with(
            "File not found: %s", "The file non_existent.bed does not exist.")

    @patch("PanelPal.accessories.bedfile_functions.logger")
    @patch("os.path.isfile")
    def test_unexpected_error(self, mock_isfile, mock_logger):
        """
        Test handling of unexpected errors.
        """
        mock_isfile.return_value = True

        # Simulate an unexpected error during file opening
        with patch("builtins.open", side_effect=RuntimeError("Unexpected error")):
            with pytest.raises(RuntimeError, match="Unexpected error"):
                read_bed_file("unexpected_error.bed")

        mock_logger.error.assert_called_once_with(
            "An unexpected error occurred while reading '%s': %s",
            "unexpected_error.bed",
            "Unexpected error"
        )


class TestsCompareBedFunction:
    '''
    Tests for the function that compares the contents of two bed files.
    '''
    @pytest.fixture
    def temp_bed_files(self):
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
        with open(file2_path, 'w', encoding='utf-8') as f:
            f.write("13\t48877886\t48878185\tRB1_NM_000321.3_exon1\n")
            f.write("13\t48881415\t48881542\tRB1_NM_000321.3_exon2\n")
            f.write("13\t48916734\t48916850\tRB1_NM_000321.3_exon3\n")
            # Different
            f.write("13\t48919500\t48919600\tRB1_NM_000321.3_exon5\n")

        yield file1_path, file2_path

        # Cleanup temporary files
        if file1_path.exists():
            file1_path.unlink()
        if file2_path.exists():
            file2_path.unlink()

    def test_compare_bed_files(self, temp_bed_files):
        """
        Test the `compare_bed_files` function to ensure the differences
        are written correctly.
        """
        # Extract the paths from the fixture
        file1, file2 = temp_bed_files

        # Call the compare_bed_files function
        compare_bed_files(str(file1), str(file2))

        # Define expected output file name
        output_folder = "bedfile_comparisons"
        output_file_name = f"comparison_{file1.name}_{file2.name}.txt"
        expected_output_file = Path(output_folder) / output_file_name

        # Ensure that the output file is created
        assert expected_output_file.exists(), \
            f"Expected output file {expected_output_file} was not created."

        # Check the content of the output file
        with open(expected_output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Assert that entries unique to file1 are marked correctly
            assert "RB1_NM_000321.3_exon4" in content
            assert "Present in tmp/file1.bed only" in content
            # Assert that entries unique to file2 are marked correctly
            assert "RB1_NM_000321.3_exon5" in content
            assert "Present in tmp/file2.bed only" in content

        # Clean up the output file after testing
        expected_output_file.unlink(missing_ok=True)

    @pytest.fixture
    def temp_identical_bed_files(self):
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

    def test_identical_bed_files(self, temp_identical_bed_files):
        """
        Test the comparison function when both BED files are identical.
        """
        # Extract the paths from the fixture
        file3, file4 = temp_identical_bed_files

        # Call the compare_bed_files function
        compare_bed_files(str(file3), str(file4))

        # Define expected output file name
        output_folder = "bedfile_comparisons"
        output_file_name = f"comparison_{file3.name}_{file4.name}.txt"
        expected_output_file = Path(output_folder) / output_file_name

        # Ensure that the output file is created
        assert expected_output_file.exists(), \
            f"Expected output file {expected_output_file} was not created."

        # Check that no differences are reported for identical files
        with open(expected_output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Present in tmp/file3.bed only" not in content
            assert "Present in tmp/file4.bed only" not in content

        # Clean up the output file after testing
        expected_output_file.unlink(missing_ok=True)

    @pytest.fixture
    def temp_missing_bed_file(self):
        """
        Fixture to simulate a missing BED file scenario.
        """
        temp_dir = Path("tmp/")
        missing_file_path = temp_dir / "missing_file.bed"
        yield missing_file_path

    def test_missing_bed_file(self, temp_missing_bed_file):
        """
        Test that the function raises a FileNotFoundError when a BED
        file is missing.
        """
        with pytest.raises(FileNotFoundError):
            compare_bed_files(str(temp_missing_bed_file),
                              "some_other_file.bed")

    @pytest.fixture
    def temp_nonexistent_bed_files(self):
        """
        Fixture to simulate non-existent BED files for testing.
        """
        # Define file paths that do not exist
        non_existent_file1 = Path("tmp/non_existent_file1.bed")
        non_existent_file2 = Path("tmp/non_existent_file2.bed")

        yield non_existent_file1, non_existent_file2

    @patch("PanelPal.accessories.bedfile_functions.logger")
    def test_file_not_found_error(self, mock_logger):
        """
        Ensure that the logger is called when one or both input files do not exist
        and raises a FileNotFoundError.
        """
        with pytest.raises(FileNotFoundError, match="One or both input files do not exist."):
            compare_bed_files("non_existent_file1.bed", "existing_file2.bed")

        mock_logger.error.assert_any_call(
            "Input file does not exist: %s", "non_existent_file1.bed"
        )
        mock_logger.error.assert_any_call(
            "Input file does not exist: %s", "existing_file2.bed"
        )

        # Simulate the scenario where file2 does not exist, but file1 does
        with pytest.raises(FileNotFoundError, match="One or both input files do not exist."):
            compare_bed_files("existing_file1.bed", "non_existent_file2.bed")

        mock_logger.error.assert_any_call(
            "Input file does not exist: %s", "existing_file1.bed"
        )
        mock_logger.error.assert_any_call(
            "Input file does not exist: %s", "non_existent_file2.bed"
        )

    @patch("builtins.open", side_effect=OSError("Disk full"))
    @patch("os.path.exists", return_value=True)  # Prevent FileNotFoundError
    @patch("PanelPal.accessories.bedfile_functions.logger")
    def test_os_error_handling(self, mock_logger, mock_exists, mocked_open, temp_bed_files):
        """
        Test handling of OSError when writing to the output file, using real temporary BED files.
        """
        file1, file2 = temp_bed_files

        # Mock read_bed_file to return some dummy data without actually opening the file
        with patch("PanelPal.accessories.bedfile_functions.read_bed_file") as mock_read_bed_file:
            mock_read_bed_file.side_effect = [
                [frozenset([("chrom", "chr1"), ("start", 100), ("end", 200)])],
                [frozenset([("chrom", "chr2"), ("start", 150), ("end", 250)])],
            ]

            # Test that OSError is raised during the comparison process
            with pytest.raises(OSError, match="Disk full"):
                compare_bed_files(str(file1), str(file2))

            # Verify that both expected error log calls were made
            mock_logger.error.assert_any_call(
                "Failed to write to output file '%s': %s",
                'bedfile_comparisons/comparison_file1.bed_file2.bed.txt',
                'Disk full'
            )

            mock_logger.error.assert_any_call(
                'Error: %s', 'Disk full'
            )

    @patch("os.path.exists",
           side_effect=lambda path: path in ["tmp/file1.bed", "tmp/file2.bed"])
    # Simulate successful folder creation
    @patch("os.makedirs", return_value=None)
    @patch("PanelPal.accessories.bedfile_functions.logger")
    def test_create_output_folder_success(self, mock_logger, mock_makedirs,
                                          mock_exists, temp_bed_files):
        """
        Test that the function successfully creates the output folder if it does not exist.
        """
        file1, file2 = temp_bed_files  # Extract temporary BED files

        # Call the function
        compare_bed_files(str(file1), str(file2))

        # Verify folder creation was attempted
        mock_makedirs.assert_called_once_with("bedfile_comparisons")
        mock_logger.debug.assert_any_call("Creating output folder: %s",
                                          "bedfile_comparisons")

    @patch("os.path.exists",  # file exists, folder does not
           side_effect=lambda path: path in ["tmp/file1.bed", "tmp/file2.bed"])
    @patch("os.makedirs", side_effect=OSError("Permission denied"))
    @patch("PanelPal.accessories.bedfile_functions.logger")
    def test_create_output_folder_failure(self, mock_logger, mock_makedirs,
                                          mock_exists, temp_bed_files):
        """
        Test that the function handles errors when folder creation fails due to OSError.
        """
        file1, file2 = temp_bed_files  # Extract temporary BED files

        # Call the function and ensure an OSError is raised
        with pytest.raises(OSError, match="Permission denied"):
            compare_bed_files(str(file1), str(file2))

        # Verify that the error was logged
        mock_logger.error.assert_any_call(
            "Failed to create output folder '%s': %s", "bedfile_comparisons", "Permission denied"
        )

        mock_logger.error.assert_any_call(
            'Error: %s', 'Permission denied'
        )


class TestBedHeadFunction:
    '''
    Unit tests for the function bed_head(), which adds a hashed out
    header to bed files.
    '''
    @patch("PanelPal.accessories.bedfile_functions.open",
           new_callable=mock_open,
           read_data="Existing content"
           )
    @patch("PanelPal.accessories.bedfile_functions.logger")
    def test_bed_head_normal_file(self, mock_logger, mock_open_file):
        """
        Test header generation for a normal BED file (not merged).
        """
        panel_id = "R207"
        panel_version = "4.0"
        genome_build = "GRCh38"
        num_genes = 100
        bed_filename = "panel.bed"

        # Call the function
        bed_head(panel_id, panel_version,
                 genome_build, num_genes, bed_filename)

        # Verify header generation
        date_generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # fmt: off
        expected_header = (
            f"# BED file generated for panel: {panel_id} (Version: {panel_version}). "
            f"Date of creation: {date_generated}.\n"
            f"# Genome build: {genome_build}. Number of genes: {num_genes}.\n"
            f"# BED file: {bed_filename}\n"  # Fixed format here
            "# Columns: chrom, chromStart, chromEnd, exon_number|transcript|gene symbol\n"
        )
        # fmt: on
        mock_open_file().write.assert_called_once_with(
            expected_header + "Existing content")

        # Assert logging
        mock_logger.info.assert_called_once_with(
            "Header successfully added to %s", f"{bed_filename}")

    @patch("PanelPal.accessories.bedfile_functions.open",
           new_callable=mock_open,
           read_data="Existing content"
           )
    @patch("PanelPal.accessories.bedfile_functions.logger")
    def test_bed_head_merged_file(self, mock_logger, mock_open_file):
        """
        Test header generation for a merged BED file.
        """
        panel_id = "R207"
        panel_version = "4.0"
        genome_build = "GRCh38"
        num_genes = 50
        bed_filename = "panel_merged.bed"

        # Call the function
        bed_head(panel_id, panel_version,
                 genome_build, num_genes, bed_filename)

        # Verify header generation
        date_generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # fmt: off
        expected_header = (
            f"# Merged BED file generated for panel: {panel_id} (Version: {panel_version}) "
            f"Date of creation: {date_generated}.\n"
            f"# Genome build: {genome_build}. Number of genes: {num_genes}\n"
            f"# Merged BED file: {bed_filename}\n"
            "# Columns: chrom, chromStart, chromEnd \n"
            "# Note: for exon and gene details, see the original BED file.\n"
        )
        # fmt: on
        mock_open_file().write.assert_called_once_with(
            expected_header + "Existing content"
        )

        # Assert logging
        mock_logger.info.assert_called_once_with(
            "Header successfully added to %s", f"{bed_filename}"
        )

    @patch("PanelPal.accessories.bedfile_functions.open",
           side_effect=FileNotFoundError("File not found")
           )
    @patch("PanelPal.accessories.bedfile_functions.logger")
    def test_bed_head_file_not_found(self, mock_logger, mock_open_file):
        """
        Test FileNotFoundError handling.
        """
        with pytest.raises(FileNotFoundError):
            bed_head("R207", "4.0", "GRCh38", 100, "nonexistent.bed")

        call_args = mock_logger.error.call_args
        # Access exc_info from kwargs
        exc_info = call_args[1].get('exc_info', None)
        assert exc_info is True  # Ensure exc_info was passed
        assert "File %s not found" in call_args[0][0]  # Check error message

    @patch("PanelPal.accessories.bedfile_functions.open",
           side_effect=PermissionError("Permission denied")
           )
    @patch("PanelPal.accessories.bedfile_functions.logger")
    def test_bed_head_permission_error(self, mock_logger, mock_open_file):
        """
        Test PermissionError handling.
        """
        with pytest.raises(PermissionError):
            bed_head("R207", "4.0", "GRCh38", 100, "restricted.bed")

        # Check that the exception was logged with the expected message
        call_args = mock_logger.error.call_args
        exc_info = call_args[1].get('exc_info', None)  # Access exc_info
        assert exc_info is True  # Ensure exc_info=True was passed
        assert "Permission denied when accessing %s" in call_args[0][0]

    @patch("PanelPal.accessories.bedfile_functions.open",
           side_effect=IOError("General IO error")
           )
    @patch("PanelPal.accessories.bedfile_functions.logger")
    def test_bed_head_io_error(self, mock_logger, mock_open_file):
        """
        Test IOError handling.
        """
        with pytest.raises(IOError):
            bed_head("R207", "4.0", "GRCh38", 100, "ioerror.bed")

        # Check that the exception was logged with the expected message
        call_args = mock_logger.error.call_args
        # Access exc_info from kwargs
        exc_info = call_args[1].get('exc_info', None)
        assert exc_info is True  # Ensure exc_info=True was passed
        assert "IOError while processing %s" in call_args[0][0]

    @patch("PanelPal.accessories.bedfile_functions.open",
           side_effect=Exception("Unexpected error")
           )
    @patch("PanelPal.accessories.bedfile_functions.logger")
    def test_bed_head_unexpected_error(self, mock_logger, mock_open_file):
        """
        Test general exception handling.
        """
        with pytest.raises(Exception):
            bed_head("R207", "4.0", "GRCh38", 100, "unexpected.bed")

        # Check that the exception was logged with the expected message
        call_args = mock_logger.error.call_args
        # Access exc_info from kwargs
        exc_info = call_args[1].get('exc_info', None)
        assert exc_info is True  # Ensure exc_info=True was passed
        assert "Unexpected error while adding header to %s" in call_args[0][0]
