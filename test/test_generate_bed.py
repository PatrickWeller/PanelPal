"""
Tests for the `generate_bed.py` script in the PanelPal module using
`pytest` and `unittest.mock`.

Tests include:

- Handling of missing or incomplete arguments
- Handling of invalid genome build
- Successful execution with valid arguments
- Exception handling for various error scenarios during execution
- Mocking logger to simulate errors and validate error handling
"""

import os
import subprocess
import sys
from pathlib import Path
from unittest import mock
from unittest.mock import patch
import pytest
from PanelPal.accessories import variant_validator_api_functions, panel_app_api_functions
from PanelPal.generate_bed import main, parse_arguments


#####################
#     Unit Tests    #
#####################

class TestParseArguments:
    
    def test_parse_arguments_valid(self):
        """
        Test parse_arguments() with valid arguments.
        """
        test_args = ["script_name", "-p", "R207", "-v", "4", "-g", "GRCh38"]
        with patch.object(sys, 'argv', test_args):
            parsed_args = parse_arguments()
        
        # Assert each argument is parsed as expected
        assert parsed_args.panel_id == "R207"
        assert parsed_args.panel_version == "4"
        assert parsed_args.genome_build == "GRCh38"
        assert parsed_args.status_filter == "green"  # Checks default value

    def test_parse_arguments_missing_argument(self):
        """
        Test parse_arguments() when a required argument is missing.
        """
        test_args = ["script_name", "-p", "R207", "-v", "4"]  # Missing genome_build argument
        with patch.object(sys, 'argv', test_args), pytest.raises(SystemExit):
            parse_arguments() # Should raise a SystemExit

    def test_parse_arguments_invalid_genome_build(self):
        """
        Test parse_arguments() with an invalid genome_build.
        """
        test_args = ["script_name", "-p", "R207", "-v", "4", "-g", "INVALID_GENOME"]
        with patch.object(sys, 'argv', test_args), pytest.raises(SystemExit):
            parse_arguments() # Should raise a SystemExit

    def test_parse_arguments_default_status_filter(self):
        """
        Test parse_arguments() with no status_filter argument (should default to 'green').
        """
        test_args = ["script_name", "-p", "R207", "-v", "4", "-g", "GRCh38"]
        with patch.object(sys, 'argv', test_args):
            parsed_args = parse_arguments()

         # Check that the default status_filter is correctly set.
        assert parsed_args.status_filter == "green"  # Default value

    def test_parse_arguments_invalid_status_filter(self):
        """
        Test parse_arguments() with an invalid status_filter argument.
        """
        test_args = ["script_name", "-p", "R207", "-v", "4", "-g", "GRCh38", "-f", "invalid"]
        with patch.object(sys, 'argv', test_args), pytest.raises(SystemExit):
            parse_arguments() # Should raise a SystemExit

####################
# Functional Tests #
####################

class TestGenerateBedArguments:
    '''
    Tests for the command line arguments of the main function to 
    generate a bed file.
    '''
    def test_missing_required_arguments(self):
        """
        Test script behavior when all arguments are missing.
        """
        original_cwd = Path(os.getcwd())
        result = subprocess.run(
            [sys.executable, "PanelPal/generate_bed.py"],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "PYTHONPATH": str(original_cwd)}
        )
        assert result.returncode != 0
        assert "the following arguments are required" in result.stderr


    def test_missing_single_argument(self):
        """
        Test script behavior when a single argument is missing.
        """
        original_cwd = Path(os.getcwd())
        result = subprocess.run(
            [sys.executable, "PanelPal/generate_bed.py", "-p", "R207", "-v", "4.0"],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "PYTHONPATH": str(original_cwd)}
        )
        assert result.returncode != 0
        assert "the following arguments are required: -g/--genome_build" in result.stderr

    def test_invalid_genome_build(self):
        """
        Test script behavior with invalid genome build.
        """
        original_cwd = Path(os.getcwd())

        result = subprocess.run(
            [
                sys.executable,
                "PanelPal/generate_bed.py",
                "-p", "R207",
                "-v", "4.0",
                "-g", "INVALID_GENOME"
            ],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "PYTHONPATH": str(original_cwd)}
        )
        assert result.returncode != 0
        assert "invalid choice: 'INVALID_GENOME' (choose from 'GRCh37', 'GRCh38')" in result.stderr

    def test_valid_arguments(self):
        """
        Test script behavior with valid arguments.
        """
        # Define temporary directory
        temp_dir = Path("tmp/")

        # Ensure the directory exists
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Save the current working directory
        original_cwd = Path(os.getcwd())
        new_script_path = Path(original_cwd) / "PanelPal/generate_bed.py"

        try:
            # Change the working directory to tmp_path
            os.chdir(temp_dir)

            # Run the script as a subprocess
            result = subprocess.run(
                [
                    sys.executable,
                    str(new_script_path),
                    "-p",
                    "R219",
                    "-v",
                    "1.0",
                    "-g",
                    "GRCh38",
                ],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PYTHONPATH": str(original_cwd)}
            )

            # Assert successful execution, print error if not
            assert result.returncode == 0, \
                f"Script failed with error: {result.stderr}"

            # Verify the expected file exists and is not empty
            expected_file = Path("R219_v1.0_GRCh38.bed")
            assert expected_file.exists(), \
                f"Expected output file {expected_file} was not created."
            assert expected_file.stat().st_size > 0, \
                f"File {expected_file} is empty."

            # Verify the expected file exists and is not empty
            expected_merged_file = Path("R219_v1.0_GRCh38_merged.bed")
            assert expected_merged_file.exists(), \
                f"Expected output file {expected_merged_file} was not created."
            assert expected_merged_file.stat().st_size > 0, \
                f"File {expected_merged_file} is empty."

            if expected_file.exists():
                expected_file.unlink()  # Deletes the file
            if expected_merged_file.exists():
                expected_merged_file.unlink()  # Deletes the merged file

        finally:
            # Restore the original working directory
            os.chdir(original_cwd)

