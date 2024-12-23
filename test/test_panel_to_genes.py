import argparse
import unittest
from unittest.mock import patch, MagicMock
import pytest
from PanelPal.panel_to_genes import parse_arguments, write_genes_to_file, main

class TestPanelToGenes(unittest.TestCase):
    """Unit tests for the PanelPal panel_to_genes module."""

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments(self, mock_parse_args):
        """
        Test the parse_arguments function.
        
        This test verifies the following:
        - The function returns the expected arguments.
        - The function raises an error if the panel_id argument is missing.
        - The function raises an error if the panel_version argument is missing.
        - The function raises an error if the confidence_status argument is missing.
        - The function raises an error if the confidence_status argument is not one of the expected choices.

        Mocks:
        - mock_parse_args: Mock for the parse_args method of the ArgumentParser class.
        """
        mock_parse_args.return_value = argparse.Namespace(
            panel_id='R207', panel_version=1.2, confidence_status='green'
        )
        args = parse_arguments()
        self.assertEqual(args.panel_id, 'R207')
        self.assertEqual(args.panel_version, 1.2)
        self.assertEqual(args.confidence_status, 'green')

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('PanelPal.panel_to_genes.logger')
    def test_write_genes_to_file(self, mock_logger, mock_open):
        """
        Test the write_genes_to_file function.

        This test verifies the following:
        - The function writes the genes to the file in TSV format.
        - The function logs the file path.

        Mocks:
        - mock_logger: Mock for the logger.
        - mock_open: Mock for the built-in open function.
        """
        
        # Set up the mocks
        gene_list = ['BRCA1', 'BRCA2', 'TP53']
        output_file = 'test_genes.tsv'

        # Run the function
        write_genes_to_file(gene_list, output_file)

        # Verify that the function wrote the genes to the file and logged the file path
        mock_open.assert_called_once_with(output_file, 'w', encoding='utf-8')
        mock_open().write.assert_any_call('BRCA1\n')
        mock_open().write.assert_any_call('BRCA2\n')
        mock_open().write.assert_any_call('TP53\n')
        mock_logger.info.assert_called_once_with("Gene list written to file: %s", output_file)

    # Add the following test method to the TestPanelToGenes class
    @patch('PanelPal.panel_to_genes.parse_arguments')
    @patch('PanelPal.panel_to_genes.is_valid_panel_id')
    @patch('PanelPal.panel_to_genes.panel_app_api_functions.get_response')
    @patch('PanelPal.panel_to_genes.panel_app_api_functions.get_response_old_panel_version')
    @patch('PanelPal.panel_to_genes.panel_app_api_functions.get_genes')
    @patch('PanelPal.panel_to_genes.write_genes_to_file')
    @patch('PanelPal.panel_to_genes.logger')
    def test_main(self, mock_logger, mock_write_genes_to_file, mock_get_genes, mock_get_response_old_panel_version, mock_get_response, mock_is_valid_panel_id, mock_parse_arguments):
        """
        Test the main function of the panel to genes script.

        This test verifies the following:
        - Argument parsing is called once with the expected arguments.
        - The panel ID validation function is called once with the correct panel ID.
        - The function to get the response for the panel ID is called once with the correct panel ID.
        - The function to get the response for the old panel version is called once with the correct parameters.
        - The function to get genes is called once with the correct parameters.
        - The function to write genes to a file is called once with the correct parameters.
        - The logger logs the command execution with the correct parameters.

        Mocks:
        - mock_logger: Mock for the logger.
        - mock_write_genes_to_file: Mock for the function that writes genes to a file.
        - mock_get_genes: Mock for the function that retrieves genes.
        - mock_get_response_old_panel_version: Mock for the function that retrieves the response for the old panel version.
        - mock_get_response: Mock for the function that retrieves the response for the panel ID.
        - mock_is_valid_panel_id: Mock for the function that validates the panel ID.
        - mock_parse_arguments: Mock for the function that parses command-line arguments.
        """
        
        # Set up the mocks
        mock_parse_arguments.return_value = argparse.Namespace(
            panel_id='R207', panel_version=1.2, confidence_status='green'
        )
        mock_is_valid_panel_id.return_value = True
        mock_get_response.return_value = MagicMock(json=lambda: {'id': '1234'})
        mock_get_response_old_panel_version.return_value = MagicMock()
        mock_get_genes.return_value = ['BRCA1', 'BRCA2', 'TP53']

        # Run the main function
        main()

        # Verify that the functions were called with the expected parameters
        mock_parse_arguments.assert_called_once()
        mock_is_valid_panel_id.assert_called_once_with('R207')
        mock_get_response.assert_called_once_with('R207')
        mock_get_response_old_panel_version.assert_called_once_with('1234', 1.2)
        mock_get_genes.assert_called_once_with(mock_get_response_old_panel_version.return_value, 'green')
        mock_write_genes_to_file.assert_called_once_with(['BRCA1', 'BRCA2', 'TP53'], 'R207_v1.2_green_genes.tsv')
        mock_logger.info.assert_any_call(
            "Command executed: panel-genes --panel_id %s --panel_version %s --confidence_filter %s",
            'R207', 1.2, 'green'
        )

if __name__ == '__main__':
    unittest.main()