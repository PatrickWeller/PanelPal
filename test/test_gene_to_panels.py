#!/usr/bin/env python

"""
Unit tests for the gene_to_panels.py script.

This test suite verifies the functionality of key functions in the gene to panels 
script, including extracting panels, extracting R codes, parsing arguments,
writing panels to CSV, and the main function.
"""

import argparse
from unittest.mock import Mock, patch
import pytest
import pandas as pd
from PanelPal.gene_to_panels import (
    confidence_to_colour,
    extract_panels,
    extract_r_codes,
    extract_r_codes_from_disorders,
    parse_arguments,
    main,
    write_panels,
    process_panels,
    log_and_print_command,
    log_and_print_no_panels,
    display_panels
)

# Sample response data for testing
SAMPLE_RESPONSE = {
    "results": [
        {
            "confidence_level": "3", 
            "panel": {
                "id": "55",
                "name": "Breast cancer pertinent cancer susceptibility",
                "relevant_disorders": ["Breast"],
            },
        },
        {
            "confidence_level": "2",
            "panel": {
                "id": "508", 
                "name": "Confirmed Fanconi anaemia or Bloom syndrome",
                "relevant_disorders": [
                    "R229",
                    "R258",
                    "Confirmed Fanconi anaemia or Bloom syndrome - mutation testing"
                ],
            },
        },
        {
            "confidence_level": "1",
            "panel": {
                "id": "398", 
                "name": "Primary immunodeficiency or monogenic inflammatory bowel disease",
                "relevant_disorders": [
                    "Primary immunodeficiency disorders",
                    "A- or hypo-gammaglobulinaemia",
                    "Congenital neutropaenia",
                    "Agranulocytosis",
                    "Combined B and T cell defect",
                    "Inherited complement deficiency",
                    "R15"
                ],
            },
        },
    ]
}

# Test for parsing command line arguments
def test_parse_arguments():
    """
    Test the parse_arguments function.

    This test uses the unittest.mock.patch to mock the argparse.ArgumentParser.parse_args method,
    providing predefined arguments for testing purposes.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Asserts
    -------
    - Asserts that the hgnc_symbol argument is 'BRCA1'.
    - Asserts that the confidence_status argument is 'green'.
    - Asserts that the show_all_panels argument is False.
    """
    with patch('argparse.ArgumentParser.parse_args',
              return_value=argparse.Namespace(
                  hgnc_symbol='BRCA1',
                  confidence_status='green',
                  show_all_panels=False)):
        args = parse_arguments()
        assert args.hgnc_symbol == 'BRCA1'
        assert args.confidence_status == 'green'
        assert args.show_all_panels is False

# Parametrized test for extracting panels based on confidence status
@pytest.mark.parametrize(
    "confidence_filter,expected_status",
    [
        ("green", "green"),
        ("amber", "amber"),
        ("red", "red")
    ]
)
def test_extract_panels_confidence_status(confidence_filter, expected_status):
    """
    Test the extract_panels function to ensure it correctly filters panels based
    on confidence status.

    Args:
        confidence_filter (str): The confidence level to filter the panels.
        expected_status (str): The expected gene status after filtering.

    Asserts:
        Asserts that the gene status of the first row in the result matches the 
        expected status.
    """
    result = extract_panels(SAMPLE_RESPONSE, confidence_filter)
    if not result.empty:
        assert result.iloc[0]["Gene Status"] == expected_status

# Test for extracting panels with specific confidence filter
def test_extract_panels_confidence_filter():
    """
    Test the extract_panels function with different confidence filters.

    This test checks the extract_panels function using three different confidence
    filters: "green", "amber", and "red". For each filter, it asserts that the
    length of the result is 1.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Asserts
    -------
    - Asserts that the length of the result is 1 for confidence_filter="green".
    - Asserts that the length of the result is 1 for confidence_filter="amber".
    - Asserts that the length of the result is 1 for confidence_filter="red".
    """

    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="green")
    assert len(result) == 1

    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="amber")
    assert len(result) == 1

    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="red")
    assert len(result) == 1

# Test for writing panels to CSV
@patch('pandas.DataFrame.to_csv')
def test_write_panels(mock_to_csv):
    """
    Test the write_panels function.

    This test verifies that the write_panels function correctly writes the 
    DataFrame to a CSV file and that the to_csv method is called once.

    Args:
        mock_to_csv (Mock): A mock object for the pandas to_csv method.

    Raises:
        AssertionError: If the to_csv method is not called exactly once.
    """
    df = pd.DataFrame({
        "PanelApp ID": ["123"],
        "R Code": ["R456"],
        "Panel Name": ["Test Panel"],
        "Gene Status": ["green"]
    })
    write_panels("BRCA1", "green", df)
    mock_to_csv.assert_called_once()

