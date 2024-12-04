"""
Tests for the `generate_bed.py` script in the PanelPal module using
`pytest` and `unittest.mock`.

Tests include:

- Handling of missing or incomplete arguments
- Handling of invalid genome build
- Successful execution with valid arguments
- Exception handling for various error scenarios during execution
- Mocking logger to simulate errors and validate error handling

Fixtures:
- `mocked_logger_fixture`: Mocks the logger to capture output during tests.
"""

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
    # Run the script as a subprocess
    result = subprocess.run(
        [
            sys.executable,
            "PanelPal/generate_bed.py",
            "-p",
            "R219",
            "-v",
            "1",
            "-g",
            "GRCh38",
        ],
        capture_output=True,
        text=True,
        check=False
    )

    # Assert successful execution, print error if not
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"

    # Verify the expected file exists
    expected_file = Path("R219_v1_GRCh38.bed")
    assert expected_file.exists(), f"Expected output file {expected_file} was not created."

    # Verify the expected file exists
    expected_merged_file = Path("R219_v1_GRCh38_merged.bed")
    assert expected_file.exists(), f"Expected output file {expected_merged_file} was not created."

# Test case for exception handling when the get_response function fails
def test_generate_bed_exception_handling():
    """
    Test exception handling works as expected.
    """
    # Test parameters
    panel_id = "R207"
    panel_version = "4"
    genome_build = "GRCh38"

    # Mocking the functions used inside main() to simulate errors
    with mock.patch.object(
        panel_app_api_functions, "get_response",
        side_effect=Exception("PanelApp API error")
        ) as mock_get_response, \
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
            main(panel_id, panel_version, genome_build)

        # Check that the function that raised the error was called once
        mock_get_response.assert_called_once_with(panel_id)

        # Ensure other functions were not called after the exception
        mock_get_genes.assert_not_called()
        mock_generate_bed_file.assert_not_called()
        mock_bedtools_merge.assert_not_called()

    # Test for exception handling when get_genes fails
    with mock.patch.object(
        panel_app_api_functions, "get_response",
        return_value={"genes": []}
        ), \
         mock.patch.object(
             panel_app_api_functions, "get_genes",
             side_effect=Exception("Gene extraction error")) as mock_get_genes:

        with pytest.raises(Exception, match="Gene extraction error"):
            main(panel_id, panel_version, genome_build)

        # Ensure the get_genes function raised the error as expected
        mock_get_genes.assert_called_once()

    # Test for exception handling when generate_bed_file fails
    with mock.patch.object(
        panel_app_api_functions, "get_response",
        return_value={"genes": []}), \
         mock.patch.object(
             panel_app_api_functions, "get_genes",
             return_value=["BRCA1", "TP53"]
             ), \
         mock.patch.object(
             variant_validator_api_functions, "generate_bed_file",
             side_effect=Exception("BED file generation error")
             ) as mock_generate_bed_file:

        with pytest.raises(Exception, match="BED file generation error"):
            main(panel_id, panel_version, genome_build)

        # Check that the generate_bed_file function raised the error as expected
        mock_generate_bed_file.assert_called_once()

    # Test the exception when bedtools_merge fails
    with mock.patch.object(
        panel_app_api_functions, "get_response",
        return_value={"genes": []}), \
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
            main(panel_id, panel_version, genome_build)

        # Check that the bedtools_merge function raised the error as expected
        mock_bedtools_merge.assert_called_once()
