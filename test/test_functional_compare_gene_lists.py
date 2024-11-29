"""
Functional tests for compare_panel_versions.py script.

Tests the end-to-end functionality of the panel comparison script.
"""

import pytest
import subprocess
import sys
import os

class TestPanelComparisonScriptCLI:
    """Functional tests for the panel comparison script's command-line interface."""

    def test_script_runs_with_valid_inputs(self):
        """
        Verify script runs successfully with valid inputs.
        Assumes PanelApp API is accessible.
        """
        # Construct absolute path to the script
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'PanelPal', 
            'compare_panel_versions.py'
        )
        
        # Simulate a valid CLI call
        result = subprocess.run([
            sys.executable, script_path, 
            '-p', 'R255', 
            '-v', '1.0', '1.6'
        ], capture_output=True, text=True)
        
        # Check that the script exits successfully
        assert result.returncode == 0, f"Script failed with error: {result.stderr}"
        
        # Verify output structure
        assert "Removed genes:" in result.stdout
        assert "Added genes:" in result.stdout

    def test_invalid_panel_name(self):
        """
        Test script behavior with an invalid panel name.
        """
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'PanelPal', 
            'compare_panel_versions.py'
        )
        
        result = subprocess.run([
            sys.executable, script_path, 
            '-p', 'X123', 
            '-v', '1.0', '2.0'
        ], capture_output=True, text=True)
        
        # Check that the script exits with an error
        assert result.returncode != 0
        assert "Panel must be an R number" in str(result.stderr)

    def test_filter_options(self):
        """
        Test different filter options.
        """
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'PanelPal', 
            'compare_panel_versions.py'
        )
        
        # Test filter options
        filter_options = ['green', 'amber', 'all']
        
        for filter_opt in filter_options:
            result = subprocess.run([
                sys.executable, script_path, 
                '-p', 'R255', 
                '-v', '1.0', '1.6', 
                '-f', filter_opt
            ], capture_output=True, text=True)
            
            assert result.returncode == 0, f"Failed with {filter_opt} filter: {result.stderr}"

    def test_missing_arguments(self):
        """
        Test script behavior with missing required arguments.
        """
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'PanelPal', 
            'compare_panel_versions.py'
        )
        
        # Test missing panel
        result_no_panel = subprocess.run([
            sys.executable, script_path, 
            '-v', '1.0', '2.0'
        ], capture_output=True, text=True)
        assert result_no_panel.returncode != 0

        # Test missing versions
        result_no_versions = subprocess.run([
            sys.executable, script_path, 
            '-p', 'R123'
        ], capture_output=True, text=True)
        assert result_no_versions.returncode != 0

    def test_panel_R340_versions_1_0_and_3_0(self):
        """
        Test specific scenario for panel R340 between versions 1.0 and 3.0.
        
        Verifies expected output for gene additions.
        """
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'PanelPal', 
            'compare_panel_versions.py'
        )
        
        result = subprocess.run([
            sys.executable, script_path, 
            '-p', 'R340', 
            '-v', '1.0', '3.0'
        ], capture_output=True, text=True)
        
        # Check script exits successfully
        assert result.returncode == 0, f"Script failed with error: {result.stderr}"
        
        # Check specific output
        output = result.stdout.strip()
        assert output == "Removed genes: []\nAdded genes: ['RELT', 'SLC10A7', 'SP6']"