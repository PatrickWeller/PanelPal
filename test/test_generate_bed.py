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
import pytest
from PanelPal.accessories import variant_validator_api_functions, panel_app_api_functions
from PanelPal.generate_bed import main


def test_missing_required_arguments():
    """
    Test script behavior when all arguments are missing.
    """
    result = subprocess.run(
        [sys.executable, "PanelPal/generate_bed.py"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode != 0
    assert "the following arguments are required" in result.stderr


def test_missing_single_argument():
    """
    Test script behavior when a single argument is missing.
    """
    result = subprocess.run(
        [sys.executable, "PanelPal/generate_bed.py", "-p", "R207", "-v", "4"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode != 0
    assert "the following arguments are required: -g/--genome_build" in result.stderr


def test_invalid_genome_build():
    """
    Test script behavior with invalid genome build.
    """
    result = subprocess.run(
        [
            sys.executable,
            "PanelPal/generate_bed.py",
            "-p", "R207",
            "-v", "4",
            "-g", "INVALID_GENOME"
        ],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode != 0
    assert "invalid choice: 'INVALID_GENOME' (choose from 'GRCh37', 'GRCh38')" in result.stderr


def test_valid_arguments():
    """
    Test script behavior with valid arguments.
    """
    # Define temporary directory
    temp_dir = Path("tmp/")

    # Ensure the directory exists
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Save the current working directory
    original_cwd = Path(os.getcwd())
    script_path = Path(original_cwd) / "PanelPal/generate_bed.py"

    try:
        # Mock the input function to return predefined responses
        with mock.patch('builtins.input', return_value='n'):
            # Change the working directory to tmp_path
            os.chdir(temp_dir)

            # Redirect stdout to suppress output
            with open(os.devnull, 'w') as devnull:
                # Run the script as a subprocess, making sure stdin is piped
                result = subprocess.run(
                    [
                        sys.executable,
                        str(script_path),
                        "-p", "R219",
                        "-v", "1",
                        "-g", "GRCh38",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                    input='n',  # Mock the input here directly
                )

            # Assert successful execution, print error if not
            assert result.returncode == 0, \
                f"Script failed with error: {result.stderr}"

    finally:
        # Clean up: return to the original working directory
        os.chdir(original_cwd)


def test_generate_bed_exception_handling():
    """
    Test exception handling works as expected.
    """
    # Mocking the function that parses command-line arguments to simulate arguments passed
    with mock.patch('PanelPal.generate_bed.parse_arguments', return_value=mock.MagicMock(
            panel_id="R207", panel_version="4", genome_build="GRCh38")):

        # Test for invalid arguments (e.g., missing panel_id)
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            subprocess.run(
                [sys.executable, "PanelPal/generate_bed.py", "-p",
                    "R219"],  # Missing genome build and version
                capture_output=True, text=True, check=True
            )

        # Ensure the subprocess call resulted in a non-zero exit status
        assert exc_info.value.returncode == 2

        # Check the stderr for the expected error message
        assert "error: the following arguments are required: -v/--panel_version, -g/--genome_build" in exc_info.value.stderr
