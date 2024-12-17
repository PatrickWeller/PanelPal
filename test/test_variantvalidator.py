"""
Test suite for the `variant_validator_api_functions` module.

This module contains test cases for functions that interact with the Variant Validator API
and handle genomic data processing, including gene-to-transcript mapping, exon extraction, 
BED file generation, and bedtools merging.

Tests are implemented for the following functions:
- `get_gene_transcript_data`: Retrieves gene-to-transcript data from the Variant Validator API.
- `extract_exon_info`: Extracts exon-specific information from gene transcript data.
- `generate_bed_file`: Generates a BED file from gene transcript data.
- `bedtools_merge`: Merges sorted BED files using bedtools.

Tested functions:
-----------------
1. `get_gene_transcript_data`: Retrieves transcript data for a given gene.
2. `extract_exon_info`: Processes and extracts exon data from gene transcript data.
3. `generate_bed_file`: Generates a BED file with transcript data.
4. `bedtools_merge`: Merges multiple BED files using bedtools.

Test cases include:
-------------------
- Successful API calls and data retrieval.
- Handling rate-limited API responses with retries.
- Error handling for invalid genome builds, server errors, and API failures.
- Exon extraction with missing or incomplete data.
- Verification of correct BED file format and content.
- Ensuring subprocess calls and logging during bedtools file merging.

Tests also mock external dependencies like API calls and subprocess commands
to ensure the functionality of the methods independently of actual network requests
or external tools.
"""

import time
import os
import subprocess
from unittest.mock import patch
import responses
import pytest
import requests
from PanelPal.accessories.variant_validator_api_functions import (
    get_gene_transcript_data,
    extract_exon_info,
    generate_bed_file,
    bedtools_merge,
)


class TestGetGeneTranscriptData:
    """
    Test cases for the `get_gene_transcript_data` function.

    Attributes
    ----------
    base_url : str
        The base URL for the gene-to-transcripts API endpoint.
    """
    base_url = (
        "https://rest.variantvalidator.org/VariantValidator/tools/gene2transcripts_v2/"
    )

    @responses.activate
    def test_api_success(self):
        """Test successful API response for valid gene and build."""
        # Set up test parameters
        gene = "BRCA1"
        build = "GRCh38"
        url = (
            f"{self.base_url}/{gene}/mane_select/refseq/{build}"
            "?content-type=application%2Fjson"
        )

        # Mock the successful response from the API
        mock_response = {
            "gene": "BRCA1",
            "transcripts": [
                {"id": "NM_007294.3", "gene": "BRCA1"}
            ],  # Example mock response
        }

        # Mock the GET request to return the mock response with a 200 status code
        responses.add(
            responses.GET,
            url,
            json=mock_response,
            status=200,
        )

        # Call the function and assert the expected result
        result = get_gene_transcript_data(gene, build)
        assert result == mock_response

    @responses.activate
    def test_api_rate_limit_exceeded_with_retries(self):
        """Test API retries on rate limit exceeded (429) responses."""
        # Set up test parameters
        gene = "BRCA1"
        build = "GRCh38"
        url = (
            f"{self.base_url}/{gene}/mane_select/refseq/{build}"
            "?content-type=application%2Fjson"
        )
        mock_response = {"error": "Rate limit exceeded"}

        # Mock multiple 429 responses to simulate rate limit being exceeded
        for _ in range(3):  # Retry 3 times (max_retries is 4, so 3 retries)
            responses.add(
                responses.GET,
                url,
                json=mock_response,
                status=429,
            )
            time.sleep(1)  # Sleep to simulate wait time between retries

        # The fourth request should succeed with a 200 response
        success_response = {
            "gene": "BRCA1",
            "transcripts": [{"id": "NM_007294.3", "gene": "BRCA1"}],
        }
        responses.add(
            responses.GET,
            url,
            json=success_response,
            status=200,
        )

        # Call the function and assert the expected result
        result = get_gene_transcript_data(gene, build)
        assert result == success_response

        # Verify that the response was retried 3 times and then succeeded
        assert len(responses.calls) == 4  # 3 retries + 1 success

    @responses.activate
    def test_api_rate_limit_exceeded_max_retries(self):
        """Test API behavior when max retries are exceeded."""
        # Set up test parameters
        gene = "BRCA1"
        build = "GRCh38"
        url = (
            f"{self.base_url}/{gene}/mane_select/refseq/{build}"
            "?content-type=application%2Fjson"
        )
        mock_response = {"error": "Rate limit exceeded"}

        # Mock 5 consecutive 429 responses to test the max retries
        for _ in range(5):
            responses.add(
                responses.GET,
                url,
                json=mock_response,
                status=429,
            )
            time.sleep(1)

        # The function should raise an exception after 4 retries
        with pytest.raises(requests.exceptions.RequestException):
            get_gene_transcript_data(gene, build)

        # Verify that the correct number of retries were attempted
        assert len(responses.calls) == 4

    @responses.activate
    def test_other_api_errors(self):
        """Test API behavior on server errors (500)."""
        # Set up test parameters
        gene = "BRCA1"
        build = "GRCh38"
        url = (
            f"{self.base_url}/{gene}/mane_select/refseq/{build}"
            "?content-type=application%2Fjson"
        )

        # If a request is made, generate a mock 500 Server Error response
        responses.add(responses.GET, url, status=500)

        # Test that a corresponding exception is raised.
        with pytest.raises(
            requests.exceptions.RequestException,
            match="HTTP 500: Failed to fetch data for BRCA1.",
        ):
            get_gene_transcript_data(gene, build)

    @responses.activate
    def test_api_wrong_genome_build(self):
        """Test ValueError raised for invalid genome build."""
        # Set up test parameters
        gene = "BRCA1"
        build = "egg"

        # Test that a corresponding exception is raised.
        with pytest.raises(
            ValueError, match="egg is not a valid genome build. Use GRCh37 or GRCh38."
        ):
            get_gene_transcript_data(gene, build)