# Test for main function when no panels are found
@patch('requests.get')
def test_main_no_panels(mock_get):
    """
    Test the main function when no panels are returned.
    This test mocks the response of an API call to return an empty list of results,
    simulating a scenario where no panels are found for the given HGNC symbol and 
    confidence status.
    Args:
        mock_get (Mock): A mock object to replace the 'requests.get' method.
    Returns:
        None
    """
    mock_response = Mock()
    mock_response.json.return_value = {"results": []}
    mock_get.return_value = mock_response

    main(hgnc_symbol="TEST", confidence_status="green", show_all_panels=False)

# Test for extracting panels with multiple confidence levels
def test_extract_panels_multiple_confidence_levels():
    """
    Test the extract_panels function with multiple confidence levels.

    This test checks if the extract_panels function correctly filters and 
    returns panels with all confidence levels ("green", "amber", "red") when 
    the confidence_filter is set to "all".

    Assertions:
        - The length of the result should be 3.
        - The unique values in the "Gene Status" column of the result should be 
          {"green", "amber", "red"}.
    """
    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="all")
    assert len(result) == 3
    assert set(result["Gene Status"].unique()) == {"green", "amber", "red"}

# Test for extracting R codes from an empty dataframe
def test_extract_r_codes_from_disorders_empty_df():
    """
    Test the extract_r_codes_from_disorders function with an empty DataFrame.

    This test checks that the function returns an empty list when provided with
    an empty DataFrame that has a column named "Relevant Disorders".

    Assertions:
        - The result should be an empty list.
    """
    empty_df = pd.DataFrame(columns=["Relevant Disorders"])
    result = extract_r_codes_from_disorders(empty_df)
    assert len(result) == 0

# Test for extracting multiple R codes from disorders
def test_extract_r_codes_multiple_codes():
    """
    Test the extract_r_codes function with multiple R-codes.

    This test checks if the extract_r_codes function correctly extracts
    multiple R-codes from a string containing both R-codes and other text.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    disorders = "R123, R456, R789, Some disease"
    result = extract_r_codes(disorders)
    assert result == "R123, R456, R789"

# Parametrized test for extracting R codes from disorders with filtering
@pytest.mark.parametrize(
    "input_df,expected_len",
    [
        (pd.DataFrame({"Relevant Disorders": ["Familial ovarian cancer, R207"]}), 1),
        (pd.DataFrame({"Relevant Disorders": ["GI tract tumours"]}), 0),
        (pd.DataFrame({"Relevant Disorders": ["R229", "R258"]}), 2)
    ]
)
def test_extract_r_codes_from_disorders_filtering(input_df, expected_len):
    """
    Test the extraction of R codes from disorders with filtering.

    Parameters
    ----------
    input_df : pandas.DataFrame
        The input dataframe containing disorder information.
    expected_len : int
        The expected length of the resulting list of R codes.

    Raises
    ------
    AssertionError
        If the length of the result does not match the expected length.
    """
    result = extract_r_codes_from_disorders(input_df, show_all_panels=False)
    assert len(result) == expected_len

# Parametrized test for converting confidence level to colour
@pytest.mark.parametrize(
    "level,expected_colour",
    [
        (1, "red"),
        (2, "amber"),
        (3, "green"),
        ("1", "red"),
        ("2", "amber"),
        ("3", "green"),
        ("unknown", "unknown"),
        (None, "unknown")
    ]
)
def test_confidence_to_colour(level, expected_colour):
    """
    Test the confidence_to_colour function.

    Parameters
    ----------
    level : int or float
        The confidence level to be converted to a colour.
    expected_colour : str
        The expected colour corresponding to the given confidence level.

    Raises
    ------
    AssertionError
        If the colour returned by confidence_to_colour(level) does not match expected_colour.
    """
    assert confidence_to_colour(level) == expected_colour

# Test for extracting panels from an empty response
def test_extract_panels_empty_response():
    """
    Test the `extract_panels` function with an empty response.

    This test verifies that the `extract_panels` function returns an empty
    result when provided with an empty response dictionary.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    empty_response = {"results": []}
    result = extract_panels(empty_response, confidence_filter="green")
    assert result.empty

# Test for extracting R codes when no codes are present
def test_extract_r_codes_no_codes():
    """
    Test case for the function `extract_r_codes` when no R-codes are present.

    This test checks if the function `extract_r_codes` correctly returns "N/A" 
    when the input disorder does not have any associated R-codes.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    disorders = "GI tract tumours"
    result = extract_r_codes(disorders)
    assert result == "N/A"

# Test for extracting a single R code from disorders
def test_extract_r_codes_single_code():
    """
    Test the extract_r_codes function with a single code.

    This test case checks if the function correctly extracts a single R code
    from a string containing a disorder description and an R code.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    disorders = "Familial ovarian cancer, R207"
    result = extract_r_codes(disorders)
    assert result == "R207"


