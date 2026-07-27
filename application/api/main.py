"""CrownCorridor Fast-Read FastAPI Application.

Provides async endpoints for sub-100ms property search, state-level filtering,
and historical property document retrieval.
"""

import logging
import math
import time
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crowncorridor-api")

# pylint: disable=wrong-import-order
from api.search import (  # isort: skip
    get_hierarchical_structure,
    get_properties_by_hierarchy,
    get_property_by_id,
    search_properties,
)


class StateCodeEnum(str, Enum):
    """Supported state codes."""

    TS = "TS"
    AP = "AP"


ALLOWED_SORT_ORDERS = {
    "registration_date:desc",
    "registration_date:asc",
    "sale_consideration:desc",
    "sale_consideration:asc",
    "cagr:desc",
    "cagr:asc",
}

app = FastAPI(
    title="CrownCorridor Fast-Read API",
    description="Sub-100ms Search and CAGR Analytics API for AP & TS Real Estate Records",
    version="1.0.0",
)

# Enable CORS for frontend integration (app/index.html / portal.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


# --- Pydantic Data Models ---


class PropertyItem(BaseModel):
    """Pydantic model representing a search hit property item."""

    id: str = Field(..., description="Unique document ID of the property")
    property_title: str = Field(..., description="Title of the property")
    locality: str = Field(..., description="Locality or colony name")
    mandal: str = Field(..., description="Mandal or SRO jurisdiction")
    district: str = Field(..., description="District name")
    state_code: str = Field(..., description="State code ('TS' or 'AP')")
    sale_consideration: float | None = Field(0.0, description="Latest sale consideration in INR")
    cagr: float | None = Field(None, description="Calculated CAGR percentage")
    rate_per_sqft: float | None = Field(None, description="Rate per square foot in INR")
    coordinates: list[float] | None = Field(
        None, description="Latitude and Longitude pair [lat, lng]"
    )
    registration_date: str | None = Field(
        None, description="ISO format date string of registration"
    )


class HierarchyMandalItem(BaseModel):
    """Pydantic model for mandal summary in hierarchy query."""

    mandal_name: str = Field(..., description="Mandal or SRO jurisdiction name")
    property_count: int = Field(..., description="Number of properties in mandal")


class HierarchyDistrictItem(BaseModel):
    """Pydantic model for district summary in hierarchy query."""

    district_name: str = Field(..., description="District name")
    property_count: int = Field(..., description="Number of properties in district")
    mandals: list[HierarchyMandalItem] = Field(default_factory=list, description="List of mandals")


class HierarchyStateResponse(BaseModel):
    """Pydantic model for state-level hierarchical structure response."""

    state_code: str = Field(..., description="State code ('TS' or 'AP')")
    total_properties: int = Field(..., description="Total properties in state")
    districts: list[HierarchyDistrictItem] = Field(..., description="List of districts in state")


class HierarchyPropertyListResponse(BaseModel):
    """Pydantic model for properties under a specific mandal/district."""

    state_code: str = Field(..., description="State code ('TS' or 'AP')")
    district: str = Field(..., description="District name")
    mandal: str = Field(..., description="Mandal name")
    total_properties: int = Field(..., description="Total properties under mandal")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(20, description="Results per page")
    total_pages: int = Field(1, description="Total pages available")
    has_next: bool = Field(False, description="Whether more pages exist")
    properties: list[PropertyItem] = Field(..., description="List of properties")


class SearchResponse(BaseModel):
    """Pydantic model representing global search response."""

    total_found: int = Field(..., description="Total matching documents found")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Results per page")
    total_pages: int = Field(..., description="Total pages available")
    has_next: bool = Field(..., description="Whether more pages exist")
    search_time_ms: int = Field(..., description="Engine search execution time in ms")
    execution_time_ms: float = Field(..., description="Total API handler execution time in ms")
    results: list[PropertyItem] = Field(..., description="List of matching property items")


