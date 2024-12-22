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


from unittest import mock
from unittest.mock import patch
from io import StringIO
import pytest
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
    # Mock sys.argv to simulate the script being called without required arguments
    with patch('sys.argv', new=["generate_bed.py"]):
        with pytest.raises(SystemExit) as exc_info:
            # Attempt to parse arguments without providing required ones
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                parse_arguments()

        # Check that the script exits with the expected error code
        assert exc_info.value.code != 0

        # Check that the error message mentions missing arguments
        assert "the following arguments are required" in mock_stderr.getvalue()


def test_missing_single_argument():
    """Test missing a single required argument"""
    # Mock sys.argv to simulate the script being called with missing arguments
    with patch('sys.argv', new=["generate_bed.py", "-p", "R207", "-v", "4"]):
        with pytest.raises(SystemExit) as exc_info:
            # Attempt to parse arguments with missing genome build argument
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                parse_arguments()

        # Check that the script exits with the expected error code
        assert exc_info.value.code != 0

        # Check that the error message mentions missing -g/--genome_build argument
        assert "the following arguments are required: -g/--genome_build" in mock_stderr.getvalue()


def test_invalid_genome_build():
    """Test with an invalid genome build"""
    # Mock sys.argv to simulate the script being called with an invalid genome build
    with patch('sys.argv', new=[
            "generate_bed.py", "-p", "R207", "-v", "4", "-g", "INVALID_GENOME"]):
        with pytest.raises(SystemExit) as exc_info:
            # Attempt to parse arguments with an invalid genome build
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                parse_arguments()

        # Check that the script exits with the expected error code
        assert exc_info.value.code != 0

        # Check that the error message mentions the invalid genome build
        assert (
            "invalid choice: 'INVALID_GENOME' "
            "(choose from 'GRCh37', 'GRCh38')"
            in mock_stderr.getvalue()
        )


def test_empty_panel_id():
    """Test with an empty panel_id"""
    # Mock sys.argv to simulate running the script with an empty panel_id
    with patch("sys.argv", new=["generate_bed.py", "-p", "", "-v", "4", "-g", "GRCh38"]):
        # Mock the input to avoid the prompt
        with patch("builtins.input", return_value="n"):  # Simulate 'n' for patient info
            with patch("PanelPal.generate_bed.logger") as mock_logger:
                # Call the main function directly within a try-except block
                try:
                    main()
                except Exception:
                    # Check that the error message was logged
                    mock_logger.error.assert_called_with(
                        "An error occurred in the BED file generation process for panel_id=%s: %s",
                        "",
                        mock_logger._mock_return_value
                    )


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