# Test for main function with parsed arguments
def test_main_parse_arguments():
    """
    Test the main function's argument parsing.

    This test mocks the `argparse.ArgumentParser.parse_args` method to return
    a predefined set of arguments and then calls the `main` function with
    `hgnc_symbol` set to `None`.

    Mocked Arguments
    ----------------
    hgnc_symbol : str
        The HGNC symbol for the gene (e.g., 'BRCA1').
    confidence_status : str
        The confidence status of the gene (e.g., 'green').
    show_all_panels : bool
        Flag to indicate whether to show all panels.

    Returns
    -------
    None
    """
    with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        hgnc_symbol='BRCA1',
        confidence_status='green',
        show_all_panels=True
    )):
        main(hgnc_symbol=None)

# Test for main function when no panels are found
def test_main_no_panels_found():
    """
    Test case for the `main` function when no panels are found.

    This test mocks the `requests.get` method to return an empty list of results,
    simulating a scenario where no panels are found for the given HGNC symbol and
    confidence status.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        main(hgnc_symbol="TEST", confidence_status="green", show_all_panels=False)

# Test for main function with multiple confidence levels
def test_main_multiple_confidence_levels():
    """
    Test the main function with multiple confidence levels.

    This test mocks the 'requests.get' method to return a predefined sample response.
    It then calls the 'main' function with specific parameters to verify its behavior
    when handling multiple confidence levels.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_get.return_value = mock_response

        main(hgnc_symbol="TEST", confidence_status="all", show_all_panels=False)

# Test for main function with show_all_panels set to True
def test_main_show_all_panels():
    """
    Test the main function with the 'show_all_panels' parameter set to True.

    This test mocks the 'requests.get' method to return a predefined sample response.
    It then calls the 'main' function with specific parameters to verify its behavior
    when the 'show_all_panels' flag is enabled.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_get.return_value = mock_response

        main(hgnc_symbol="TEST", confidence_status="green", show_all_panels=True)

# Test for main function command execution
def test_main_command_executed():
    """
    Test the main command execution with specific arguments.

    This test patches the `argparse.ArgumentParser.parse_args` method to return
    a predefined set of arguments and then calls the `main` function with
    `hgnc_symbol` set to `None`.

    The predefined arguments are:
    - hgnc_symbol: 'BRCA1'
    - confidence_status: 'green'
    - show_all_panels: True

    The purpose of this test is to verify that the `main` function is executed
    correctly with the given arguments.

    """
    with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        hgnc_symbol='BRCA1',
        confidence_status='green',
        show_all_panels=True
    )):
        main(hgnc_symbol=None)

# Test for main function with green and amber confidence statuses
def test_main_confidence_status_green_amber():
    """
    Test the main function with confidence status set to 'green,amber'.

    This test mocks the 'requests.get' method to return a predefined sample response.
    It then calls the main function with the specified parameters and checks if the
    function behaves as expected.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_get.return_value = mock_response

        main(hgnc_symbol="TEST", confidence_status="green,amber", show_all_panels=False)

# Test for extracting panels with no confidence level
def test_extract_panels_no_confidence_level():
    """
    Test case for the `extract_panels` function when no panels meet the confidence level filter.

    This test checks the behavior of the `extract_panels` function when the provided response
    contains panels, but none of them meet the specified confidence level filter 
    ("green" in this case).

    The expected result is that the function returns an empty DataFrame.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    response = {
        "results": [
            {
                "panel": {
                    "id": "789",
                    "name": "Test Panel 3",
                    "relevant_disorders": ["R7890", "Another disorder"],
                },
            }
        ]
    }
    result = extract_panels(response, confidence_filter="green")
    assert result.empty

# Test for extracting panels with invalid confidence level
def test_extract_panels_invalid_confidence_level():
    """
    Test the `extract_panels` function with an invalid confidence level.

    This test checks the behavior of the `extract_panels` function when the 
    confidence level in the response does not match the specified confidence 
    filter. The response contains a panel with a confidence level of "5", 
    while the confidence filter is set to "green". The expected result is 
    that the function returns an empty DataFrame.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    response = {
        "results": [
            {
                "confidence_level": "5",
                "panel": {
                    "id": "101",
                    "name": "Test Panel 4",
                    "relevant_disorders": ["R1010", "Invalid disorder"],
                },
            }
        ]
    }
    result = extract_panels(response, confidence_filter="green")
    assert result.empty

