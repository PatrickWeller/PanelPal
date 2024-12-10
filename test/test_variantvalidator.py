import time
import responses
import pytest
import requests
import os
import subprocess
from unittest.mock import patch
from PanelPal.accessories.variant_validator_api_functions import (
    get_gene_transcript_data, extract_exon_info, generate_bed_file, bedtools_merge
)


class TestGetGeneTranscriptData:
    base_url = (
        "https://rest.variantvalidator.org/VariantValidator/tools/gene2transcripts_v2/"
    )

    @responses.activate
    def test_api_success(self):
        # Mock the successful response from the API
        gene = "BRCA1"
        build = "GRCh38"
        url = (
            f"{self.base_url}/{gene}/mane_select/refseq/{build}"
            "?content-type=application%2Fjson"
        )
        mock_response = {
            "gene": "BRCA1",
            "transcripts": [{"id": "NM_007294.3", "gene": "BRCA1"}]  # Example mock response
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
        gene = "BRCA1"
        build = "GRCh38"
        url = (
            f"{self.base_url}/{gene}/mane_select/refseq/{build}"
            "?content-type=application%2Fjson"
        )
        mock_response = {
            "error": "Rate limit exceeded"
        }

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
            "transcripts": [{"id": "NM_007294.3", "gene": "BRCA1"}]
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
        gene = "BRCA1"
        build = "GRCh38"
        url = (
            f"{self.base_url}/{gene}/mane_select/refseq/{build}"
            "?content-type=application%2Fjson"
        )
        mock_response = {
            "error": "Rate limit exceeded"
        }

        # Mock 5 consecutive 429 responses to test the max retries
        for _ in range(5):
            responses.add(
                responses.GET,
                f"{self.base_url}/{gene}/mane_select/refseq/{build}?content-type=application%2Fjson",
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
            requests.exceptions.RequestException, match="HTTP 500: Failed to fetch data for BRCA1."
        ):
            get_gene_transcript_data(gene, build)

    @responses.activate
    def test_api_wrong_genome_build(self):
        gene = "BRCA1"
        build = "egg"
        with pytest.raises(ValueError, match="egg is not a valid genome build. Use GRCh37 or GRCh38."):
            get_gene_transcript_data(gene, build)


class TestExtractExonInfo:
    def test_extract_exon_info_valid_data(self):
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
                                        "genomic_end": 201390858
                                    },
                                    {
                                        "exon_number": 2,
                                        "genomic_start": 201386911,
                                        "genomic_end": 201386940
                                    }
                                ]
                            }
                        }
                    }
                ]
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
                "gene_symbol": "TNNI1"
            },
            {
                "chromosome": "1",
                "exon_start": 201386911,
                "exon_end": 201386940,
                "exon_number": 2,
                "reference": "NM_003281.4",
                "gene_symbol": "TNNI1"
            }
        ]

        # Call the function and check the output
        result = extract_exon_info(mock_gene_transcript_data)
        assert result == expected_output

    def test_extract_exon_info_empty_data(self):
        # Test case with an empty input list
        result = extract_exon_info([])
        assert result == []  # Expect an empty list

    def test_extract_exon_info_missing_exon_structure(self):
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
                        }
                    }
                ]
            }
        ]

        # Call the function and check that it returns an empty list, as no exon data is present
        result = extract_exon_info(mock_gene_transcript_data)
        assert result == []

    def test_extract_exon_info_partial_data(self):
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
                                        "genomic_start": 201390801
                                        # Missing "genomic_end" field
                                    }
                                ]
                            }
                        }
                    }
                ]
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
                "gene_symbol": "TNNI1"
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
                                "genomic_end": 43044685
                            },
                            {
                                "exon_number": 2,
                                "genomic_start": 43045685,
                                "genomic_end": 43045913
                            }
                        ]
                    }
                }
            }
        ]
    }
]

