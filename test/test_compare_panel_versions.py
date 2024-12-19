"""
Unit tests for the compare_gene_lists.py script.

This test suite verifies the functionality of key functions in the panel version 
comparison script, ensuring correct behavior for panel validation, version 
ordering, gene list comparisons, and gene presence/absence detection.
"""
import argparse
import sys
import pytest

from PanelPal.compare_panel_versions import (
    validate_panel,
    determine_order,
    is_gene_absent,
    get_removed_genes,
    get_added_genes,
    argument_parser,
    main,
)

# The line below is a directive to pylint to ignore a specific formatting feature.
# This feature is not relevant for testing.
# pylint: disable=too-few-public-methods


#####################
#     Unit Tests    #
#####################
class TestArgParser:
    """
    Test class for the argument_parser function, which handles command-line arguments.
    """

    def test_valid_arguments(self, monkeypatch):
        """
        Test case to ensure that valid arguments parse correctly.
        Simulates the scenario where valid command-line arguments are provided.
        """
        # Mock the command line arguments
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "compare_gene_lists.py",
                "-p", "R1234",
                "-v", "1.0", "2.0",
                "-f", "green",
            ],
        )

        # Call the argument_parser function
        args = argument_parser()

        # Assert that the arguments parse correctly
        assert args.panel == "R1234", "Panel argument parsing failed"
        assert args.versions == [1.0, 2.0], "Versions argument parsing failed"
        assert args.status_filter == "green", "Status filter argument parsing failed"

    def test_default_filter(self, monkeypatch):
        """
        Test case to ensure that the default filter is set to 'green' when no filter is provided.
        Simulates the scenario where the status filter argument is not provided.
        """
        # Mock the command line arguments without the status filter
        monkeypatch.setattr(
            sys, "argv", ["compare_gene_lists.py", "-p", "R1234", "-v", "1.0", "2.0"]
        )

        # Call the argument_parser function
        args = argument_parser()

        # Assert that the default status filter value is 'green'
        assert args.status_filter == "green", "Default filter argument parsing failed"

    def test_invalid_filter(self, monkeypatch):
        """
        Test case to ensure that an invalid filter argument raises an error.
        Simulates the scenario where an invalid filter value ('blue') is provided.
        """
        # Mock the command line arguments with an invalid status filter
        monkeypatch.setattr(
            sys,
            "argv",
            ["compare_gene_lists.py", "-p", "R1234", "-v", "1.0", "2.0", "-f", "blue"],
        )

        # Call the function and expect it to raise an error due to invalid status filter
        with pytest.raises(SystemExit):  # argparse should exit with an error for invalid input
            argument_parser()

    def test_missing_panel_argument(self, monkeypatch):
        """
        Test case to ensure that the 'panel' argument is required and raises an error if missing.
        Simulates the scenario where the panel argument is not provided.
        """
        # Mock the command line arguments with a missing panel argument
        monkeypatch.setattr(
            sys, "argv", ["compare_gene_lists.py", "-v", "1.0", "2.0", "-f", "green"]
        )

        # Call the function and expect it to raise an error due to missing required argument
        with pytest.raises(SystemExit):  # argparse should exit with an error for missing panel
            argument_parser()

    def test_missing_versions_argument(self, monkeypatch):
        """
        Test case to ensure that the 'versions' argument is required and raises an error if missing.
        Simulates the scenario where the versions argument is not provided.
        """
        # Mock the command line arguments with a missing versions argument
        monkeypatch.setattr(
            sys, "argv", ["compare_gene_lists.py", "-p", "R1234", "-f", "green"]
        )

        # Call the function and expect it to raise an error due to missing versions
        with pytest.raises(SystemExit):  # argparse should exit with an error for missing versions
            argument_parser()


class TestValidatePanel:
    """Tests for the validate_panel function."""
    def test_valid_panel_names(self):
        """Verify that panel names in a valid format are accepted."""
        assert validate_panel("R123") == "R123"
        assert validate_panel("R1") == "R1"
        assert validate_panel("R9999") == "R9999"

    def test_invalid_panel_names(self):
        """Ensure invalid panel names raise an ArgumentTypeError."""
        with pytest.raises(argparse.ArgumentTypeError):
            validate_panel("123")  # No R prefix
        with pytest.raises(argparse.ArgumentTypeError):
            validate_panel("R")  # R with no numbers
        with pytest.raises(argparse.ArgumentTypeError):
            validate_panel("RX123")  # Non-digit after R
        with pytest.raises(argparse.ArgumentTypeError):
            validate_panel("r123")  # Lowercase r