class TestExtractExonInfo:
    """
    Test cases for the `extract_exon_info` function.
    """
    def test_extract_exon_info_valid_data(self):
        """Test extracting exon information from valid gene transcript data."""
        # Example input data based on the provided structure
        mock_gene_transcript_data = [
            {
                "current_symbol": "TNNI1",
                "transcripts": [
                    {
                        "annotations": {"chromosome": "1"},
                        "reference": "NM_003281.4",
                        "genomic_spans": {
                            "NC_000001.10": {
                                "exon_structure": [
                                    {
                                        "exon_number": 1,
                                        "genomic_start": 201390801,
                                        "genomic_end": 201390858,
                                    },
                                    {
                                        "exon_number": 2,
                                        "genomic_start": 201386911,
                                        "genomic_end": 201386940,
                                    },
                                ]
                            }
                        },
                    }
                ],
            }
        ]

        # Expected output data
        expected_output = [
            {
                "chromosome": "1",
                "exon_start": 201390801,
                "exon_end": 201390858,
                "exon_number": 1,
                "reference": "NM_003281.4",
                "gene_symbol": "TNNI1",
            },
            {
                "chromosome": "1",
                "exon_start": 201386911,
                "exon_end": 201386940,
                "exon_number": 2,
                "reference": "NM_003281.4",
                "gene_symbol": "TNNI1",
            },
        ]

        # Call the function and check the output
        result = extract_exon_info(mock_gene_transcript_data)
        assert result == expected_output

    def test_extract_exon_info_empty_data(self):
        """Test extracting exon information when given an empty input list."""
        result = extract_exon_info([])
        assert not result  # Expect an empty list

    def test_extract_exon_info_missing_exon_structure(self):
        """Test extracting exon information when exon structure is missing."""
        # Test case where `exon_structure` is missing
        mock_gene_transcript_data = [
            {
                "current_symbol": "TNNI1",
                "transcripts": [
                    {
                        "annotations": {"chromosome": "1"},
                        "reference": "NM_003281.4",
                        "genomic_spans": {
                            "NC_000001.10": {
                                # Missing exon_structure key
                            }
                        },
                    }
                ],
            }
        ]

        # Call the function and check that it returns an empty list, as no exon data is present
        result = extract_exon_info(mock_gene_transcript_data)
        assert not result

    def test_extract_exon_info_partial_data(self):
        """Test extracting exon information when some exon data fields are missing."""
        # Test case with missing fields in exon data
        mock_gene_transcript_data = [
            {
                "current_symbol": "TNNI1",
                "transcripts": [
                    {
                        "annotations": {"chromosome": "1"},
                        "reference": "NM_003281.4",
                        "genomic_spans": {
                            "NC_000001.10": {
                                "exon_structure": [
                                    {
                                        "exon_number": 1,
                                        "genomic_start": 201390801,
                                        # Missing "genomic_end" field
                                    }
                                ]
                            }
                        },
                    }
                ],
            }
        ]

        # Expected output should only include the fields that have complete data
        expected_output = [
            {
                "chromosome": "1",
                "exon_start": 201390801,
                "exon_end": None,  # Field is missing, so expect None
                "exon_number": 1,
                "reference": "NM_003281.4",
                "gene_symbol": "TNNI1",
            }
        ]

        # Call the function and check the output
        result = extract_exon_info(mock_gene_transcript_data)
        assert result == expected_output


# Sample transcript data for mocking
MOCK_TRANSCRIPT_DATA = [
    {
        "current_symbol": "BRCA1",
        "transcripts": [
            {
                "annotations": {"chromosome": "17"},
                "reference": "NM_007294.4",
                "genomic_spans": {
                    "NC_000017.11": {
                        "exon_structure": [
                            {
                                "exon_number": 1,
                                "genomic_start": 43044294,
                                "genomic_end": 43044685,
                            },
                            {
                                "exon_number": 2,
                                "genomic_start": 43045685,
                                "genomic_end": 43045913,
                            },
                        ]
                    }
                },
            }
        ],
    }
]