# --- API Routes ---


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for container and monitoring checks.

    Returns:
        dict: Health status payload.
    """
    return {"status": "healthy", "service": "CrownCorridor Read API"}


@app.get("/health/ready", tags=["System"])
def readiness_check():
    """Readiness check endpoint that verifies Typesense search connectivity.

    Returns:
        dict: Service readiness status payload.

    Raises:
        HTTPException: 503 if search engine ping fails.
    """
    try:
        from api.search import get_typesense_client

        tc = get_typesense_client()
        tc.collections["properties"].retrieve()
        return {"status": "ready", "search_engine": "connected"}
    except Exception as exc:
        logger.error(f"Readiness check failed: {exc}", exc_info=True)
        raise HTTPException(status_code=503, detail="Search engine unready")


@app.get("/api/v1/search", response_model=SearchResponse, tags=["Search"])
def search_endpoint(
    q: str = Query("", max_length=200, description="Search term (locality, survey number, colony)"),
    state_code: StateCodeEnum | None = Query(None, description="State filter: 'TS' or 'AP'"),
    min_price: float | None = Query(None, ge=0, description="Minimum sale price in INR"),
    max_price: float | None = Query(None, ge=0, description="Maximum sale price in INR"),
    min_cagr: float | None = Query(None, description="Minimum CAGR percentage"),
    sort_by: str = Query("registration_date:desc", description="Typesense sort order string"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
):
    """Global smart search endpoint powering the persistent search bar."""
    if sort_by not in ALLOWED_SORT_ORDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by option '{sort_by}'. Allowed options: {sorted(ALLOWED_SORT_ORDERS)}",
        )

    start_time = time.time()
    state_str = state_code.value if state_code else None

    data = search_properties(
        q=q,
        state_code=state_str,
        min_price=min_price,
        max_price=max_price,
        min_cagr=min_cagr,
        sort_by=sort_by,
        page=page,
        per_page=per_page,
    )

    execution_time_ms = round((time.time() - start_time) * 1000, 2)
    total_found = data["total_found"]
    total_pages = math.ceil(total_found / per_page) if total_found > 0 else 0
    has_next = page < total_pages

    return {
        "total_found": total_found,
        "page": data["page"],
        "per_page": data["per_page"],
        "total_pages": total_pages,
        "has_next": has_next,
        "search_time_ms": data.get("search_time_ms", 0),
        "execution_time_ms": execution_time_ms,
        "results": data["results"],
    }


@app.get(
    "/api/v1/hierarchy/{state_code}",
    response_model=HierarchyStateResponse,
    tags=["Hierarchy"],
)
def get_state_hierarchy(state_code: StateCodeEnum, response: Response):
    """Retrieves the nested District -> Mandal hierarchy for a state."""
    response.headers["Cache-Control"] = "public, max-age=3600, s-maxage=86400"
    data = get_hierarchical_structure(state_code.value)
    return data


@app.get(
    "/api/v1/hierarchy/{state_code}/{district}/{mandal}/properties",
    response_model=HierarchyPropertyListResponse,
    tags=["Hierarchy"],
)
def get_properties_for_mandal(
    state_code: StateCodeEnum,
    district: str,
    mandal: str,
    response: Response,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """Retrieves properties strictly scoped under a specific State -> District -> Mandal node."""
    response.headers["Cache-Control"] = "public, max-age=300"
    data = get_properties_by_hierarchy(
        state_code=state_code.value,
        district=district,
        mandal=mandal,
        page=page,
        per_page=per_page,
    )
    total_found = data["total_found"]
    total_pages = math.ceil(total_found / per_page) if total_found > 0 else 0
    has_next = page < total_pages

    return {
        "state_code": state_code.value,
        "district": district,
        "mandal": mandal,
        "total_properties": total_found,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": has_next,
        "properties": data["results"],
    }


@app.get("/api/v1/properties/{property_id}", response_model=PropertyItem, tags=["Properties"])
def get_property_details(property_id: str, response: Response):
    """Returns full registration audit and sale history for a specific property."""
    doc = get_property_by_id(property_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Property document '{property_id}' not found.")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return doc


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)  # nosec B104
