"""
Tests for the db_input functions.
These tests cover correct inputs, edge cases, invalid inputs, and interactions with the database.
"""

from unittest.mock import patch, MagicMock
from PanelPal.db_input import (
    add_patient_to_db, patient_info_prompt,
    bed_file_info_prompt, add_bed_file_to_db,
    add_panel_data_to_db
)
from datetime import date, datetime
import pytest


def test_patient_info_prompt_correct():
    with patch("builtins.input", side_effect=["yes", "1234567890", "John Doe", "01-01-1990"]):
        patient_info = patient_info_prompt()
        assert patient_info["patient_id"] == "1234567890"
        assert patient_info["patient_name"] == "John Doe"
        assert patient_info["dob"] == datetime(1990, 1, 1).date()


def test_bed_file_info_prompt_correct():
    with patch("builtins.input", side_effect=["01-01-2022"]):
        bed_file_info = bed_file_info_prompt(
            "1234567890", "R207", "4", "GRCh38")
        assert bed_file_info["analysis_date"] == datetime(2022, 1, 1).date()
        assert bed_file_info["bed_file"] == "R207_v4_GRCh38.bed"
        assert bed_file_info["merged_bed_file"] == "R207_v4_GRCh38_merged.bed"


def test_patient_info_prompt_edge_case():
    with patch("builtins.input", side_effect=["yes", "1234567890", "A B C", "31-12-1999"]):
        patient_info = patient_info_prompt()
        assert patient_info["patient_id"] == "1234567890"
        assert patient_info["patient_name"] == "A B C"
        assert patient_info["dob"] == datetime(1999, 12, 31).date()


def test_patient_info_prompt_invalid_nhs_number(capsys):
    """
    Test error message appears/there is a prompt to retype NHS number 
    if it is not a 10 digit numeric
    """
    with patch("builtins.input", side_effect=["yes", "12345", "John Doe", "01-01-1990"]):
        try:
            patient_info = patient_info_prompt()
        except StopIteration:
            patient_info = None

        captured = capsys.readouterr()
        assert "Invalid NHS number. It must be a 10-digit numeric string." in captured.out
        assert patient_info is None


def test_patient_info_prompt_invalid_name(capsys):
    """
    Test invalid character (!) used for patient name
    """
    with patch("builtins.input", side_effect=["yes", "1234567890", "John!", "01-01-1990"]):
        try:
            patient_info = patient_info_prompt()
        except StopIteration:
            patient_info = None

        captured = capsys.readouterr()
        assert "Invalid name. It must contain only letters and spaces." in captured.out
        assert patient_info is None


def test_patient_info_prompt_invalid_dob(capsys):
    """
    Test invalid date of birth
    """
    with patch("builtins.input", side_effect=["yes", "1234567890", "John Doe", "01-01-99"]):
        try:
            patient_info = patient_info_prompt()
        except StopIteration:
            patient_info = None

        captured = capsys.readouterr()
        assert "Invalid date format. Please use DD-MM-YYYY." in captured.out
        assert patient_info is None


def test_bed_file_info_prompt_invalid_date(capsys):
    """
    Test invalid BED file analysis date
    """
    with patch("builtins.input", side_effect=["99-99-9999"]):
        try:
            bed_file_info = bed_file_info_prompt(
                "1234567890", "R207", "4", "GRCh38")
        except StopIteration:
            bed_file_info = None

        captured = capsys.readouterr()
        assert "Invalid date format. Please use DD-MM-YYYY." in captured.out
        assert bed_file_info is None


def test_patient_info_prompt_skip(capsys):
    """
    Test what happens when user types n (to skip data collection)
    """
    with patch("builtins.input", side_effect=["n"]):
        try:
            patient_info = patient_info_prompt()
        except StopIteration:
            patient_info = None

        captured = capsys.readouterr()
        assert patient_info is None


# Fixture for mock session
@pytest.fixture
def mock_session():
    """Create a mock session to simulate database interactions."""
    with patch("PanelPal.db_input.Session") as mock_session:
        yield mock_session


def test_add_patient_to_db(mock_session):
    """
    Test for adding patient to the database
    """
    mock_db = MagicMock()
    mock_session.return_value = mock_db

    patient_info = {
        "patient_id": "123456789",
        "patient_name": "John Doe",
        "dob": date(1990, 1, 1)
    }

    add_patient_to_db(patient_info)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_add_patient_to_db_error(mock_session):
    """
    Test for error while adding patient to the database
    """
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.add.side_effect = Exception("Database error")

    patient_info = {
        "patient_id": "123456789",
        "patient_name": "John Doe",
        "dob": date(1990, 1, 1)
    }

    try:
        add_patient_to_db(patient_info)
    except Exception:
        pass

    mock_db.rollback.assert_called_once()


def test_add_bed_file_to_db(mock_session):
    """
    Test for adding bed file info to the database
    """
    mock_db = MagicMock()
    mock_session.return_value = mock_db

    bed_file_info = {
        "analysis_date": datetime(2022, 1, 1).date(),
        "bed_file": "R207_v4_GRCh38.bed",
        "merged_bed_file": "R207_v4_GRCh38_merged.bed",
        "patient_id": "1234567890",
        "panel_name": "R207",
        "panel_version": "4",
        "genome_build": "GRCh38"
    }

    add_bed_file_to_db(bed_file_info)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_add_bed_file_to_db_error(mock_session):
    """
    Test for error when adding bed file info to the database
    """
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.add.side_effect = Exception("Database error")

    bed_file_info = {
        "analysis_date": datetime(2022, 1, 1).date(),
        "bed_file": "R207_v4_GRCh38.bed",
        "merged_bed_file": "R207_v4_GRCh38_merged.bed",
        "patient_id": "1234567890",
        "panel_name": "R207",
        "panel_version": "4",
        "genome_build": "GRCh38"
    }

    try:
        add_bed_file_to_db(bed_file_info)
    except Exception:
        pass

    mock_db.rollback.assert_called_once()


def test_add_panel_data_to_db(mock_session):
    """
    Test for adding panel data to the database
    """
    mock_db = MagicMock()
    mock_session.return_value = mock_db

    # Panel data info as a dictionary
    panel_data_info = {
        "panel_id": "R207",
        "bed_file_id": "R207_v4_GRCh38.bed"
    }

    # Unpack dictionary for individual arguments, if necessary
    add_panel_data_to_db(
        panel_data_info["panel_id"], panel_data_info["bed_file_id"])

    # Verify that add and commit were called
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_add_panel_data_to_db_error(mock_session):
    """
    Test for error while adding panel data to the database
    """
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.add.side_effect = Exception("Database error")

    panel_data_info = {
        "panel_id": "R207",
        "bed_file_id": "R207_v4_GRCh38.bed"
    }

    try:
        add_panel_data_to_db(
            panel_data_info["panel_id"], panel_data_info["bed_file_id"])
    except Exception:
        pass

    # Ensure rollback was called in case of error
    mock_db.rollback.assert_called_once()
