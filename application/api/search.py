"""Typesense client wrapper module for CrownCorridor fast read property search."""

import logging
import os
from typing import Any

import typesense
from fastapi import HTTPException

logger = logging.getLogger("crowncorridor.api.search")

# Configuration from environment
TYPESENSE_HOST = os.getenv("TYPESENSE_HOST", "localhost")
TYPESENSE_PORT = os.getenv("TYPESENSE_PORT", "8108")
TYPESENSE_PROTOCOL = os.getenv("TYPESENSE_PROTOCOL", "http")
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY")

if not TYPESENSE_API_KEY:
    # Allow dry-run or testing overrides if set later, but warn or enforce explicitly when client initialized
    pass

COLLECTION_NAME = "properties"


def get_typesense_client() -> typesense.Client:
    """Creates and returns a Typesense client instance.

    Returns:
        typesense.Client: Configured Typesense client object.

    Raises:
        ValueError: If TYPESENSE_API_KEY environment variable is not set.
    """
    api_key = os.getenv("TYPESENSE_API_KEY")
    if not api_key:
        raise ValueError("TYPESENSE_API_KEY environment variable is required.")

    return typesense.Client(
        {
            "nodes": [
                {
                    "host": TYPESENSE_HOST,
                    "port": TYPESENSE_PORT,
                    "protocol": TYPESENSE_PROTOCOL,
                }
            ],
            "api_key": api_key,
            "connection_timeout_seconds": 2,
        }
    )


