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

import pytest
import os
import shutil
import subprocess
import sys
from unittest import mock
from unittest.mock import patch, MagicMock
from pathlib import Path
from io import StringIO
from PanelPal.accessories import variant_validator_api_functions, panel_app_api_functions
from PanelPal.generate_bed import main, parse_arguments


#####################
#     Unit Tests    #
#####################


class TestValidArguments:
    def test_valid_arguments(self):
        with mock.patch('builtins.input', return_value='n'):
            try:
                main(panel_id="R169", panel_version="1.1", genome_build="GRCh38")
            except Exception as e:
                pytest.fail(f"Main function raised an exception: {e}")

    def test_generate_bed_valid_arguments(self):
        with mock.patch('builtins.input', return_value='n'):
            try:
                main(panel_id="R169", panel_version="1.1", genome_build="GRCh37")
            except Exception as e:
                pytest.fail(f"Main function raised an exception: {e}")


class TestInvalidArguments:
    def test_missing_required_arguments(self):
        with mock.patch('sys.argv', new=["generate_bed.py"]):
            with pytest.raises(SystemExit) as exc_info:
                with mock.patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                    parse_arguments()
            assert exc_info.value.code != 0
            assert "the following arguments are required" in mock_stderr.getvalue()

    def test_missing_single_argument(self):
        with mock.patch('sys.argv', new=["generate_bed.py", "-p", "R207", "-v", "4"]):
            with pytest.raises(SystemExit) as exc_info:
                with mock.patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                    parse_arguments()
            assert exc_info.value.code != 0
            assert "the following arguments are required: -g/--genome_build" in mock_stderr.getvalue()

    def test_invalid_genome_build(self):
        with mock.patch('sys.argv', new=["generate_bed.py", "-p", "R207", "-v", "4", "-g", "INVALID_GENOME"]):
            with pytest.raises(SystemExit) as exc_info:
                with mock.patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                    parse_arguments()
            assert exc_info.value.code != 0
            assert "invalid choice: 'INVALID_GENOME' " "(choose from 'GRCh37', 'GRCh38')" in mock_stderr.getvalue(
            )

    def test_empty_panel_id(self):
        with mock.patch("sys.argv", new=["generate_bed.py", "-p", "", "-v", "4", "-g", "GRCh38"]):
            with mock.patch("builtins.input", return_value="n"):
                with mock.patch("PanelPal.generate_bed.logger") as mock_logger:
                    try:
                        main()
                    except Exception:
                        mock_logger.error.assert_called_with(
                            "Invalid panel_id '%s'. Panel ID must start with 'R' followed by digits (e.g., 'R207').",
                            ''
                        )


class TestArgumentParsing:
    @mock.patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments(self, mock_parse_args):
        mock_parse_args.return_value = mock.MagicMock(
            panel_id="R169", panel_version="1", genome_build="GRCh37"
        )
        args = parse_arguments()
        assert args.panel_id == "R169"
        assert args.panel_version == "1"
        assert args.genome_build == "GRCh37"
        mock_parse_args.assert_called_once()


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
        assert parsed_args.panel_version == 4.0
        assert parsed_args.genome_build == "GRCh38"
        assert parsed_args.status_filter == "green"  # Checks default value

    def test_parse_arguments_missing_argument(self):
        """
        Test parse_arguments() when a required argument is missing.
        """
        test_args = ["script_name", "-p", "R207",
                     "-v", "4"]  # Missing genome_build argument
        with patch.object(sys, 'argv', test_args), pytest.raises(SystemExit):
            parse_arguments()  # Should raise a SystemExit

    def test_parse_arguments_invalid_genome_build(self):
        """
        Test parse_arguments() with an invalid genome_build.
        """
        test_args = ["script_name", "-p", "R207",
                     "-v", "4", "-g", "INVALID_GENOME"]
        with patch.object(sys, 'argv', test_args), pytest.raises(SystemExit):
            parse_arguments()  # Should raise a SystemExit

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
        test_args = ["script_name", "-p", "R207",
                     "-v", "4", "-g", "GRCh38", "-f", "invalid"]
        with patch.object(sys, 'argv', test_args), pytest.raises(SystemExit):
            parse_arguments()  # Should raise a SystemExit

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

        simulated_input = 'n\n'  # simulate user skipping addition to databas

        try:
            # Change to temporary working dir
            os.chdir(temp_dir)

            # Run script as subprocess with the simulated input (n)
            result = subprocess.run(
                [
                    sys.executable,
                    str(new_script_path),
                    "-p", "R219",
                    "-v", "1.0",
                    "-g", "GRCh38"
                ],
                input=simulated_input,
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PYTHONPATH": str(original_cwd)}
            )

            # Assert successful execution
            assert result.returncode == 0, f"Script failed with error: {
                result.stderr}"

        finally:
            # Clean up the temporary directory after the test
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir)


