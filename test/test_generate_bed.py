import pytest
import subprocess
import sys
import logging
from unittest import mock
from ..PanelPal.generate_bed import main
from accessories import variant_validator_api_functions, panel_app_api_functions




def test_missing_required_arguments():
    """Test script behavior when required arguments are missing."""
    result = subprocess.run(
        [sys.executable, "PanelPal/generate_bed.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "the following arguments are required" in result.stderr


def test_missing_arguments():
    """Test script behavior when invalid arguments are passed."""
    result = subprocess.run(
        [sys.executable, "PanelPal/generate_bed.py", "-p", "R207", "-v", "4"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "the following arguments are required: -g/--genome_build" in result.stderr


def test_valid_arguments():
    """Test script behavior with valid arguments."""
    # Run the script as a subprocess
    result = subprocess.run(
        [
            sys.executable,
            "PanelPal/generate_bed.py",
            "-p",
            "R207",
            "-v",
            "4",
            "-g",
            "GRCh38",
        ],
        capture_output=True,
        text=True,
    )
    
    # Assert successful execution
    assert result.returncode == 0
    
    # Check for the success message in either stdout or stderr
    output = result.stdout + result.stderr
    assert "Process completed successfully" in output


# Mocking the logger to capture the log output for verification
@pytest.fixture
def mock_logger():
    with mock.patch("PanelPal.PanelPal.generate_bed.logger") as mock_logger:
        yield mock_logger  # Yield the mocked logger to the test

# Test case for exception handling in the 'main' function
def test_generate_bed_exception_handling():
    # Test parameters
    panel_id = "R207"
    panel_version = "4"
    genome_build = "GRCh38"
    
    # Mocking the functions used inside main() to simulate errors
    with mock.patch.object(panel_app_api_functions, "get_response", side_effect=Exception("PanelApp API error")) as mock_get_response, \
         mock.patch.object(panel_app_api_functions, "get_genes") as mock_get_genes, \
         mock.patch.object(variant_validator_api_functions, "generate_bed_file") as mock_generate_bed_file, \
         mock.patch.object(variant_validator_api_functions, "bedtools_merge") as mock_bedtools_merge:
        
        # Call the 'main' function and assert that it raises the expected exception
        with pytest.raises(Exception, match="PanelApp API error"):
            main(panel_id, panel_version, genome_build)

        # Check that the function that raised the error was called
        mock_get_response.assert_called_once_with(panel_id)
        
        # Ensure other functions were not called, since the exception occurred early
        mock_get_genes.assert_not_called()
        mock_generate_bed_file.assert_not_called()
        mock_bedtools_merge.assert_not_called()

    # Test the case where another error occurs during a different part of the process
    with mock.patch.object(panel_app_api_functions, "get_response", return_value={"genes": []}), \
         mock.patch.object(panel_app_api_functions, "get_genes", side_effect=Exception("Gene extraction error")) as mock_get_genes:
        
        with pytest.raises(Exception, match="Gene extraction error"):
            main(panel_id, panel_version, genome_build)
        
        # Ensure the get_genes function raised the error as expected
        mock_get_genes.assert_called_once()

    # Test another part of the process: generation of BED file
    with mock.patch.object(panel_app_api_functions, "get_response", return_value={"genes": []}), \
         mock.patch.object(panel_app_api_functions, "get_genes", return_value=["BRCA1", "TP53"]), \
         mock.patch.object(variant_validator_api_functions, "generate_bed_file", side_effect=Exception("BED file generation error")) as mock_generate_bed_file:
        
        with pytest.raises(Exception, match="BED file generation error"):
            main(panel_id, panel_version, genome_build)
        
        # Check that the generate_bed_file function raised the error as expected
        mock_generate_bed_file.assert_called_once()

    # Test the bedtools merge error
    with mock.patch.object(panel_app_api_functions, "get_response", return_value={"genes": []}), \
         mock.patch.object(panel_app_api_functions, "get_genes", return_value=["BRCA1", "TP53"]), \
         mock.patch.object(variant_validator_api_functions, "generate_bed_file"), \
         mock.patch.object(variant_validator_api_functions, "bedtools_merge", side_effect=Exception("Bedtools merge error")) as mock_bedtools_merge:
        
        with pytest.raises(Exception, match="Bedtools merge error"):
            main(panel_id, panel_version, genome_build)
        
        # Check that the bedtools_merge function raised the error as expected
        mock_bedtools_merge.assert_called_once()