class TestGenerateBedExceptionHandling:
    '''
    Tests the handling of errors and exceptions in the main function
    for generating bed files.
    '''
    # Test case for exception handling when the get_response function fails
    def test_generate_bed_exception_handling(self):
        """
        Test exception handling works as expected.
        """
        # Mocking the function that parses command-line arguments to simulate arguments passed
        with mock.patch('PanelPal.generate_bed.parse_arguments', return_value=mock.MagicMock(
            panel_id="R219", panel_version="1.0", genome_build="GRCh38")):

            # Mocking the functions used inside main() to simulate errors
            with mock.patch.object(
                panel_app_api_functions, "get_response",
                side_effect=Exception("PanelApp API error")
                ) as mock_get_response, \
                 mock.patch.object(
                    panel_app_api_functions, "get_response_old_panel_version"
                    ) as mock_get_response_old_panel_version, \
                mock.patch.object(
                    panel_app_api_functions, "get_genes"
                    ) as mock_get_genes, \
                mock.patch.object(
                    variant_validator_api_functions, "generate_bed_file"
                    ) as mock_generate_bed_file, \
                mock.patch.object(
                    variant_validator_api_functions, "bedtools_merge"
                    ) as mock_bedtools_merge:

                # Call the 'main' function and assert that it raises the expected exception
                with pytest.raises(Exception, match="PanelApp API error"):
                    main()

                # Check that the function that raised the error was called once
                mock_get_response.assert_called_once_with('R219')

                # Ensure other functions were not called after the exception
                mock_get_response_old_panel_version.assert_not_called()
                mock_get_genes.assert_not_called()
                mock_generate_bed_file.assert_not_called()
                mock_bedtools_merge.assert_not_called()

            # Test for exception handling when get_response_old_panel_version fails
            with mock.patch.object(
                panel_app_api_functions, "get_response",
                return_value=mock.MagicMock(json=mock.MagicMock(return_value={"id": "R219"}))
                ), \
                mock.patch.object(
                    panel_app_api_functions, "get_response_old_panel_version",
                    side_effect=Exception("Failed to fetch old panel version")
                    ) as mock_get_response_old_panel_version, \
                mock.patch.object(
                    panel_app_api_functions, "get_genes"
                    ) as mock_get_genes:

                with pytest.raises(Exception, match="Failed to fetch old panel version"):
                    main()

                # Ensure get_response_old_panel_version raised the error as expected
                mock_get_response_old_panel_version.assert_called_once_with("R219", "1.0")
                mock_get_genes.assert_not_called()

            # Test for exception handling when get_genes fails
            with mock.patch.object(
                panel_app_api_functions, "get_response",
                return_value=mock.MagicMock(json=mock.MagicMock(return_value={"id": "R219"}))
                ), \
                mock.patch.object(
                    panel_app_api_functions, "get_response_old_panel_version",
                    return_value=mock.MagicMock(json=mock.MagicMock(return_value={"genes": []}))
                    ) as mock_get_response_old_panel_version, \
                mock.patch.object(
                    panel_app_api_functions, "get_genes",
                    side_effect=Exception("Failed to retrieve genes.")) as mock_get_genes:

                with pytest.raises(Exception, match="Failed to retrieve genes."):
                    main()

                # Ensure the get_genes function raised the error as expected
                mock_get_genes.assert_called_once()

            # Test for exception handling when generate_bed_file fails
            with mock.patch.object(
                panel_app_api_functions, "get_response",
                return_value=mock.MagicMock(json=mock.MagicMock(return_value={"id": "R219"}))), \
                mock.patch.object(
                    panel_app_api_functions, "get_response_old_panel_version",
                    return_value=mock.MagicMock(json=mock.MagicMock(return_value={"genes": []}))), \
                mock.patch.object(
                    panel_app_api_functions, "get_genes",
                    return_value=["BRCA1", "TP53"]
                    ), \
                mock.patch.object(
                    variant_validator_api_functions, "generate_bed_file",
                    side_effect=Exception("BED file generation error")
                    ) as mock_generate_bed_file:

                with pytest.raises(Exception, match="BED file generation error"):
                    main()

                # Check that the generate_bed_file function raised the error as expected
                mock_generate_bed_file.assert_called_once()

            # Test the exception when bedtools_merge fails
            with mock.patch.object(
                panel_app_api_functions, "get_response",
                return_value=mock.MagicMock(json=mock.MagicMock(return_value={"id": "R219"}))), \
                mock.patch.object(
                    panel_app_api_functions, "get_response_old_panel_version",
                    return_value=mock.MagicMock(json=mock.MagicMock(return_value={"genes": []}))), \
                mock.patch.object(
                    panel_app_api_functions, "get_genes",
                    return_value=["BRCA1", "TP53"]
                    ), \
                mock.patch.object(
                    variant_validator_api_functions, "generate_bed_file"
                    ), \
                mock.patch.object(
                    variant_validator_api_functions, "bedtools_merge",
                    side_effect=Exception("Bedtools merge error")
                    ) as mock_bedtools_merge:

                with pytest.raises(Exception, match="Bedtools merge error"):
                    main()

                # Check that the bedtools_merge function raised the error as expected
                mock_bedtools_merge.assert_called_once()

