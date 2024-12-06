import responses
import pytest
import requests
from PanelPal.accessories.panel_app_api_functions import (
    get_response,
    get_name_version,
    get_genes,
    get_response_old_panel_version,
)
from PanelPal.accessories.panel_app_api_functions import PanelAppError


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
            "relevant_disorders": ["R233"],
            "stats": {
                "number_of_genes": 1,
                "number_of_strs": 0,
                "number_of_regions": 0,
            },
            "types": [
                {
                    "name": "GMS Rare Disease",
                    "slug": "gms-rare-disease",
                    "description": "This panel type is used for GMS panels that are not virtual (i.e. could be a wet lab test)",
                },
                {
                    "name": "GMS signed-off",
                    "slug": "gms-signed-off",
                    "description": "This panel has undergone review by a NHSE GMS disease specialist group and processes to be signed-off for use within the GMS.",
                },
            ],
            "genes": [
                {
                    "gene_data": {
                        "alias": ["ATK", "XLA", "PSCTK1"],
                        "biotype": "protein_coding",
                        "hgnc_id": "HGNC:1133",
                        "gene_name": "Bruton tyrosine kinase",
                        "omim_gene": ["300300"],
                        "alias_name": ["Bruton's tyrosine kinase"],
                        "gene_symbol": "BTK",
                        "hgnc_symbol": "BTK",
                        "hgnc_release": "2017-11-03",
                        "ensembl_genes": {
                            "GRch37": {
                                "82": {
                                    "location": "X:100604435-100641183",
                                    "ensembl_id": "ENSG00000010671",
                                }
                            },
                            "GRch38": {
                                "90": {
                                    "location": "X:101349447-101390796",
                                    "ensembl_id": "ENSG00000010671",
                                }
                            },
                        },
                        "hgnc_date_symbol_changed": "1986-01-01",
                    },
                    "entity_type": "gene",
                    "entity_name": "BTK",
                    "confidence_level": "3",
                    "penetrance": None,
                    "mode_of_pathogenicity": "",
                    "publications": [],
                    "evidence": ["NHS GMS", "Expert Review Green"],
                    "phenotypes": [],
                    "mode_of_inheritance": "X-LINKED: hemizygous mutation in males, monoallelic mutations in females may cause disease (may be less severe, later onset than males)",
                    "tags": [],
                    "transcript": None,
                }
            ],
            "strs": [],
            "regions": [],
        }

        # Runs the function to access the API
        response = get_response(panel_id)

        # Performs the test that the response code is successful
        assert response.status_code == 200
        # Performs the test that the json accessed matches the one above
        assert response.json() == real_json

    @responses.activate
    def test_get_response_timeout(self):
        """
        Tests for Timeout Errors
        """
        panel_id = "R293"
        url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_id}"

        # Simulate a timeout by raising a `ConnectTimeout` when the request is made
        responses.add(
            responses.GET,
            url,
            body=requests.exceptions.ConnectTimeout(),
        )

        # Test that a corresponding exception is raised with the correct message
        with pytest.raises(
            PanelAppError, match="Timeout: Panel R293 request exceeded the time limit."
        ):
            get_response(panel_id)

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
        with pytest.raises(
            Exception, match="Server error: The server failed to process the request."
        ):
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
        with pytest.raises(
            Exception, match="Service unavailable: Please try again later."
        ):
            get_response(panel_id)

    @responses.activate
    def test_http_error_unexpected_status_code(self):
        """
        Test that an unexpected HTTP status code raises a general PanelAppError.
        """
        panel_id = "R400"
        # Define the URL for the mock API call
        url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_id}"

        # Mock the API response with a 400 status code and a response body
        responses.add(responses.GET, url, status=400, body="Bad Request")

        # Assert that the function raises a PanelAppError with the correct message
        with pytest.raises(PanelAppError, match="Error: 400 - Bad Request"):
            get_response(panel_id)

    @responses.activate
    def test_request_exception(self):
        """
        Test that a RequestException raises a PanelAppError.
        """
        panel_id = "R999"
        # Define the URL for the mock API call
        url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_id}"

        # Mock the API response with a connection error
        responses.add(
            responses.GET,
            url,
            body=requests.exceptions.ConnectionError("Connection error"),
        )

        # Assert that the function raises a PanelAppError with the correct message
        with pytest.raises(
            PanelAppError, match=f"Failed to retrieve data for panel {panel_id}."
        ):
            get_response(panel_id)


