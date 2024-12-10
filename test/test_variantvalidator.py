import time
import responses
import pytest
import requests
#from unittest.mock import patch
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

class TestGenerateBedFile:
    ...


class TestBedToolsMerge:
    ...