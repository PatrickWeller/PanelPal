#!/usr/bin/env python

"""
Unit tests for the check_panel module.

This script uses pytest and unittest.mock to test the functions in the check_panel module. 
The module provides utilities for validating, formatting, and retrieving information about 
panel IDs, as well as setting up logging for tracking execution details.

The tests cover:
- Validation of panel ID formats, including standard cases and edge cases.
- Formatting of panel IDs to ensure they conform to the required format.
- Fetching panel information via mocked API calls, including handling errors, slow responses, 
  and retry logic.
- Setting up logging, including cases with invalid paths.

Each test function includes additional edge cases and proper docstrings to explain their purpose.

Dependencies:
- pytest
- unittest.mock
- check_panel module
"""

from unittest.mock import patch
import pytest
import requests
from check_panel import (
    format_panel_id,
    is_valid_panel_id,
    fetch_panel_info,
    setup_logging,
)


# --- Tests for is_valid_panel_id ---
def test_is_valid_panel_id():
    """Test the validation of correctly and incorrectly formatted panel IDs."""
    assert is_valid_panel_id("R59") is True
    assert is_valid_panel_id("R207") is True
    assert is_valid_panel_id("r59") is False  # Needs to be uppercase
    assert is_valid_panel_id("59") is False  # Requires 'R' prefix
    assert is_valid_panel_id("XYZ") is False  # Invalid format
    assert is_valid_panel_id("") is False  # Empty string


def test_is_valid_panel_id_edge_cases():
    """Test edge cases for panel ID validation."""
    assert is_valid_panel_id(" R59") is False  # Leading space
    assert is_valid_panel_id("R59 ") is False  # Trailing space
    assert is_valid_panel_id("") is False  # Empty string
    assert is_valid_panel_id("R59!") is False  # Special characters
    assert is_valid_panel_id("R") is False  # Missing numeric component


# --- Tests for format_panel_id ---
def test_format_panel_id():
    """Test the formatting of panel IDs to ensure they are correctly prefixed."""
    assert format_panel_id("R59") == "R59"
    assert format_panel_id("59") == "R59"  # Adds 'R' prefix


def test_format_panel_id_edge_cases():
    """Test edge cases for formatting panel IDs."""
    assert format_panel_id(" R59 ") == "R59"  # Trims spaces
    assert format_panel_id("r59") == "R59"  # Converts to uppercase
    assert format_panel_id("9999999999999") == "R9999999999999"  # Handles large IDs
    with pytest.raises(ValueError):
        format_panel_id("59!")  # Invalid characters
    with pytest.raises(ValueError):
        format_panel_id("")  # Empty string


# --- Tests for fetch_panel_info ---
@patch("check_panel.get_response")
@patch("check_panel.get_name_version")
def test_fetch_panel_info(mock_get_name_version, _):
    """Test fetching panel information from a valid panel ID."""
    mock_get_name_version.return_value = {"name": "PanelName", "version": "1.0"}
    result = fetch_panel_info("R59")
    assert result == {"name": "PanelName", "version": "1.0"}


@patch("check_panel.get_response")
@patch("check_panel.get_name_version")
def test_fetch_panel_info_edge_cases(mock_get_name_version, mock_get_response):
    """Test edge cases for fetching panel information."""
    mock_get_response.return_value = None  # Nonexistent panel
    result = fetch_panel_info("R999999")
    assert result == {}  # Should handle missing panels gracefully

    mock_get_name_version.return_value = {}  # Incomplete response
    result = fetch_panel_info("R59")
    assert result == {}

    mock_get_response.side_effect = requests.exceptions.ConnectionError
    result = fetch_panel_info("R59")
    assert result == {}  # Handles connection error


@patch("check_panel.get_response")
@patch("check_panel.get_name_version")
def test_fetch_panel_info_slow_response(_, mock_get_response):
    """Test handling of slow API responses with retries."""
    mock_get_response.side_effect = [requests.exceptions.Timeout]
    result = fetch_panel_info("R59", retries=1, delay=1)
    assert result == {}  # Should return empty dictionary


@patch("check_panel.get_response")
@patch("check_panel.get_name_version")
def test_fetch_panel_info_max_retries(_, mock_get_response):
    """Test maximum retry logic for API request failures."""
    mock_get_response.side_effect = requests.exceptions.RequestException
    result = fetch_panel_info("R59", retries=5, delay=0.1)
    assert result == {}
    assert mock_get_response.call_count == 5  # Retries exactly 5 times


# --- Tests for setup_logging ---
def test_setup_logging():
    """Test that logging setup correctly creates a log file."""
    setup_logging(log_file="test.log")  # Ensure log file is created


def test_setup_logging_invalid_path():
    """Test that invalid log file paths are handled gracefully."""
    with pytest.raises(FileNotFoundError):
        setup_logging(log_file="/nonexistent/path/test.log")  # Invalid directory