class TestGenerateBedExceptionHandling:
    '''
    Tests for handling errors in the process of generating bed files.
    '''

    def test_generate_bed_exception_handling(self):
        """
        Test that exceptions are handled properly when functions fail.
        """
        panel_id = "R219"
        panel_version = "1.0"
        genome_build = "GRCh38"

        # Simulate command-line arguments
        with mock.patch('PanelPal.generate_bed.parse_arguments', return_value=mock.MagicMock(
                panel_id=panel_id, panel_version=panel_version, genome_build=genome_build)):

            # Mock PanelApp API error
            with mock.patch.object(panel_app_api_functions, "get_response", side_effect=Exception("PanelApp API error")):
                # Mock input to prevent reading from stdin
                with mock.patch('builtins.input', return_value='n'):
                    with pytest.raises(Exception, match="PanelApp API error"):
                        main()


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
        bed_file_path = temp_dir / \
            f"{panel_id}_v{panel_version}_{genome_build}.bed"
        bed_merged_path = temp_dir / \
            f"{panel_id}_v{panel_version}_{genome_build}_merged.bed"

        # Create a dummy BED file to simulate it already exists
        bed_file_path.write_text("Dummy content")

        # Save the current working directory
        original_cwd = Path(os.getcwd())
        new_script_path = Path(original_cwd) / "PanelPal/generate_bed.py"

        try:
            # Change the working directory to the temporary directory
            os.chdir(temp_dir)

            # Mock input to simulate the user typing 'n' to stop
            # Simulate user input 'n' followed by Enter
            with mock.patch('builtins.input', return_value='n\n'):
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
        bed_file_path = temp_dir / \
            f"{panel_id}_v{panel_version}_{genome_build}.bed"
        bed_merged_path = temp_dir / \
            f"{panel_id}_v{panel_version}_{genome_build}_merged.bed"

        # Ensure the BED file does not exist
        if bed_file_path.exists():
            bed_file_path.unlink()

        # Save the current working directory
        original_cwd = Path(os.getcwd())
        new_script_path = Path(original_cwd) / "PanelPal/generate_bed.py"

        try:
            # Change the working directory to the temporary directory
            os.chdir(temp_dir)

            # Mock input to simulate the user typing 'n' to stop
            # Simulate user input 'n' followed by Enter
            with mock.patch('builtins.input', return_value='n\n'):
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

    @patch("PanelPal.generate_bed.bed_file_exists")
    @patch("PanelPal.generate_bed.parse_arguments")
    @patch("PanelPal.generate_bed.logger")
    def test_bed_file_exists_halts(self, mock_logger, mock_parse_arguments, mock_bed_file_exists):
        """
        Test that the main function stops execution when the BED file already exists.
        """
        # Mock the arguments
        mock_parse_arguments.return_value = MagicMock(
            panel_id="R207",
            panel_version="4.0",
            genome_build="GRCh38"
        )

        # Mock bed_file_exists to return True
        mock_bed_file_exists.return_value = True

        # Mock input to simulate the user typing 'n' to stop
        with mock.patch('builtins.input', return_value='n\n'):
            # Call the main function
            main()

        # Assert logger.warning is called
        mock_logger.warning.assert_called_once_with(
            "Process stopping: BED file already exists for panel_id=%s, "
            "panel_version=%s, genome_build=%s.",
            "R207",
            "4.0",
            "GRCh38",
        )

    @patch("PanelPal.generate_bed.bed_file_exists")
    @patch("PanelPal.generate_bed.parse_arguments")
    @patch("PanelPal.generate_bed.logger")
    def test_no_existance_continues(self, mock_logger, mock_parse_arguments, mock_bed_file_exists):
        """
        Test that the main function continues execution when the BED file does not exist.
        """
        # Mock the arguments
        mock_parse_arguments.return_value = MagicMock(
            panel_id="R207",
            panel_version="4.0",
            genome_build="GRCh38"
        )

        # Mock bed_file_exists to return False
        mock_bed_file_exists.return_value = False

        # Mock dependent function calls to prevent actual execution
        with patch("PanelPal.generate_bed.panel_app_api_functions.get_response"), \
                patch("PanelPal.generate_bed.panel_app_api_functions.get_response_old_panel_version"), \
                patch("PanelPal.generate_bed.panel_app_api_functions.get_genes", return_value=[]), \
                patch("PanelPal.generate_bed.variant_validator_api_functions.generate_bed_file"), \
                patch("PanelPal.generate_bed.variant_validator_api_functions.bedtools_merge"), \
                patch("PanelPal.generate_bed.bed_head"):

            # Mock input to simulate the user typing 'n' to stop
            with mock.patch('builtins.input', return_value='n\n'):
                # Call the main function
                main()

        # Assert logger.debug is called
        mock_logger.debug.assert_any_call(
            "No existing BED file found. Proceeding with generation."
        )