class TestGetNameVersion:

    @responses.activate
    def test_get_name_version_failure(self):
        """
        Tests that non-200 HTTP status codes return default 'N/A' values.
        """
        # Mock URL used for simulating the API call
        url = "https://panelapp.genomicsengland.co.uk/api/v1/panels/R233"

        # Mock a 404 response with a 'Not found' message in the JSON body
        responses.add(responses.GET, url, json={"detail": "Not found."}, status=404)

        # Send a GET request to the mocked URL
        response = requests.get(url)

        # Call the function being tested
        result = get_name_version(response)

        # Assert that the result contains default 'N/A' values
        assert result == {"name": "N/A", "panel_pk": "N/A", "version": "N/A"}

    @responses.activate
    def test_success(self):
        """
        Tests a successful API response.
        """
        # Mock URL used for simulating the API call
        url = "https://panelapp.genomicsengland.co.uk/api/v1/panels/R233"

        # Mock a successful API response with valid panel data
        responses.add(
            responses.GET,
            url,
            status=200,
            json={
                "id": 1208,
                "name": "Agammaglobulinaemia with absent BTK expression",
                "version": "1.1",
            },
        )

        # Send a GET request to the mocked URL
        response = requests.get(url)

        # Call the function being tested
        result = get_name_version(response)

        # Assert that the result matches the mocked data
        assert result == {
            "name": "Agammaglobulinaemia with absent BTK expression",
            "panel_pk": 1208,
            "version": "1.1",
        }

    @responses.activate
    def test_value_error_on_invalid_json(self):
        """
        Test that the function raises PanelAppError when the response JSON is invalid,
        causing a ValueError during parsing.
        """
        url = "https://panelapp.genomicsengland.co.uk/api/v1/panels/123/?version=1.0"

        # Mock an invalid JSON response (e.g., broken or malformed JSON)
        responses.add(
            responses.GET,
            url,
            body="invalid_json",  # Invalid JSON will trigger a ValueError
            status=200,
        )

        # Perform the request and expect a PanelAppError to be raised
        response = requests.get(url)
        with pytest.raises(PanelAppError, match="Failed to parse panel data."):
            get_name_version(response)


class TestGetGenes:
    @responses.activate
    def test_get_genes_success(self):
        """
        Test that the function returns a list of gene symbols on success.
        """
        # Mock URL used for simulating the API call
        url = "https://panelapp.genomicsengland.co.uk/api/v1/panels/R233"

        # Mock a successful response with gene symbols in the JSON body
        responses.add(
            responses.GET,
            url,
            json={
                "genes": [
                    {"gene_data": {"gene_symbol": "BRCA1"}},
                    {"gene_data": {"gene_symbol": "BRCA2"}},
                ]
            },
            status=200,
        )

        # Send a GET request to the mocked URL
        response = requests.get(url)

        # Call the function being tested
        genes = get_genes(response)

        # Assert that the function returns the correct list of gene symbols
        assert genes == ["BRCA1", "BRCA2"]

    @responses.activate
    def test_get_genes_http_error(self):
        """
        Test that an HTTP error raises requests.exceptions.HTTPError.
        """
        # Mock URL used for simulating the API call
        url = "https://panelapp.genomicsengland.co.uk/api/v1/panels/R233"

        # Mock a 404 response with a 'Not found' message in the JSON body
        responses.add(responses.GET, url, json={"detail": "Not found."}, status=404)

        # Send a GET request to the mocked URL
        response = requests.get(url)

        # Assert that the function raises an HTTPError for the 404 response
        with pytest.raises(requests.exceptions.HTTPError):
            get_genes(response)

    @responses.activate
    def test_get_genes_json_error(self):
        """
        Test that a JSON parsing error raises PanelAppError.
        """
        # Mock URL used for simulating the API call
        url = "https://panelapp.genomicsengland.co.uk/api/v1/panels/R233"

        # Mock a response with invalid JSON content
        responses.add(responses.GET, url, body='{"genes": [invalid_json]}', status=200)

        # Send a GET request to the mocked URL
        response = requests.get(url)

        # Assert that the function raises a PanelAppError for invalid JSON
        with pytest.raises(PanelAppError):
            get_genes(response)


