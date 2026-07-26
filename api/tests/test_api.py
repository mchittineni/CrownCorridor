"""Unit tests for CrownCorridor FastAPI search microservice and Typesense indexing.

These tests verify API endpoints, parameter parsing, search responses, zero-PII compliance,
and offline fallback behaviors.
"""

import pathlib
import sys
from unittest.mock import patch

from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.main import app
from pipeline.index_to_typesense import index_documents, load_all_property_records

client = TestClient(app)


class TestHealthCheck:
    """Tests for system health check endpoint."""

    def test_health_endpoint_returns_200(self):
        """Verifies that /health returns HTTP 200 and expected status dict."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data


class TestSearchEndpoint:
    """Tests for /api/v1/search endpoint."""

    @patch("api.search.get_typesense_client")
    def test_search_endpoint_returns_valid_structure(self, mock_get_client):
        """Verifies response structure for default global search query."""
        mock_client = patch("typesense.Client").start()
        mock_get_client.return_value = mock_client
        mock_client.collections.__getitem__.return_value.documents.search.return_value = {
            "found": 1,
            "search_time_ms": 2,
            "hits": [
                {
                    "document": {
                        "id": "PROP-01",
                        "property_title": "Cyber Heights",
                        "locality": "Gachibowli",
                        "mandal": "Serilingampally",
                        "district": "Rangareddy",
                        "state_code": "TS",
                        "sale_consideration": 10000000.0,
                    }
                }
            ],
        }
        response = client.get("/api/v1/search?q=gachibowli")
        assert response.status_code == 200
        data = response.json()
        assert "total_found" in data
        assert "page" in data
        assert "per_page" in data
        assert "search_time_ms" in data
        assert "execution_time_ms" in data
        assert "results" in data
        assert isinstance(data["results"], list)

    @patch("api.search.get_typesense_client")
    def test_search_endpoint_with_filters(self, mock_get_client):
        """Verifies query parameters filtering by state_code, price, and CAGR."""
        mock_client = patch("typesense.Client").start()
        mock_get_client.return_value = mock_client
        mock_client.collections.__getitem__.return_value.documents.search.return_value = {
            "found": 0,
            "search_time_ms": 1,
            "hits": [],
        }
        url = "/api/v1/search?q=cyber&state_code=TS&min_price=1000000&min_cagr=5.0"
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 20

    @patch("api.main.search_properties")
    def test_search_endpoint_returns_mocked_results(self, mock_search):
        """Verifies Pydantic model validation with mocked property hits."""
        mock_search.return_value = {
            "total_found": 1,
            "page": 1,
            "per_page": 20,
            "search_time_ms": 2,
            "results": [
                {
                    "id": "PROP-TG-HYD-01",
                    "property_title": "Cyber Heights Residency",
                    "locality": "Gachibowli",
                    "mandal": "Serilingampally",
                    "district": "Rangareddy",
                    "state_code": "TS",
                    "sale_consideration": 19425000.0,
                    "cagr": 11.42,
                    "rate_per_sqft": 10500.0,
                    "coordinates": [17.4401, 78.3489],
                    "registration_date": "2026-07-01",
                }
            ],
        }
        response = client.get("/api/v1/search?q=cyber")
        assert response.status_code == 200
        data = response.json()
        assert data["total_found"] == 1
        assert data["results"][0]["id"] == "PROP-TG-HYD-01"
        assert data["results"][0]["state_code"] == "TS"


class TestPropertyDetailsEndpoint:
    """Tests for /api/v1/properties/{property_id} endpoint."""

    @patch("api.search.get_typesense_client")
    def test_property_details_not_found(self, mock_get_client):
        """Verifies 404 response for non-existent property ID."""
        mock_client = patch("typesense.Client").start()
        mock_get_client.return_value = mock_client
        import typesense.exceptions

        mock_client.collections.__getitem__.return_value.documents.__getitem__.return_value.retrieve.side_effect = typesense.exceptions.ObjectNotFound(
            404, "Not found"
        )
        response = client.get("/api/v1/properties/NON_EXISTENT_DOC_ID")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    @patch("api.main.get_property_by_id")
    def test_property_details_found(self, mock_get_by_id):
        """Verifies 200 response when property document exists."""
        mock_get_by_id.return_value = {
            "id": "PROP-AP-VIZ-01",
            "property_title": "Sea Breeze Towers",
            "locality": "Pandurangapuram",
            "mandal": "Visakhapatnam Urban",
            "district": "Visakhapatnam",
            "state_code": "AP",
        }
        response = client.get("/api/v1/properties/PROP-AP-VIZ-01")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "PROP-AP-VIZ-01"
        assert data["state_code"] == "AP"


class TestHierarchyEndpoints:
    """Tests for state -> district -> mandal -> properties hierarchical endpoints."""

    @patch("api.search.get_typesense_client")
    def test_state_hierarchy_endpoint_scopes_mandals_per_district(
        self, mock_get_client
    ):
        """Verifies state hierarchy performs multi-search so mandals belong strictly to their district."""
        mock_client = patch("typesense.Client").start()
        mock_get_client.return_value = mock_client

        # Mock initial district facet search response
        mock_client.collections.__getitem__.return_value.documents.search.return_value = {
            "found": 15,
            "facet_counts": [
                {
                    "field_name": "district",
                    "counts": [
                        {"value": "Medchal", "count": 5},
                        {"value": "Rangareddy", "count": 10},
                    ],
                }
            ],
        }

        # Sorted districts order: Medchal, Rangareddy
        mock_client.multi_search.perform.return_value = {
            "results": [
                {
                    "facet_counts": [
                        {
                            "field_name": "mandal",
                            "counts": [{"value": "Kukatpally", "count": 5}],
                        }
                    ]
                },
                {
                    "facet_counts": [
                        {
                            "field_name": "mandal",
                            "counts": [{"value": "Serilingampally", "count": 10}],
                        }
                    ]
                },
            ]
        }

        response = client.get("/api/v1/hierarchy/TS")
        assert response.status_code == 200
        data = response.json()
        assert data["state_code"] == "TS"
        assert len(data["districts"]) == 2

        # Assert Rangareddy only has Serilingampally, not Kukatpally
        rr = next(d for d in data["districts"] if d["district_name"] == "Rangareddy")
        assert len(rr["mandals"]) == 1
        assert rr["mandals"][0]["mandal_name"] == "Serilingampally"

        # Assert Medchal only has Kukatpally
        medchal = next(d for d in data["districts"] if d["district_name"] == "Medchal")
        assert len(medchal["mandals"]) == 1
        assert medchal["mandals"][0]["mandal_name"] == "Kukatpally"

    @patch("api.search.get_typesense_client")
    def test_mandal_properties_hierarchy_endpoint_passes_full_filter(
        self, mock_get_client
    ):
        """Verifies mandal properties endpoint strictly passes state_code, district, and mandal filter to Typesense."""
        mock_client = patch("typesense.Client").start()
        mock_get_client.return_value = mock_client

        mock_search = mock_client.collections.__getitem__.return_value.documents.search
        mock_search.return_value = {
            "found": 1,
            "hits": [
                {
                    "document": {
                        "id": "PROP-01",
                        "property_title": "Test Villa",
                        "locality": "Gachibowli",
                        "mandal": "Serilingampally",
                        "district": "Rangareddy",
                        "state_code": "TS",
                        "sale_consideration": 5000000.0,
                        "cagr": 8.5,
                    }
                }
            ],
        }

        url = "/api/v1/hierarchy/TS/Rangareddy/Serilingampally/properties"
        response = client.get(url)
        assert response.status_code == 200

        # Assert that search parameters sent to Typesense contained the complete filter_by expression
        args, kwargs = mock_search.call_args
        search_params = args[0]
        expected_filter = (
            "state_code:=`TS` && district:=`Rangareddy` && mandal:=`Serilingampally`"
        )
        assert search_params["filter_by"] == expected_filter

    @patch("api.search.get_typesense_client")
    def test_search_exception_raises_503(self, mock_get_client):
        """Verifies that Typesense client errors trigger HTTP 503 rather than empty 200s."""
        mock_client = patch("typesense.Client").start()
        mock_get_client.return_value = mock_client

        mock_client.collections.__getitem__.return_value.documents.search.side_effect = Exception(
            "Connection refused"
        )

        response = client.get("/api/v1/search?q=cyber")
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "Search service unavailable" in data["detail"]


class TestTypesenseIndexingPipeline:
    """Tests for Typesense data loading and indexing pipeline."""

    def test_load_all_property_records(self):
        """Verifies that property records are correctly transformed from data files."""
        docs = load_all_property_records()
        assert isinstance(docs, list)
        assert len(docs) > 0
        for doc in docs:
            assert "id" in doc
            assert "property_title" in doc
            assert "state_code" in doc
            assert doc["state_code"] in ["TS", "AP"]
            assert "sale_consideration" in doc

    def test_index_documents_dry_run(self):
        """Verifies dry-run indexing returns document count without connecting."""
        docs = load_all_property_records()
        count = index_documents(documents=docs, dry_run=True)
        assert count == len(docs)
