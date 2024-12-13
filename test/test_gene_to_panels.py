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
    with patch('argparse.ArgumentParser.parse_args',
              return_value=argparse.Namespace(
                  hgnc_symbol='BRCA1',
                  confidence_status='green',
                  show_all_panels=False)):
        args = parse_arguments()
        assert args.hgnc_symbol == 'BRCA1'
        assert args.confidence_status == 'green'
        assert args.show_all_panels == False

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
    result = extract_panels(SAMPLE_RESPONSE, confidence_filter)
    if not result.empty:
        assert result.iloc[0]["Gene Status"] == expected_status

# Test for extracting panels with specific confidence filter
def test_extract_panels_confidence_filter():
    confidence_filter = "green"
    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="green")
    assert len(result) == 1

    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="amber")
    assert len(result) == 1

    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="red")
    assert len(result) == 1

# Test for writing panels to CSV
@patch('pandas.DataFrame.to_csv')
def test_write_panels(mock_to_csv):
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
    mock_response = Mock()
    mock_response.json.return_value = {"results": []}
    mock_get.return_value = mock_response
    
    main(hgnc_symbol="TEST", confidence_status="green", show_all_panels=False)

# Test for extracting panels with multiple confidence levels
def test_extract_panels_multiple_confidence_levels():
    result = extract_panels(SAMPLE_RESPONSE, confidence_filter="all")
    assert len(result) == 3
    assert set(result["Gene Status"].unique()) == {"green", "amber", "red"}

# Test for extracting R codes from an empty dataframe
def test_extract_r_codes_from_disorders_empty_df():
    empty_df = pd.DataFrame(columns=["Relevant Disorders"])
    result = extract_r_codes_from_disorders(empty_df)
    assert len(result) == 0

# Test for extracting multiple R codes from disorders
def test_extract_r_codes_multiple_codes():
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
    assert confidence_to_colour(level) == expected_colour

# Test for extracting panels from an empty response
def test_extract_panels_empty_response():
    empty_response = {"results": []}
    result = extract_panels(empty_response, confidence_filter="green")
    assert result.empty

# Test for extracting R codes when no codes are present
def test_extract_r_codes_no_codes():
    disorders = "GI tract tumours"
    result = extract_r_codes(disorders)
    assert result == "N/A"

# Test for extracting a single R code from disorders
def test_extract_r_codes_single_code():
    disorders = "Familial ovarian cancer, R207"
    result = extract_r_codes(disorders)
    assert result == "R207"

# Test for extracting multiple R codes from disorders
def test_extract_r_codes_multiple_codes():
    disorders = "R229, R258, Confirmed Fanconi anaemia or Bloom syndrome - mutation testing"
    result = extract_r_codes(disorders)
    assert result == "R229, R258"

# Test for main function with parsed arguments
def test_main_parse_arguments():
    with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        hgnc_symbol='BRCA1',
        confidence_status='green',
        show_all_panels=True
    )):
        main(hgnc_symbol=None)

# Test for main function when no panels are found
def test_main_no_panels_found():
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        main(hgnc_symbol="TEST", confidence_status="green", show_all_panels=False)
    
# Test for main function with multiple confidence levels
def test_main_multiple_confidence_levels():
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_get.return_value = mock_response

        main(hgnc_symbol="TEST", confidence_status="all", show_all_panels=False)

# Test for main function with show_all_panels set to True
def test_main_show_all_panels():
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_get.return_value = mock_response

        main(hgnc_symbol="TEST", confidence_status="green", show_all_panels=True)

# Test for main function command execution
def test_main_command_executed():
    with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        hgnc_symbol='BRCA1',
        confidence_status='green',
        show_all_panels=True
    )):
        main(hgnc_symbol=None)

# Test for main function with green and amber confidence statuses
def test_main_confidence_status_green_amber():
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_get.return_value = mock_response

        main(hgnc_symbol="TEST", confidence_status="green,amber", show_all_panels=False)

# Test for extracting panels with no confidence level
def test_extract_panels_no_confidence_level():
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
    disorders = "R123, Some disorder, R456, Another disorder"
    result = extract_r_codes(disorders)
    assert result == "R123, R456"

# Test for extracting R codes when no disorders are present
def test_extract_r_codes_no_disorders():
    disorders = None
    result = extract_r_codes(disorders)
    assert result == "N/A"

# Test for extracting R codes from an empty string
def test_extract_r_codes_empty_string():
    disorders = ""
    result = extract_r_codes(disorders)
    assert result == "N/A"

# Test for extracting R codes from disorders including all panels
def test_extract_r_codes_from_disorders_include_all():
    input_df = pd.DataFrame({"Relevant Disorders": ["R229", "No R code disorder"]})
    result = extract_r_codes_from_disorders(input_df, show_all_panels=True)
    assert len(result) == 2
    assert result.iloc[0]["R Code"] == "R229"
    assert result.iloc[1]["R Code"] == "N/A"

# Test for processing panels
def test_process_panels():
    response_json = SAMPLE_RESPONSE
    confidence_statuses = ["green"]
    result = process_panels(response_json, confidence_statuses, show_all_panels=True)
    assert len(result) == 1

# Test for logging and printing command
@patch('PanelPal.gene_to_panels.get_logger')
def test_log_and_print_command(mock_get_logger):
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    log_and_print_command("BRCA1", "green", False)
    mock_logger.info.assert_called_once()

# Test for logging and printing when no panels are found
@patch('PanelPal.gene_to_panels.get_logger')
def test_log_and_print_no_panels(mock_get_logger):
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    log_and_print_no_panels("BRCA1", "green")
    mock_logger.info.assert_called_once()

# Test for displaying panels
def test_display_panels(capsys):
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
