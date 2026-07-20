"""Typesense client wrapper module for CrownCorridor fast read property search."""

import os
from typing import Any, Dict, Optional
import typesense

# Configuration from environment with default values
TYPESENSE_HOST = os.getenv("TYPESENSE_HOST", "localhost")
TYPESENSE_PORT = os.getenv("TYPESENSE_PORT", "8108")
TYPESENSE_PROTOCOL = os.getenv("TYPESENSE_PROTOCOL", "http")
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY", "xyz123-crowncorridor-key")

COLLECTION_NAME = "properties"


def get_typesense_client() -> typesense.Client:
    """Creates and returns a Typesense client instance.

    Returns:
        typesense.Client: Configured Typesense client object.
    """
    return typesense.Client({
        'nodes': [{
            'host': TYPESENSE_HOST,
            'port': TYPESENSE_PORT,
            'protocol': TYPESENSE_PROTOCOL
        }],
        'api_key': TYPESENSE_API_KEY,
        'connection_timeout_seconds': 2
    })


def search_properties(
    q: str,
    state_code: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_cagr: Optional[float] = None,
    sort_by: str = "registration_date:desc",
    page: int = 1,
    per_page: int = 20,
    client: Optional[typesense.Client] = None
) -> Dict[str, Any]:
    """Executes a fuzzy search across property records using Typesense.

    Args:
        q (str): Query term for matching locality, mandal, district, property title, or survey.
        state_code (Optional[str]): Filter for state code ('TS' or 'AP').
        min_price (Optional[float]): Minimum sale price in INR.
        max_price (Optional[float]): Maximum sale price in INR.
        min_cagr (Optional[float]): Minimum CAGR percentage.
        sort_by (str): Typesense sort specification string.
        page (int): Page number (1-indexed).
        per_page (int): Number of items per page.
        client (Optional[typesense.Client]): Optional Typesense client override for testing.

    Returns:
        Dict[str, Any]: Search response containing total count, page info, search time,
            and formatted results.
    """
    if client is None:
        client = get_typesense_client()

    filter_conditions = []

    if state_code:
        filter_conditions.append(f"state_code:={state_code.upper()}")

    if min_price is not None or max_price is not None:
        low = min_price if min_price is not None else 0
        high = max_price if max_price is not None else 1000000000
        filter_conditions.append(f"sale_consideration:[{low}..{high}]")

    if min_cagr is not None:
        filter_conditions.append(f"cagr:>={min_cagr}")

    filter_by_str = " && ".join(filter_conditions) if filter_conditions else ""

    search_parameters = {
        'q': q if q.strip() else '*',
        'query_by': 'locality,mandal,district,property_title,survey_number',
        'filter_by': filter_by_str,
        'sort_by': sort_by,
        'page': page,
        'per_page': per_page,
        'infix': 'always',
        'num_typos': 2,
    }

    try:
        response = client.collections[COLLECTION_NAME].documents.search(search_parameters)

        hits = [
            {
                "id": hit["document"]["id"],
                "property_title": hit["document"].get("property_title"),
                "locality": hit["document"].get("locality"),
                "mandal": hit["document"].get("mandal"),
                "district": hit["document"].get("district"),
                "state_code": hit["document"].get("state_code"),
                "sale_consideration": hit["document"].get("sale_consideration"),
                "cagr": hit["document"].get("cagr"),
                "rate_per_sqft": hit["document"].get("rate_per_sqft"),
                "coordinates": hit["document"].get("coordinates"),
                "registration_date": hit["document"].get("registration_date")
            }
            for hit in response.get("hits", [])
        ]

        return {
            "total_found": response.get("found", 0),
            "page": page,
            "per_page": per_page,
            "search_time_ms": response.get("search_time_ms", 0),
            "results": hits
        }

    except Exception as exc:
        return {
            "error": str(exc),
            "total_found": 0,
            "page": page,
            "per_page": per_page,
            "search_time_ms": 0,
            "results": []
        }


def get_property_by_id(
    property_id: str,
    client: Optional[typesense.Client] = None
) -> Optional[Dict[str, Any]]:
    """Fetches full historical record for a single property by document ID.

    Args:
        property_id (str): Document ID of the property record.
        client (Optional[typesense.Client]): Optional Typesense client override for testing.

    Returns:
        Optional[Dict[str, Any]]: Property document dict if found, else None.
    """
    if client is None:
        client = get_typesense_client()

    try:
        document = client.collections[COLLECTION_NAME].documents[property_id].retrieve()
        return document
    except Exception:
        return None


if __name__ == "__main__":
    print("Typesense Search Wrapper initialized.")
    print(f"Host: {TYPESENSE_HOST}:{TYPESENSE_PORT} | Collection: {COLLECTION_NAME}")
