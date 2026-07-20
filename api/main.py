"""CrownCorridor Fast-Read FastAPI Application.

Provides async endpoints for sub-100ms property search, state-level filtering,
and historical property document retrieval.
"""

import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from api.search import get_property_by_id, search_properties

app = FastAPI(
    title="CrownCorridor Fast-Read API",
    description="Sub-100ms Search and CAGR Analytics API for AP & TS Real Estate Records",
    version="1.0.0"
)

# Enable CORS for frontend integration (app/index.html / portal.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
    sale_consideration: float = Field(..., description="Latest sale consideration in INR")
    cagr: Optional[float] = Field(None, description="Calculated CAGR percentage")
    rate_per_sqft: Optional[float] = Field(None, description="Rate per square foot in INR")
    coordinates: Optional[List[float]] = Field(
        None, description="Latitude and Longitude pair [lat, lng]"
    )
    registration_date: Optional[str] = Field(
        None, description="ISO format date string of registration"
    )


class SearchResponse(BaseModel):
    """Pydantic model representing global search response."""

    total_found: int = Field(..., description="Total matching documents found")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Results per page")
    search_time_ms: int = Field(..., description="Engine search execution time in ms")
    execution_time_ms: float = Field(..., description="Total API handler execution time in ms")
    results: List[PropertyItem] = Field(..., description="List of matching property items")


# --- API Routes ---

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for container and monitoring checks.

    Returns:
        dict: Health status payload.
    """
    return {"status": "healthy", "service": "CrownCorridor Read API"}


@app.get("/api/v1/search", response_model=SearchResponse, tags=["Search"])
async def search_endpoint(
    q: str = Query("", description="Search term (locality, survey number, colony)"),
    state_code: Optional[str] = Query(None, description="State filter: 'TS' or 'AP'"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum sale price in INR"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum sale price in INR"),
    min_cagr: Optional[float] = Query(None, description="Minimum CAGR percentage"),
    sort_by: str = Query("registration_date:desc", description="Typesense sort order string"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page")
):
    """Global smart search endpoint powering the persistent search bar.

    Args:
        q (str): Query search text.
        state_code (Optional[str]): State filter code ('TS' or 'AP').
        min_price (Optional[float]): Minimum price filter in INR.
        max_price (Optional[float]): Maximum price filter in INR.
        min_cagr (Optional[float]): Minimum CAGR percentage.
        sort_by (str): Sorting criteria string.
        page (int): Page number.
        per_page (int): Page size.

    Returns:
        dict: Search response adhering to SearchResponse model.
    """
    start_time = time.time()

    data = search_properties(
        q=q,
        state_code=state_code,
        min_price=min_price,
        max_price=max_price,
        min_cagr=min_cagr,
        sort_by=sort_by,
        page=page,
        per_page=per_page
    )

    execution_time_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "total_found": data["total_found"],
        "page": data["page"],
        "per_page": data["per_page"],
        "search_time_ms": data.get("search_time_ms", 0),
        "execution_time_ms": execution_time_ms,
        "results": data["results"]
    }


@app.get("/api/v1/properties/{property_id}", tags=["Properties"])
async def get_property_details(property_id: str):
    """Returns full registration audit and sale history for a specific property.

    Args:
        property_id (str): Unique document ID for the property.

    Returns:
        dict: Document object for the property.

    Raises:
        HTTPException: If property document is not found.
    """
    doc = get_property_by_id(property_id)
    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"Property document '{property_id}' not found."
        )
    return doc


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
