import responses
import pytest
import requests
from accessories.panel_app_api_functions import get_response, get_name_version, get_genes


class TestGetResponse:
    
    def test_get_response_success(self):
        """
        Tests successful api requests generates both a correct json, and a 200 status code
        """
        
        panel_id = "R233"
        
        # This is real data from the api from panel R233
        # It is only one gene so was chosen for brevity.
        # The null values were changed for None for python compatibility.
        # If this test ever fails:
            # it may be because the panel is updated
            # but it may be because the api has changed what data it provides
        # either way, this will require investigation by software devs
        real_json = {
                        "id": 1208,
                        "hash_id": None,
                        "name": "Agammaglobulinaemia with absent BTK expression",
                        "disease_group": "",
                        "disease_sub_group": "",
                        "status": "public",
                        "version": "1.1",
                        "version_created": "2023-09-14T12:48:53.836747Z",
                        "relevant_disorders": [
                            "R233"
                        ],
                        "stats": {
                            "number_of_genes": 1,
                            "number_of_strs": 0,
                            "number_of_regions": 0
                        },
                        "types": [
                            {
                            "name": "GMS Rare Disease",
                            "slug": "gms-rare-disease",
                            "description": "This panel type is used for GMS panels that are not virtual (i.e. could be a wet lab test)"
                            },
                            {
                            "name": "GMS signed-off",
                            "slug": "gms-signed-off",
                            "description": "This panel has undergone review by a NHSE GMS disease specialist group and processes to be signed-off for use within the GMS."
                            }
                        ],
                        "genes": [
                            {
                            "gene_data": {
                                "alias": [
                                "ATK",
                                "XLA",
                                "PSCTK1"
                                ],
                                "biotype": "protein_coding",
                                "hgnc_id": "HGNC:1133",
                                "gene_name": "Bruton tyrosine kinase",
                                "omim_gene": [
                                "300300"
                                ],
                                "alias_name": [
                                "Bruton's tyrosine kinase"
                                ],
                                "gene_symbol": "BTK",
                                "hgnc_symbol": "BTK",
                                "hgnc_release": "2017-11-03",
                                "ensembl_genes": {
                                "GRch37": {
                                    "82": {
                                    "location": "X:100604435-100641183",
                                    "ensembl_id": "ENSG00000010671"
                                    }
                                },
                                "GRch38": {
                                    "90": {
                                    "location": "X:101349447-101390796",
                                    "ensembl_id": "ENSG00000010671"
                                    }
                                }
                                },
                                "hgnc_date_symbol_changed": "1986-01-01"
                            },
                            "entity_type": "gene",
                            "entity_name": "BTK",
                            "confidence_level": "3",
                            "penetrance": None,
                            "mode_of_pathogenicity": "",
                            "publications": [],
                            "evidence": [
                                "NHS GMS",
                                "Expert Review Green"
                            ],
                            "phenotypes": [],
                            "mode_of_inheritance": "X-LINKED: hemizygous mutation in males, monoallelic mutations in females may cause disease (may be less severe, later onset than males)",
                            "tags": [],
                            "transcript": None
                            }
                        ],
                        "strs": [],
                        "regions": []
                        }
        
        # Runs the function to access the API
        response = get_response(panel_id)
        
        # Performs the test that the response code is successful
        assert response.status_code == 200
        # Performs the test that the json accessed matches the one above
        assert response.json() == real_json


    @responses.activate
    def test_get_response_not_found(self):
        """
        Tests for 404 errors
        """
        
        panel_id = "R293"
        url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_id}"
        
        # If a request is made, generate a mock 404 Not Found response
        responses.add(responses.GET, url, status=404)

        # Test that a corresponding exception is raised.
        with pytest.raises(Exception, match=f"Panel {panel_id} not found."):
            get_response(panel_id)


    @responses.activate
    def test_get_response_server_error(self):
        """
        Tests for 500 Errors
        """
        panel_id = "R293"
        url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_id}"
        
        # If a request is made, generate a mock 500 Server Error response
        responses.add(responses.GET, url, status=500)
        
        # Test that a corresponding exception is raised.
        with pytest.raises(Exception, match="Server error: The server failed to process the request."):
            get_response(panel_id)


    @responses.activate
    def test_get_response_service_unavailable(self):
        """
        Tests for 503 Errors
        """
        panel_id = "R293"
        url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_id}"
        
        # If a request is made, generate a mock 503 Service Unavailable response
        responses.add(responses.GET, url, status=503)

        # Test that a corresponding exception is raised.
        with pytest.raises(Exception, match="Service unavailable: Please try again later."):
            get_response(panel_id)


class TestGetNameVersion:

    @responses.activate
    def test_get_name_version_failure(self):
        """
        Tests that non 200 codes return None
        """
        
        # This URL is irrelevant since we're mocking the response
        url = "https://panelapp.genomicsengland.co.uk/api/v1/panels/R233"

        # Mock the failed response (404)
        responses.add(
            responses.GET, url,
            json={"detail": "Not found."},
            status=404
        )
        
        # Generates the mock response
        response = requests.get(url)
        result = get_name_version(response)
        # Tests that the response returns blank dict in this function
        assert result == {'name': 'N/A', 'panel_pk': 'N/A', 'version': 'N/A'}
    
    
    def test_success(self):
        """
        Tests a successful api response
        """
        
        # This URL is irrelevant since we're mocking the response
        url = "https://panelapp.genomicsengland.co.uk/api/v1/panels/R233"

        # Creates a mock response
        responses.add(
            responses.GET, url, status=200,
            json={
                "id": 1208,
                "name": "Agammaglobulinaemia with absent BTK expression",
                "version": "1.1"
            }
        )
        
        # Generates the mock response
        response = requests.get(url)
        result = get_name_version(response)
        
        # Tests that a successful api response creates a panel name and version OK
        assert result == {
            "name": "Agammaglobulinaemia with absent BTK expression",
            "panel_pk": 1208,
            "version": "1.1"
            }
        
        
class TestGetGenes:
    
    @responses.activate
    def test_response(self):
        ...
    
    def test_succcess(self):
        ...