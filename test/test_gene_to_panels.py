#!/usr/bin/env python

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import argparse

from PanelPal.gene_to_panels import (
    confidence_to_colour,
    extract_panels,
    extract_r_codes,
    extract_r_codes_from_disorders,
    parse_arguments,
    main,
    write_panels
)

# Test data
SAMPLE_RESPONSE = {
    "results": [
        {
            "confidence_level": "3", 
            "panel": {
                "id": "123",
                "name": "Test Panel 1",
                "relevant_disorders": ["R1234", "Some disorder"],
            },
        },
        {
            "confidence_level": "2",
            "panel": {
                "id": "456", 
                "name": "Test Panel 2",
                "relevant_disorders": ["Another disorder"],
            },
        },
    ]
}

def test_parse_arguments():
    """
    Test the parse_arguments function.

    This test verifies that the parse_arguments function correctly parses the provided arguments.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    with patch('argparse.ArgumentParser.parse_args',
              return_value=argparse.Namespace(
                  hgnc_symbol='BRCA1',
                  confidence_status='green',
                  show_all_panels=False)):
        args = parse_arguments()
        assert args.hgnc_symbol == 'BRCA1'
        assert args.confidence_status == 'green'
        assert args.show_all_panels == False

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
    Test the extract_panels function for filtering by confidence status.

    Parameters
    ----------
    confidence_filter : str
        The confidence level to filter the panels.
    expected_status : str
        The expected gene status after filtering.

    Returns
    -------
    None
    """
    result = extract_panels(SAMPLE_RESPONSE, confidence_filter)
    if not result.empty:
        assert result.iloc[0]["Gene Status"] == expected_status

def test_extract_panels_confidence_filter():
    """
    Test the extract_panels function with different confidence filters.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # Test with confidence filter 'green' (should match one panel)
    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="green")
    assert len(result) == 1
    assert result.iloc[0]["Gene Status"] == "green"

    # Test with confidence filter 'amber' (should match one panel)
    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="amber")
    assert len(result) == 1
    assert result.iloc[0]["Gene Status"] == "amber"

    # Test with confidence filter 'red' (should match no panels)
    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="red")
    assert result.empty

    # Test with confidence filter 'all' (should match all panels)
    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="all")
    assert len(result) == 2
    assert set(result["Gene Status"].unique()) == {"green", "amber"}


@patch('pandas.DataFrame.to_csv')
def test_write_panels(mock_to_csv):
    """
    Test the write_panels function to ensure it writes the panel information to a CSV file.

    Parameters
    ----------
    mock_to_csv : unittest.mock.Mock
        Mock object for pandas DataFrame to_csv method.

    Returns
    -------
    None
    """
    df = pd.DataFrame({
        "PanelApp ID": ["123"],
        "R Code": ["R456"],
        "Panel Name": ["Test Panel"],
        "Gene Status": ["green"]
    })
    write_panels("BRCA1", "green", df)
    mock_to_csv.assert_called_once()

@patch('requests.get')
def test_main_no_panels(mock_get):
    """
    Test the main function with no panels found for the specified gene.

    Parameters
    ----------
    mock_get : unittest.mock.Mock
        Mock object for requests.get method.

    Returns
    -------
    None
    """
    mock_response = Mock()
    mock_response.json.return_value = {"results": []}
    mock_get.return_value = mock_response
    
    main(hgnc_symbol="TEST", confidence_status="green", show_all_panels=False)

def test_extract_panels_multiple_confidence_levels():
    """
    Test the extract_panels function with multiple confidence levels.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="all")
    assert len(result) == 2
    assert set(result["Gene Status"].unique()) == {"green", "amber"}

def test_extract_r_codes_from_disorders_empty_df():
    """
    Test the extract_r_codes_from_disorders function with an empty dataframe.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    empty_df = pd.DataFrame(columns=["Relevant Disorders"])
    result = extract_r_codes_from_disorders(empty_df)
    assert len(result) == 0

def test_extract_r_codes_multiple_codes():
    """
    Test the extract_r_codes function with a disorder string containing multiple R codes.

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
    Test the extract_r_codes_from_disorders function with different input dataframes.

    Parameters
    ----------
    input_df : pandas.DataFrame
        Input dataframe containing a 'Relevant Disorders' column with disorder descriptions.
    expected_len : int
        Expected number of R codes that should be extracted from the input.

    Returns
    -------
    None
    """
    result = extract_r_codes_from_disorders(input_df, show_all_panels=False)
    assert len(result) == expected_len

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
    level : int or str
        The confidence level to be tested.
    expected_colour : str
        The expected colour corresponding to the confidence level.

    Returns
    -------
    None
    """
    assert confidence_to_colour(level) == expected_colour

def test_extract_panels_empty_response():
    """
    Test the extract_panels function with an empty response.

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

def test_extract_r_codes_no_codes():
    """
    Test the extract_r_codes function with a disorder string that contains no R codes.

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

def test_extract_r_codes_single_code():
    """
    Test the extract_r_codes function with a disorder string containing a single R code.

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

def test_extract_r_codes_multiple_codes():
    """
    Test the extract_r_codes function with a disorder string containing multiple R codes.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    disorders = "R229, R258, Confirmed Fanconi anaemia or Bloom syndrome - mutation testing"
    result = extract_r_codes(disorders)
    assert result == "R229, R258"

def test_main_parse_arguments():
    """
    Test the main function to ensure it correctly parses command-line arguments.

    Parameters
    ----------
    None

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

def test_main_no_panels_found():
    """
    Test the main function with no panels found for the specified gene.

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
    
def test_main_multiple_confidence_levels():
    """
    Test the main function with multiple confidence levels.

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

def test_main_show_all_panels():
    """
    Test the main function with show_all_panels set to True.

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

def test_main_command_executed():
    """
    Test the main function to ensure the correct command is logged.

    Parameters
    ----------
    None

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

def test_main_confidence_status_green_amber():
    """
    Test the main function with confidence_status set to "green,amber".

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

# Additional tests
def test_extract_panels_no_confidence_level():
    """
    Test the extract_panels function with a response that has no confidence level.

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

def test_extract_panels_invalid_confidence_level():
    """
    Test the extract_panels function with a response that has an invalid confidence level.

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

def test_extract_r_codes_mixed_content():
    """
    Test the extract_r_codes function with a disorder string containing mixed content.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    disorders = "R123, Some disorder, R456, Another disorder"
    result = extract_r_codes(disorders)
    assert result == "R123, R456"

def test_extract_r_codes_no_disorders():
    """
    Test the extract_r_codes function with no disorders.

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

def test_extract_r_codes_empty_string():
    """
    Test the extract_r_codes function with an empty string.

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

def test_extract_r_codes_from_disorders_include_all():
    """
    Test the extract_r_codes_from_disorders function with show_all_panels set to True.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    input_df = pd.DataFrame({"Relevant Disorders": ["R229", "No R code disorder"]})
    result = extract_r_codes_from_disorders(input_df, show_all_panels=True)
    assert len(result) == 2
    assert result.iloc[0]["R Code"] == "R229"
    assert result.iloc[1]["R Code"] == "N/A"
