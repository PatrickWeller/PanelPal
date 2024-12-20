import argparse
import unittest
from unittest.mock import patch, MagicMock
from PanelPal.panel_to_genes import parse_arguments, write_genes_to_file, main

class TestPanelToGenes(unittest.TestCase):
    """
    Unit tests for the PanelPal panel_to_genes module.

    Classes:
        TestPanelToGenes: Contains unit tests for the panel_to_genes functions.

    Methods:
        test_parse_arguments(self, mock_parse_args):
            Tests the parse_arguments function to ensure it correctly parses command-line arguments.

        test_write_genes_to_file(self, mock_logger, mock_open):
            Tests the write_genes_to_file function to ensure it writes the gene list to a file correctly.

        test_main(self, mock_logger, mock_write_genes_to_file, mock_get_genes, mock_get_response_old_panel_version, mock_get_response, mock_is_valid_panel_id, mock_parse_arguments):
            Tests the main function to ensure it executes the workflow correctly, including parsing arguments, validating panel ID, fetching responses, getting genes, and writing genes to a file.
    """

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments(self, mock_parse_args):
        """
        Test the parse_arguments function.

        This test verifies that the parse_arguments function correctly parses
        command-line arguments and returns an argparse.Namespace object with
        the expected attributes.

        Args:
            mock_parse_args (Mock): A mock object for the parse_args function.

        Returns:
            None
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

        This test verifies that the write_genes_to_file function correctly writes a list of genes to a file.
        It checks that the file is opened with the correct parameters, that each gene is written to the file,
        and that an info log message is generated indicating the file to which the genes were written.

        Args:
            mock_logger (Mock): A mock object for the logger.
            mock_open (Mock): A mock object for the open function.
        """
        gene_list = ['BRCA1', 'BRCA2', 'TP53']
        output_file = 'test_genes.tsv'
        write_genes_to_file(gene_list, output_file)
        mock_open.assert_called_once_with(output_file, 'w', encoding='utf-8')
        mock_open().write.assert_any_call('BRCA1\n')
        mock_open().write.assert_any_call('BRCA2\n')
        mock_open().write.assert_any_call('TP53\n')
        mock_logger.info.assert_called_once_with("Gene list written to file: %s", output_file)

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

        This test verifies that the main function correctly processes the input arguments,
        validates the panel ID, retrieves the panel response, fetches the genes, and writes
        the genes to a file. It also checks that appropriate logging is performed.

        Mocks:
            mock_logger: Mock for the logger.
            mock_write_genes_to_file: Mock for the function that writes genes to a file.
            mock_get_genes: Mock for the function that retrieves genes.
            mock_get_response_old_panel_version: Mock for the function that retrieves the response for an old panel version.
            mock_get_response: Mock for the function that retrieves the response for a panel.
            mock_is_valid_panel_id: Mock for the function that validates the panel ID.
            mock_parse_arguments: Mock for the function that parses command-line arguments.

        Assertions:
            - The parse_arguments function is called once.
            - The is_valid_panel_id function is called once with the correct panel ID.
            - The get_response function is called once with the correct panel ID.
            - The get_response_old_panel_version function is called once with the correct panel ID and version.
            - The get_genes function is called once with the correct response and confidence status.
            - The write_genes_to_file function is called once with the correct genes and filename.
            - The logger.info function is called with the correct command execution message.
        """
        mock_parse_arguments.return_value = argparse.Namespace(
            panel_id='R207', panel_version=1.2, confidence_status='green'
        )
        mock_is_valid_panel_id.return_value = True
        mock_get_response.return_value = MagicMock(json=lambda: {'id': '1234'})
        mock_get_response_old_panel_version.return_value = MagicMock()
        mock_get_genes.return_value = ['BRCA1', 'BRCA2', 'TP53']

        main()

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