import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import logging
import os
import sys
import requests

# Import the functions from the script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'PanelPal')))
from check_panel import setup_logging, parse_arguments, is_valid_panel_id, format_panel_id, fetch_panel_info


# Tests for `format_panel_id`
def test_format_panel_id_valid():
    """Test if the panel ID is formatted correctly."""
    assert format_panel_id("207") == "R207"
    assert format_panel_id("r207") == "R207"
    assert format_panel_id("R207") == "R207"

def test_format_panel_id_invalid():
    """Test if invalid panel IDs raise ValueError."""
    with pytest.raises(ValueError):
        format_panel_id("XYZ")
    with pytest.raises(ValueError):
        format_panel_id("R27a")
    with pytest.raises(ValueError):
        format_panel_id("")

# Tests for 'get_name_version'
def test_fetch_panel_info():
    """Test R207 returns 'Inherited ovarian cancer (without breast cancer)' """
    formatted_id = "R207"
    result = fetch_panel_info(formatted_id)
    assert result["name"] == "Inherited ovarian cancer (without breast cancer)"

    """Test R59 returns 'Early onset or syndromic epilepsy' """
    formatted_id = "R207"
    result = fetch_panel_info(formatted_id)
    assert result["name"] == "Inherited ovarian cancer (without breast cancer)"

@patch("check_panel.get_response")
@patch("check_panel.get_name_version")

def test_fetch_panel_info_retry(mock_get_name_version, mock_get_response):
    """Test retry behavior when the API request fails."""
    
    # Arrange: Mock the request to fail for the first two attempts and succeed on the third.
    mock_get_response.side_effect = [requests.exceptions.RequestException, requests.exceptions.RequestException, 
                                     {"panel_id": "R59", "name": "Clinical Indication", "version": "1.0"}]
    mock_get_name_version.return_value = {"name": "Clinical Indication", "version": "1.0"}
    
    formatted_id = "R59"
    result = fetch_panel_info(formatted_id)

    # Assert: Ensure that the third attempt succeeds and the result is correct.
    assert result["name"] == "Clinical Indication"
    assert result["version"] == "1.0"
    mock_get_response.assert_called_with(formatted_id)