# Test for extracting R codes from mixed content
def test_extract_r_codes_mixed_content():
    """
    Test the extract_r_codes function with a string containing mixed content.

    The input string contains both disorder codes (starting with 'R') and disorder names.
    This test checks if the function correctly extracts only the disorder codes.

    Returns
    -------
    None
    """
    disorders = "R123, Some disorder, R456, Another disorder"
    result = extract_r_codes(disorders)
    assert result == "R123, R456"

# Test for extracting R codes when no disorders are present
def test_extract_r_codes_no_disorders():
    """
    Test the extract_r_codes function when no disorders are provided.

    This test checks the behavior of the extract_r_codes function when the input
    disorders is None. The expected result is "N/A".

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    disorders = None
    result = extract_r_codes(disorders)
    assert result == "N/A"

# Test for extracting R codes from an empty string
def test_extract_r_codes_empty_string():
    """
    Test the extract_r_codes function with an empty string.

    This test checks if the function correctly handles an empty string input
    and returns "N/A" as expected.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    disorders = ""
    result = extract_r_codes(disorders)
    assert result == "N/A"

# Test for extracting R codes from disorders including all panels
def test_extract_r_codes_from_disorders_include_all():
    """
    Test the `extract_r_codes_from_disorders` function with the `show_all_panels` 
    parameter set to True.

    This test checks the following:
    - The function correctly extracts R codes from the "Relevant Disorders" column of 
      the input DataFrame.
    - When the disorder does not have an R code, it should return "N/A".
    - The length of the resulting DataFrame should be 2.

    Test cases:
    - Input DataFrame with "Relevant Disorders" containing "R229" and "No R code disorder".
    - Expected output DataFrame should have "R229" and "N/A" in the "R Code" column.

    Raises
    ------
    AssertionError
        If the length of the result is not 2 or the R codes do not match the expected values.
    """
    input_df = pd.DataFrame({"Relevant Disorders": ["R229", "No R code disorder"]})
    result = extract_r_codes_from_disorders(input_df, show_all_panels=True)
    assert len(result) == 2
    assert result.iloc[0]["R Code"] == "R229"
    assert result.iloc[1]["R Code"] == "N/A"

# Test for processing panels
def test_process_panels():
    """
    Test the process_panels function.

    This test verifies that the process_panels function correctly processes the
    given response JSON and filters panels based on the specified confidence statuses.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Asserts
    -------
    - The length of the result is 1, indicating that only one panel meets the criteria.
    """
    response_json = SAMPLE_RESPONSE
    confidence_statuses = ["green"]
    result = process_panels(response_json, confidence_statuses, show_all_panels=True)
    assert len(result) == 1

# Test for logging and printing command
@patch('PanelPal.gene_to_panels.get_logger')
def test_log_and_print_command(mock_get_logger):
    """
    Test the log_and_print_command function.

    Parameters
    ----------
    mock_get_logger : unittest.mock.Mock
        A mock object for the get_logger function.

    Notes
    -----
    This test verifies that the log_and_print_command function logs the correct information.
    It uses a mock logger to capture the log output and asserts that the logger's info method
    is called exactly once.
    """
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    log_and_print_command("BRCA1", "green", False)
    mock_logger.info.assert_called_once()

# Test for logging and printing when no panels are found
@patch('PanelPal.gene_to_panels.get_logger')
def test_log_and_print_no_panels(mock_get_logger):
    """
    Test the log_and_print_no_panels function to ensure it logs the correct message 
    when no panels are found.

    Parameters
    ----------
    mock_get_logger : unittest.mock.Mock
        A mock object for the logger getter function.

    Notes
    -----
    This test checks that the logger's info method is called exactly once when the 
    log_and_print_no_panels function is executed.
    """
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    log_and_print_no_panels("BRCA1", "green")
    mock_logger.info.assert_called_once()

# Test for displaying panels
def test_display_panels(capsys):
    """
    Test the display_panels function.

    This test verifies that the display_panels function correctly prints the
    panel information to the console. It captures the standard output and
    checks if the expected strings are present.

    Parameters
    ----------
    capsys : pytest.CaptureFixture
        A pytest fixture to capture the standard output.

    Returns
    -------
    None

    Asserts
    -------
    - Asserts that the output contains the string "Panels associated with gene BRCA1".
    - Asserts that the output contains the string "Test Panel".
    """
    df = pd.DataFrame({
        "PanelApp ID": ["123"],
        "R Code": ["R456"],
        "Panel Name": ["Test Panel"],
        "Gene Status": ["green"]
    })
    display_panels("BRCA1", df)
    captured = capsys.readouterr()
    assert "Panels associated with gene BRCA1" in captured.out
    assert "Test Panel" in captured.out