class TestGenerateBedFile:
    @patch('PanelPal.accessories.variant_validator_api_functions.get_gene_transcript_data')
    def test_successful_bed_file_generation(self, mock_get_transcript_data, tmp_path):
        """
        Test generate_bed_file creates a valid BED file with correct content
        """
        # Set up the mock to return predefined transcript data
        mock_get_transcript_data.return_value = MOCK_TRANSCRIPT_DATA
        
        # Change the current working directory to the temporary directory
        os.chdir(tmp_path)
        
        # Define test parameters
        gene_list = ['BRCA1']
        panel_name = 'TestPanel'
        panel_version = '1'
        genome_build = 'GRCh38'
        
        # Call the function
        generate_bed_file(gene_list, panel_name, panel_version, genome_build)
        
        # Check if the file was created
        output_file = f"{panel_name}_v{panel_version}_{genome_build}.bed"
        assert os.path.exists(output_file)
        
        # Read and verify file contents
        with open(output_file, 'r') as f:
            content = f.readlines()
        
        assert len(content) > 0, "BED file should not be empty"
        
        # Verify specific aspects of the generated BED file
        for line in content:
            parts = line.strip().split('\t')
            assert len(parts) == 4, "BED file should have 4 columns"
            assert parts[0] == '17'  # Chromosome from mock data
            assert int(parts[1]) >= 0  # Start position should be non-negative
            assert int(parts[2]) > int(parts[1])  # End position should be greater than start
            assert '|' in parts[3]  # Concatenated info column

    @patch('PanelPal.accessories.variant_validator_api_functions.get_gene_transcript_data')
    def test_error_handling(self, mock_get_transcript_data):
        """
        Test generate_bed_file handles API errors gracefully
        """
        # Mock get_gene_transcript_data to raise an exception
        mock_get_transcript_data.side_effect = Exception("API Error")
        
        # Expect the function to raise a SystemExit
        with pytest.raises(SystemExit):
            generate_bed_file(['ErrorGene'], 'TestPanel', '1', 'GRCh38')

class TestBedToolsMerge:
#     def test_successful_merge(self, tmp_path):
#         """
#         Test bedtools_merge creates a valid merged BED file
#         """
#         os.chdir(tmp_path)
        
#         # Create a sample input BED file
#         input_file = "test.bed"
#         with open(input_file, 'w') as f:
#             f.write("chr1\t100\t200\tinfo1\n")
#             f.write("chr1\t150\t250\tinfo2\n")
        
#         # Perform merge operation
#         bedtools_merge('TestPanel', '1', 'GRCh38', directory=tmp_path)
        
#         # Check if merged file exists
#         merged_file = tmp_path / 'TestPanel_v1_GRCh38_merged.bed'
#         assert merged_file.exists(), f"Expected output file {merged_file} does not exist."
        
#         # Verify merged file content
#         with open(merged_file, 'r') as f:
#             content = f.readlines()
        
#         assert len(content) > 0, "Merged BED file should not be empty"
        
#         for line in content:
#             parts = line.strip().split('\t')
#             assert len(parts) == 3, "Merged BED file should have 3 columns"

#         with open(merged_file, 'r') as f:
#             content = f.read()
#         assert "chr1\t100\t250" in content 

    # def test_merge_no_input_file(self, tmp_path):
    #     """
    #     Test bedtools_merge handles non-existent input file
    #     """
    #     os.chdir(tmp_path)
        
    #     # Attempt to merge a non-existent file
    #     with pytest.raises(subprocess.CalledProcessError):
    #         bedtools_merge('NonExistentPanel', '1', 'GRCh38')

    @patch("subprocess.run")
    @patch("PanelPal.accessories.variant_validator_api_functions.logger")
    def test_bedtools_merge_success(self, mock_logger, mock_subprocess_run):
        # Arrange
        panel_name = "R59"
        panel_version = "2"
        genome_build = "GRCh38"
        bed_file = f"{panel_name}_v{panel_version}_{genome_build}.bed"
        merged_bed_file = f"{panel_name}_v{panel_version}_{genome_build}_merged.bed"
        expected_command = f"bedtools sort -i {bed_file} | bedtools merge > {merged_bed_file}"

        # Act
        bedtools_merge(panel_name, panel_version, genome_build)

        # Assert
        mock_subprocess_run.assert_called_once_with(expected_command, shell=True, check=True)
        mock_logger.info.assert_called_once_with("Successfully sorted and merged BED file to %s", merged_bed_file)


    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "bedtools merge"))
    @patch("PanelPal.accessories.variant_validator_api_functions.logger")
    def test_bedtools_merge_failure(self, mock_logger, mock_subprocess_run):
        # Arrange
        panel_name = "R59"
        panel_version = "2"
        genome_build = "GRCh38"

        # Act & Assert
        with pytest.raises(subprocess.CalledProcessError):
            bedtools_merge(panel_name, panel_version, genome_build)

        mock_logger.error.assert_called_once()
        assert "Error during bedtools operation" in mock_logger.error.call_args[0][0]