class TestGetResponseOldPanelVersion:
    @responses.activate
    def test_successful_response(self):
        """
        Test that the function returns the response object when the request is successful.
        """
        panel_pk = "123"
        version = "2.0"
        # Construct the URL using panel_pk and version
        url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_pk}/?version={version}"

        # Mock a successful response with status 200 and a success message
        responses.add(responses.GET, url, json={"status": "success"}, status=200)

        # Call the function to test and assert expected response values
        response = get_response_old_panel_version(panel_pk, version)
        assert response.status_code == 200
        assert response.json() == {"status": "success"}

    @responses.activate
    def test_get_response_old_panel_version_timeout(self):
        """
        Tests for Timeout Errors in get_response_old_panel_version
        """
        panel_pk = "123"
        version = "1.0"
        url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_pk}/?version={version}"

        # Simulate a timeout by raising a `ConnectTimeout` when the request is made
        responses.add(
            responses.GET,
            url,
            body=requests.exceptions.ConnectTimeout(),
        )

        # Test that the correct exception is raised with the expected message
        with pytest.raises(
            PanelAppError,
            match=f"Timeout: Panel {panel_pk} request exceeded the time limit. Please try again",
        ):
            get_response_old_panel_version(panel_pk, version)

    @responses.activate
    def test_404_error(self):
        """
        Test that the function raises PanelAppError for a 404 Not Found response.
        """
        panel_pk = "999"
        version = "1.0"
        # Construct the URL for a nonexistent panel version
        url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_pk}/?version={version}"

        # Mock a 404 Not Found response
        responses.add(responses.GET, url, status=404)

        # Expect a PanelAppError to be raised with the correct error message
        with pytest.raises(
            PanelAppError,
            match=f"Failed to retrieve version {version} of panel {panel_pk}.",
        ):
            get_response_old_panel_version(panel_pk, version)

    @responses.activate
    def test_server_error(self):
        """
        Test that the function raises PanelAppError for a 500 Internal Server Error response.
        """
        panel_pk = "123"
        version = "3.0"
        # Construct the URL for the panel and version
        url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_pk}/?version={version}"

        # Mock a 500 Internal Server Error response
        responses.add(responses.GET, url, status=500)

        # Expect a PanelAppError to be raised for server-side issues
        with pytest.raises(
            PanelAppError,
            match=f"Failed to retrieve version {version} of panel {panel_pk}.",
        ):
            get_response_old_panel_version(panel_pk, version)

    @responses.activate
    def test_network_error(self):
        """
        Test that the function raises PanelAppError for network-related issues.
        """
        panel_pk = "456"
        version = "1.1"
        # Construct the URL for the panel and version
        url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/{panel_pk}/?version={version}"

        # Simulate a network-related error such as a connection issue
        responses.add(
            responses.GET,
            url,
            body=responses.ConnectionError("Network error occurred."),
        )

        # Expect a PanelAppError to be raised due to network issues
        with pytest.raises(
            PanelAppError,
            match=f"Failed to retrieve version {version} of panel {panel_pk}.",
        ):
            get_response_old_panel_version(panel_pk, version)