class TestValidPanelCheck:
    '''
    Test that the logic works for checking the panel_id is valid.
    '''
    def test_invalid_panel_id(self):
        """
        Test that the script raises a ValueError and logs an error for an invalid panel_id.
        """
        panel_id = "X123"  # Invalid panel_id
        panel_version = "4.0"
        genome_build = "GRCh38"

        original_cwd = Path(os.getcwd())

        result = subprocess.run(
            [
                sys.executable,
                "PanelPal/generate_bed.py",
                "-p", panel_id,
                "-v", panel_version,
                "-g", genome_build
            ],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "PYTHONPATH": str(original_cwd)}
        )

        # Ensure that the script exits with an error code
        assert result.returncode != 0

        # Ensure that the error message for invalid panel_id is present in stderr
        assert f"Invalid panel_id '{panel_id}'" in result.stderr

class TestBedFileExists:
    '''
    Tests for the logic that checks if a bed file exists, and stops if
    it does or continues if it does not.
    '''
    def test_bed_file_exists(self):
        """
        Test that the script stops when the BED file exists.
        """
        panel_id = "R219"
        panel_version = "1.0"
        genome_build = "GRCh38"

        temp_dir = Path("tmp/")  # Temporary directory for bed files

        # Ensure the temporary directory exists
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Define the bed file path
        bed_file_path = temp_dir / f"{panel_id}_v{panel_version}_{genome_build}.bed"
        bed_merged_path = temp_dir / f"{panel_id}_v{panel_version}_{genome_build}_merged.bed"

        # Create a dummy BED file to simulate it already exists
        bed_file_path.write_text("Dummy content")

        # Save the current working directory
        original_cwd = Path(os.getcwd())
        new_script_path = Path(original_cwd) / "PanelPal/generate_bed.py"

        try:
            # Change the working directory to the temporary directory
            os.chdir(temp_dir)

            # Run the script and capture its output
            result = subprocess.run(
                [
                    sys.executable,
                    str(new_script_path),
                    "-p", panel_id,
                    "-v", panel_version,
                    "-g", genome_build
                ],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PYTHONPATH": str(original_cwd)}
            )

            # Ensure that the script exits with a warning
            assert result.returncode == 0
            assert "PROCESS STOPPED: A BED file for the panel" in result.stdout

        finally:
            # Restore the original working directory
            os.chdir(original_cwd)

        # Clean up the dummy BED file if it exists
        if bed_file_path.exists():
            bed_file_path.unlink()

        if bed_merged_path.exists():
            bed_merged_path.unlink()

    def test_bed_file_does_not_exist(self):
        """
        Test that the script proceeds to generate a BED file when it does not exist.
        """
        panel_id = "R219"
        panel_version = "1.0"
        genome_build = "GRCh37"

        # Ensure the temporary directory exists
        temp_dir = Path("tmp/")  # Temporary directory for bed files
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Define the bed file path
        bed_file_path = temp_dir / f"{panel_id}_v{panel_version}_{genome_build}.bed"
        bed_merged_path = temp_dir / f"{panel_id}_v{panel_version}_{genome_build}_merged.bed"

        # Ensure the BED file does not exist
        if bed_file_path.exists():
            bed_file_path.unlink()

        # Save the current working directory
        original_cwd = Path(os.getcwd())
        new_script_path = Path(original_cwd) / "PanelPal/generate_bed.py"

        try:
            # Change the working directory to the temporary directory
            os.chdir(temp_dir)

            # Run the script and capture its output
            result = subprocess.run(
                [
                    sys.executable,
                    str(new_script_path),
                    "-p", panel_id,
                    "-v", panel_version,
                    "-g", genome_build
                ],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PYTHONPATH": str(original_cwd)}
            )

            # Ensure that the script exits successfully
            assert result.returncode == 0

        finally:
            # Restore the original working directory
            os.chdir(original_cwd)

        # Clean up the dummy BED file if it exists
        if bed_file_path.exists():
            bed_file_path.unlink()

        if bed_merged_path.exists():
            bed_merged_path.unlink()