class TestDetermineOrder:
    """Tests for the determine_order function."""
    def test_version_ordering(self):
        """Check that determine_order correctly identifies older and newer versions."""
        assert determine_order([1.0, 2.0]) == (1.0, 2.0)
        assert determine_order([2.0, 1.0]) == (1.0, 2.0)
        assert determine_order([1.1, 1.2]) == (1.1, 1.2)
        assert determine_order([2.3, 1.9]) == (1.9, 2.3)


class TestIsGeneAbsent:
    """Tests for the is_gene_absent function."""
    def test_gene_presence(self):
        """Verify gene presence and absence detection."""
        # Create a list of genes
        gene_list = ["BRCA1", "BRCA2", "TP53"]

        # Test when the gene is not present
        assert is_gene_absent("MYC", gene_list) is True
        assert is_gene_absent("CHEK2", gene_list) is True
        # Test when the gene is present
        assert is_gene_absent("BRCA1", gene_list) is False
        assert is_gene_absent("TP53", gene_list) is False


class TestRemovedGenes:
    """Tests for the get_removed_genes function."""
    def test_gene_removal(self):
        """Check identification of genes removed between panel versions."""
        # Test that a list of genes is returned when genes have been removed
        older_panel = ["BRCA1", "BRCA2", "MYC", "TP53"]
        newer_panel = ["BRCA1", "MYC", "CHEK2"]
        removed = get_removed_genes(older_panel, newer_panel)
        assert set(removed) == {"BRCA2", "TP53"}

        # Tests an empty list is returned when no genes have been removed
        older_panel = ["BRCA1", "MYC"]
        newer_panel = ["BRCA1", "MYC", "CHEK2"]
        removed = get_removed_genes(older_panel, newer_panel)
        # Checks it returns an empty list
        assert not removed


class TestAddedGenes:
    """Tests for the get_added_genes function."""
    def test_gene_addition(self):
        """Verify identification of genes added between panel versions."""
        # Test that a list of genes is returned when a gene has been added
        older_panel = ["BRCA1", "MYC", "CHEK2"]
        newer_panel = ["BRCA1", "BRCA2", "MYC", "TP53"]
        added = get_added_genes(older_panel, newer_panel)
        assert set(added) == {"BRCA2", "TP53"}

        # Test that an empty list is returned when no genes have been added
        older_panel = ["BRCA1", "MYC", "CHEK2"]
        newer_panel = ["BRCA1", "MYC", "CHEK2"]
        added = get_added_genes(older_panel, newer_panel)
        assert not added


####################
# Functional Tests #
####################

class TestMain:
    """Functional tests for the main script of the compare_panel_versions module."""

    def test_main_success(self, capsys):
        """Test the main function when valid arguments are passed."""
        # Specify CL arguments
        sys.argv = [
            "compare_panel_versions.py",
            "-p", "R21",
            "-v", "1.5", "1.9",
            "-f", "all"
        ]

        # Specify what output is expected
        expected_output = "Removed genes: []\nAdded genes: ['LMOD1', 'MYH11']"

        # Run main
        main()

        # Capture the standard output and standard error
        captured = capsys.readouterr()

        # Test the expected output is printed to screen
        assert expected_output in captured.out

    def test_main_panel_wrong(self):
        """Test the main function with an invalid panel argument."""
        # Specify CL arguments
        sys.argv = [
            "compare_panel_versions.py",
            "--panel", "R2132",
            "-v", "1.0", "1.1"
        ]

        # Capture and save the SystemExit Exception
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Test the exit code = 1
        assert str(exc_info.value) == "Panel R2132 not found. Exiting program."

    def test_main_old_version_wrong(self):
        """Test the main function with an invalid old version."""
        # Specify CL arguments
        sys.argv = [
            "compare_panel_versions.py",
            "--panel", "R39",
            "-v", "1.999", "2.0"
        ]

        # Capture and save the SystemExit Exception
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Test the exit code = 1
        assert exc_info.value.code == 1

    def test_main_new_version_wrong(self):
        """Test the main function with an invalid new version."""
        #Specify the CL arguments
        sys.argv = [
            "compare_panel_versions.py",
            "--panel", "R255",
            "-v", "1.1", "9999.0",
        ]

        # Capture and save the SystemExit Exception
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Test the exit code = 1
        assert exc_info.value.code == 1
