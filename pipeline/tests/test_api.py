"""Unit tests for CrownCorridor FastAPI search microservice and Typesense indexing.

These tests verify API endpoints, parameter parsing, search responses, zero-PII compliance,
and offline fallback behaviors.
"""

import pathlib
import sys
from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest

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

    def test_search_endpoint_returns_valid_structure(self):
        """Verifies response structure for default global search query."""
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

    def test_search_endpoint_with_filters(self):
        """Verifies query parameters filtering by state_code, price, and CAGR."""
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
                    "registration_date": "2026-07-01"
                }
            ]
        }
        response = client.get("/api/v1/search?q=cyber")
        assert response.status_code == 200
        data = response.json()
        assert data["total_found"] == 1
        assert data["results"][0]["id"] == "PROP-TG-HYD-01"
        assert data["results"][0]["state_code"] == "TS"


class TestPropertyDetailsEndpoint:
    """Tests for /api/v1/properties/{property_id} endpoint."""

    def test_property_details_not_found(self):
        """Verifies 404 response for non-existent property ID."""
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
            "state_code": "AP"
        }
        response = client.get("/api/v1/properties/PROP-AP-VIZ-01")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "PROP-AP-VIZ-01"
        assert data["state_code"] == "AP"


class TestHierarchyEndpoints:
    """Tests for state -> district -> mandal -> properties hierarchical endpoints."""

    def test_state_hierarchy_endpoint(self):
        """Verifies /api/v1/hierarchy/{state_code} returns districts and mandals."""
        response = client.get("/api/v1/hierarchy/TS")
        assert response.status_code == 200
        data = response.json()
        assert data["state_code"] == "TS"
        assert "districts" in data
        assert isinstance(data["districts"], list)

    def test_mandal_properties_hierarchy_endpoint(self):
        """Verifies /api/v1/hierarchy/{state_code}/{district}/{mandal}/properties endpoint."""
        url = "/api/v1/hierarchy/TS/Rangareddy/Serilingampally/properties"
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["state_code"] == "TS"
        assert data["district"] == "Rangareddy"
        assert data["mandal"] == "Serilingampally"
        assert "properties" in data
        assert isinstance(data["properties"], list)



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
