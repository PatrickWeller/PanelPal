"""
Unit tests for the compare_gene_lists.py script.

This test suite verifies the functionality of key functions in the panel version 
comparison script, ensuring correct behavior for panel validation, version 
ordering, gene list comparisons, and gene presence/absence detection.
"""

import pytest
import argparse
import sys
from compare_panel_versions import (
    validate_panel, 
    determine_order, 
    is_gene_absent, 
    get_removed_genes, 
    get_added_genes,
    argument_parser
)

class TestArgParser:
    """
    Test class for the argument_parser function which handles command-line arguments.
    """

    def test_valid_arguments(self, monkeypatch):
        """
        Test case to ensure that valid arguments are correctly parsed.
        Simulates the scenario where valid command-line arguments are provided.
        """
        # Mocking the command line arguments
        monkeypatch.setattr(sys, 'argv', ['compare_gene_lists.py', '-p', 'R1234', '-v', '1.0', '2.0', '-f', 'green'])
        
        # Calling the argument_parser function
        args = argument_parser()
        
        # Asserting that the arguments were parsed correctly
        assert args.panel == 'R1234', "Panel argument parsing failed"
        assert args.versions == [1.0, 2.0], "Versions argument parsing failed"
        assert args.filter == 'green', "Filter argument parsing failed"

    def test_default_filter(self, monkeypatch):
        """
        Test case to ensure that the default filter is set to 'green' when no filter is provided.
        Simulates the scenario where the filter argument is not provided.
        """
        # Mocking the command line arguments without the filter
        monkeypatch.setattr(sys, 'argv', ['compare_gene_lists.py', '-p', 'R1234', '-v', '1.0', '2.0'])
        
        # Calling the argument_parser function
        args = argument_parser()
        
        # Asserting the default filter value is 'green'
        assert args.filter == 'green', "Default filter argument parsing failed"

    def test_invalid_filter(self, monkeypatch):
        """
        Test case to ensure that an invalid filter argument raises an error.
        Simulates the scenario where an invalid filter value ('blue') is provided.
        """
        # Mocking the command line arguments with an invalid filter
        monkeypatch.setattr(sys, 'argv', ['compare_gene_lists.py', '-p', 'R1234', '-v', '1.0', '2.0', '-f', 'blue'])
        
        # Calling the function and expecting it to raise an error due to invalid filter
        with pytest.raises(SystemExit):  # argparse should exit with an error for invalid input
            argument_parser()

    def test_missing_panel_argument(self, monkeypatch):
        """
        Test case to ensure that the 'panel' argument is required and raises an error if missing.
        Simulates the scenario where the panel argument is not provided.
        """
        # Mocking the command line arguments with a missing panel argument
        monkeypatch.setattr(sys, 'argv', ['compare_gene_lists.py', '-v', '1.0', '2.0', '-f', 'green'])
        
        # Calling the function and expecting it to raise an error due to missing required argument
        with pytest.raises(SystemExit):  # argparse should exit with an error for missing panel
            argument_parser()

    def test_missing_versions_argument(self, monkeypatch):
        """
        Test case to ensure that the 'versions' argument is required and raises an error if missing.
        Simulates the scenario where the versions argument is not provided.
        """
        # Mocking the command line arguments with a missing versions argument
        monkeypatch.setattr(sys, 'argv', ['compare_gene_lists.py', '-p', 'R1234', '-f', 'green'])
        
        # Calling the function and expecting it to raise an error due to missing versions
        with pytest.raises(SystemExit):  # argparse should exit with an error for missing versions
            argument_parser()

class TestValidatePanel:
    """Tests for the validate_panel function."""

    def test_valid_panel_names(self):
        """Verify that valid panel names are accepted."""
        assert validate_panel('R123') == 'R123'
        assert validate_panel('R1') == 'R1'
        assert validate_panel('R9999') == 'R9999'

    def test_invalid_panel_names(self):
        """Ensure invalid panel names raise an ArgumentTypeError."""
        with pytest.raises(argparse.ArgumentTypeError):
            validate_panel('123')  # No R prefix
        with pytest.raises(argparse.ArgumentTypeError):
            validate_panel('R')  # R with no numbers
        with pytest.raises(argparse.ArgumentTypeError):
            validate_panel('RX123')  # Non-digit after R
        with pytest.raises(argparse.ArgumentTypeError):
            validate_panel('r123')  # Lowercase r


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
        gene_list = ["BRCA1", "BRCA2", "TP53"]
        
        assert is_gene_absent("MYC", gene_list) == True
        assert is_gene_absent("CHEK2", gene_list) == True
        assert is_gene_absent("BRCA1", gene_list) == False
        assert is_gene_absent("TP53", gene_list) == False


class TestRemovedGenes:
    """Tests for the get_removed_genes function."""

    def test_gene_removal(self):
        """Check identification of genes removed between panel versions."""
        older_panel = ["BRCA1", "BRCA2", "MYC", "TP53"]
        newer_panel = ["BRCA1", "MYC", "CHEK2"]
        removed = get_removed_genes(older_panel, newer_panel)
        assert set(removed) == {"BRCA2", "TP53"}
        
        older_panel = ["BRCA1", "MYC"]
        newer_panel = ["BRCA1", "MYC", "CHEK2"]
        removed = get_removed_genes(older_panel, newer_panel)
        assert removed == []


class TestAddedGenes:
    """Tests for the get_added_genes function."""

    def test_gene_addition(self):
        """Verify identification of genes added between panel versions."""
        older_panel = ["BRCA1", "MYC", "CHEK2"]
        newer_panel = ["BRCA1", "BRCA2", "MYC", "TP53"]
        added = get_added_genes(older_panel, newer_panel)
        assert set(added) == {"BRCA2", "TP53"}
        
        older_panel = ["BRCA1", "MYC", "CHEK2"]
        newer_panel = ["BRCA1", "MYC", "CHEK2"]
        added = get_added_genes(older_panel, newer_panel)
        assert added == []