class TestGenerateBedFile:
    """
    Test cases for the `generate_bed_file` function.
    """
    @patch(
        "PanelPal.accessories.variant_validator_api_functions.get_gene_transcript_data"
    )
    def test_successful_bed_file_generation(self, mock_get_transcript_data, tmp_path):
        """
        Test generate_bed_file creates a valid BED file with correct content
        """
        # Set up the mock to return predefined transcript data
        mock_get_transcript_data.return_value = MOCK_TRANSCRIPT_DATA

        # Change the current working directory to the temporary directory
        os.chdir(tmp_path)

        # Define test parameters
        gene_list = ["BRCA1"]
        panel_name = "TestPanel"
        panel_version = "1"
        genome_build = "GRCh38"

        # Call the function
        generate_bed_file(gene_list, panel_name, panel_version, genome_build)

        # Check if the file was created
        output_file = f"{panel_name}_v{panel_version}_{genome_build}.bed"
        assert os.path.exists(output_file)

        # Read and verify file contents, check it isn't empty
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.readlines()
        assert len(content) > 0, "BED file should not be empty"

        # Verify specific aspects of the generated BED file
        for line in content:
            parts = line.strip().split("\t")
            assert len(parts) == 4, "BED file should have 4 columns"
            assert parts[0] == "17"  # Chromosome from mock data
            assert int(parts[1]) >= 0  # Start position should be non-negative
            assert int(parts[2]) > int(
                parts[1]
            )  # End position should be greater than start
            assert "|" in parts[3]  # Concatenated info column

    @patch(
        "PanelPal.accessories.variant_validator_api_functions.get_gene_transcript_data"
    )
    def test_error_handling(self, mock_get_transcript_data):
        """
        Test generate_bed_file handles API errors gracefully
        """
        # Mock get_gene_transcript_data to raise an exception
        mock_get_transcript_data.side_effect = Exception("API Error")

        # Expect the function to raise a SystemExit
        with pytest.raises(SystemExit):
            generate_bed_file(["ErrorGene"], "TestPanel", "1", "GRCh38")


class TestBedToolsMerge:
    """
    Test cases for the `bedtools_merge` function.
    """
    @patch("subprocess.run")
    @patch("PanelPal.accessories.variant_validator_api_functions.logger")
    def test_bedtools_merge_success(self, mock_logger, mock_subprocess_run):
        """
        Test that bedtools_merge generates and runs the correct command and logs success.
        """
        # Define test parameters
        panel_name = "R59"
        panel_version = "2"
        genome_build = "GRCh38"

        # Mock BED file names
        bed_file = f"{panel_name}_v{panel_version}_{genome_build}.bed"
        merged_bed_file = f"{panel_name}_v{panel_version}_{genome_build}_merged.bed"

        # Expected command to be run.
        expected_command = (
            f"bedtools sort -i {bed_file} | bedtools merge > {merged_bed_file}"
        )

        # Run the function
        bedtools_merge(panel_name, panel_version, genome_build)

        # Assert the subprocess ran as expected and success message was logged.
        mock_subprocess_run.assert_called_once_with(
            expected_command, shell=True, check=True
        )
        mock_logger.info.assert_called_once_with(
            "Successfully sorted and merged BED file to %s", merged_bed_file
        )

    @patch(
        "subprocess.run", side_effect=subprocess.CalledProcessError(1, "bedtools merge")
    )
    @patch("PanelPal.accessories.variant_validator_api_functions.logger")
    def test_bedtools_merge_failure(self, mock_logger, mock_subprocess_run):
        """ Test that bedtools_merge handles errors and logs failure."""
        # Set up test parameters
        panel_name = "R59"
        panel_version = "2"
        genome_build = "GRCh38"

        # Mock BED file names
        bed_file = f"{panel_name}_v{panel_version}_{genome_build}.bed"
        merged_bed_file = f"{panel_name}_v{panel_version}_{genome_build}_merged.bed"

        # Expected command to be run.
        expected_command = f"bedtools sort -i {bed_file} | bedtools merge > {merged_bed_file}"

        # Trigger the bedtools_merge function and expect an error
        with pytest.raises(subprocess.CalledProcessError):
            bedtools_merge(panel_name, panel_version, genome_build)

        # Assert that subprocess.run was called with the expected command
        mock_subprocess_run.assert_called_once_with(
            expected_command, shell=True, check=True
        )

        # Check that the error was logged correctly
        mock_logger.error.assert_called_once()
        assert "Error during bedtools operation" in mock_logger.error.call_args[0][0]
