import os
from unittest.mock import patch
from pathlib import Path
import pytest
from PanelPal.accessories.bedfile_functions import compare_bed_files, read_bed_file, bed_file_exists

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

        try:
            # Create a temporary BED file with the expected name
            panel_name = "R207"
            panel_version = "4"
            genome_build = "GRCh38"
            bed_file = temp_dir / f"{panel_name}_v{panel_version}_{genome_build}.bed"
            bed_file.write_text("dummy content")  # Writing content to the file

            original_cwd = Path(os.getcwd())  # Save the current working directory
            os.chdir(temp_dir)  # Change to the temp directory

            # Verify the file is detected
            assert bed_file_exists(panel_name, panel_version, genome_build) is True, \
                f"Expected {bed_file} to exist but it was not detected."

            # Verify a non-existent file is not detected
            assert bed_file_exists("Nonexistent", "1", genome_build) is False, \
                "Non-existent file was incorrectly detected."

        finally:
            os.chdir(original_cwd)
            
        if bed_file.exists():
                bed_file.unlink()

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
            f.write("13\t48919500\t48919600\tRB1_NM_000321.3_exon5\n") # Different

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
    def test_os_error_handling(self, mock_logger, mock_exists, mock_open, temp_bed_files):
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
    @patch("os.makedirs", return_value=None)  # Simulate successful folder creation
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

    @patch("os.path.exists", # file exists, folder does not
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
