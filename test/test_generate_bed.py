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
from unittest.mock import patch
from PanelPal.generate_bed import main, parse_arguments


def test_valid_arguments():
    """
    Test script behavior with valid arguments.
    """
    with mock.patch('builtins.input', return_value='n'):  # Mock input() to return 'n'
        try:
            main(panel_id="R169", panel_version="1", genome_build="GRCh37")
        except Exception as e:
            pytest.fail(f"Main function raised an exception: {e}")


def test_missing_required_arguments():
    """Test missing required arguments"""
    result = subprocess.run(
        ["python3", "PanelPal/generate_bed.py"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode != 0
    assert "the following arguments are required" in result.stderr


def test_missing_single_argument():
    """Test missing a single required argument"""
    result = subprocess.run(
        ["python3", "PanelPal/generate_bed.py", "-p", "R207", "-v", "4"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode != 0
    assert "the following arguments are required: -g/--genome_build" in result.stderr


def test_invalid_genome_build():
    """Test with an invalid genome build"""
    result = subprocess.run(
        [
            "python3", "PanelPal/generate_bed.py",
            "-p", "R207", "-v", "4", "-g", "INVALID_GENOME"
        ],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode != 0
    assert "invalid choice: 'INVALID_GENOME' (choose from 'GRCh37', 'GRCh38')" in result.stderr


def test_edge_case_empty_panel_id():
    """Test with an empty panel_id"""
    with patch("builtins.input", return_value="test_patient_info"):
        result = subprocess.run(
            ["python3", "PanelPal/generate_bed.py",
                "-p", "", "-v", "4", "-g", "GRCh38"],
            capture_output=True,
            text=True,
            check=False
        )

    assert result.returncode != 0
    assert "An error occurred in the BED file generation process" in result.stderr


def test_generate_bed_exception_handling():
    """
    Test exception handling works as expected.
    """
    # Mock parsing of command-line arguments
    with mock.patch('PanelPal.generate_bed.parse_arguments', return_value=mock.MagicMock(
            panel_id="R207", panel_version="4", genome_build="GRCh38")):

        # Test for invalid arguments (e.g., missing panel_id)
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            subprocess.run(
                [sys.executable, "PanelPal/generate_bed.py", "-p",
                    "R219"],  # Missing genome build and version
                capture_output=True, text=True, check=True
            )

        # Check that it returned 2 errors
        assert exc_info.value.returncode == 2

        # Check that stderr contains expected error message
        assert "error: the following arguments are required: -v/--panel_version, -g/--genome_build" in exc_info.value.stderr


def test_invalid_genome_build():
    """Test with an invalid genome build"""
    result = subprocess.run(
        [
            "python3", "PanelPal/generate_bed.py",
            "-p", "R207", "-v", "4", "-g", "asdf"
        ],
        capture_output=True,
        text=True,
        check=False
    )

    # Check for non-zero exit
    assert result.returncode != 0

    # Check that stderr contains expected error message
    assert "argument -g/--genome_build: invalid choice: 'asdf' (choose from 'GRCh37', 'GRCh38')" in result.stderr


def test_generate_bed_valid_arguments():
    """
    Tests the main function with valid arguments, simulating 'n' input to skip prompts.
    """
    with patch('builtins.input', return_value='n'):
        try:
            # Run the main function with valid arguments
            main(panel_id="R169", panel_version="1", genome_build="GRCh37")
        except Exception as e:
            pytest.fail(f"Main function raised an exception: {e}")


@patch('argparse.ArgumentParser.parse_args')
def test_parse_arguments(mock_parse_args):
    """
    Mock the return value of parse_args
    """
    mock_parse_args.return_value = mock.MagicMock(
        panel_id="R169", panel_version="1", genome_build="GRCh37"
    )

    # Call parse_arguments and check its return value
    args = parse_arguments()

    # Validate the expected arguments
    assert args.panel_id == "R169"
    assert args.panel_version == "1"
    assert args.genome_build == "GRCh37"

    # Check that parse_args was called
    mock_parse_args.assert_called_once()