def search_properties(
    q: str,
    state_code: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_cagr: float | None = None,
    sort_by: str = "registration_date:desc",
    page: int = 1,
    per_page: int = 20,
    filter_by_override: str | None = None,
    client: typesense.Client | None = None,
) -> dict[str, Any]:
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
        filter_by_override (Optional[str]): Explicit Typesense filter_by expression overriding defaults.
        client (Optional[typesense.Client]): Optional Typesense client override for testing.

    Returns:
        Dict[str, Any]: Search response containing total count, page info, search time,
            and formatted results.

    Raises:
        HTTPException: 503 error if search engine fails.
    """
    if client is None:
        client = get_typesense_client()

    if filter_by_override is not None:
        filter_by_str = filter_by_override
    else:
        filter_conditions = []
        if state_code:
            filter_conditions.append(f"state_code:=`{state_code.upper()}`")

        if min_price is not None or max_price is not None:
            low = min_price if min_price is not None else 0
            high = max_price if max_price is not None else 1000000000
            filter_conditions.append(f"sale_consideration:[{low}..{high}]")

        if min_cagr is not None:
            filter_conditions.append(f"cagr:>={min_cagr}")

        filter_by_str = " && ".join(filter_conditions) if filter_conditions else ""

    search_parameters = {
        "q": q if q.strip() else "*",
        "query_by": "locality,mandal,district,property_title,survey_number",
        "filter_by": filter_by_str,
        "sort_by": sort_by,
        "page": page,
        "per_page": per_page,
        "infix": "always",
        "num_typos": 2,
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
                "registration_date": hit["document"].get("registration_date"),
            }
            for hit in response.get("hits", [])
        ]

        return {
            "total_found": response.get("found", 0),
            "page": page,
            "per_page": per_page,
            "search_time_ms": response.get("search_time_ms", 0),
            "results": hits,
        }

    except Exception as exc:
        logger.error(f"Typesense search query failed: {exc}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Search service unavailable: {str(exc)}")


def get_hierarchical_structure(
    state_code: str, client: typesense.Client | None = None
) -> dict[str, Any]:
    """Retrieves nested District -> Mandal hierarchy for a given state code.

    Args:
        state_code (str): State code ('TS' or 'AP').
        client (Optional[typesense.Client]): Optional Typesense client override.

    Returns:
        Dict[str, Any]: Hierarchical structure of state, districts, and mandals with property counts.

    Raises:
        HTTPException: 503 error if search engine fails.
    """
    if client is None:
        client = get_typesense_client()

    state_norm = state_code.upper()

    # Step 1: Query district facets for state
    district_search_params = {
        "q": "*",
        "query_by": "locality,mandal,district",
        "filter_by": f"state_code:=`{state_norm}`",
        "facet_by": "district",
        "max_facet_values": 250,
        "per_page": 0,
    }

    try:
        dist_response = client.collections[COLLECTION_NAME].documents.search(district_search_params)
        total_found = dist_response.get("found", 0)

        district_counts = {}
        for facet in dist_response.get("facet_counts", []):
            if facet.get("field_name") == "district":
                district_counts = {item["value"]: item["count"] for item in facet.get("counts", [])}

        if not district_counts:
            return {
                "state_code": state_norm,
                "total_properties": total_found,
                "districts": [],
            }

        # Step 2: Use multi_search to fetch per-district mandal facets in a single call
        districts_sorted = sorted(district_counts.keys())
        multi_search_requests = {
            "searches": [
                {
                    "collection": COLLECTION_NAME,
                    "q": "*",
                    "query_by": "locality,mandal,district",
                    "filter_by": f"state_code:=`{state_norm}` && district:=`{d_name}`",
                    "facet_by": "mandal",
                    "max_facet_values": 250,
                    "per_page": 0,
                }
                for d_name in districts_sorted
            ]
        }

        multi_response = client.multi_search.perform(multi_search_requests, {})
        results_list = multi_response.get("results", [])

        districts_list = []
        for idx, d_name in enumerate(districts_sorted):
            d_count = district_counts[d_name]
            d_result = results_list[idx] if idx < len(results_list) else {}
            mandal_counts = {}
            for facet in d_result.get("facet_counts", []):
                if facet.get("field_name") == "mandal":
                    mandal_counts = {
                        item["value"]: item["count"] for item in facet.get("counts", [])
                    }

            mandals_list = [
                {"mandal_name": m_name, "property_count": m_count}
                for m_name, m_count in mandal_counts.items()
            ]

            districts_list.append(
                {
                    "district_name": d_name,
                    "property_count": d_count,
                    "mandals": mandals_list,
                }
            )

        return {
            "state_code": state_norm,
            "total_properties": total_found,
            "districts": districts_list,
        }
    except Exception as exc:
        logger.error(
            f"Typesense hierarchy query failed for state {state_norm}: {exc}",
            exc_info=True,
        )
        raise HTTPException(status_code=503, detail=f"Hierarchy service unavailable: {str(exc)}")


def get_properties_by_hierarchy(
    state_code: str,
    district: str,
    mandal: str,
    page: int = 1,
    per_page: int = 20,
    client: typesense.Client | None = None,
) -> dict[str, Any]:
    """Retrieves property list strictly scoped under State -> District -> Mandal.

    Args:
        state_code (str): State code ('TS' or 'AP').
        district (str): District name.
        mandal (str): Mandal name.
        page (int): Page number.
        per_page (int): Items per page.
        client (Optional[typesense.Client]): Optional Typesense client.

    Returns:
        Dict[str, Any]: Property list response for the specified hierarchy node.
    """
    filter_expr = (
        f"state_code:=`{state_code.upper()}` && district:=`{district}` && mandal:=`{mandal}`"
    )
    return search_properties(
        q="*",
        state_code=state_code,
        sort_by="registration_date:desc",
        page=page,
        per_page=per_page,
        filter_by_override=filter_expr,
        client=client,
    )


def get_property_by_id(
    property_id: str, client: typesense.Client | None = None
) -> dict[str, Any] | None:
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
    except typesense.exceptions.ObjectNotFound:
        return None
    except Exception as exc:
        logger.error(f"Failed to retrieve property '{property_id}': {exc}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"Property retrieval service unavailable: {str(exc)}",
        )


if __name__ == "__main__":
    print("Typesense Search Wrapper initialized.")
    print(f"Host: {TYPESENSE_HOST}:{TYPESENSE_PORT} | Collection: {COLLECTION_NAME}")
