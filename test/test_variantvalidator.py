import pytest
import requests
#from unittest.mock import patch
from PanelPal.variant_validator_api_functions import extract_exon_info


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