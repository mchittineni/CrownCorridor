"""CrownCorridor Typesense Indexing Script.

Transforms property registration records and property histories into Typesense
documents and indexes them into the 'properties' collection.
"""

import argparse
import json
import os
import pathlib
from typing import Any, Dict, List
import typesense

ROOT = pathlib.Path(__file__).parent.parent
DATA_DIR = ROOT / "data"

COLLECTION_NAME = "properties"

COLLECTION_SCHEMA: Dict[str, Any] = {
    "name": COLLECTION_NAME,
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "property_title", "type": "string"},
        {"name": "locality", "type": "string", "facet": True},
        {"name": "mandal", "type": "string", "facet": True},
        {"name": "district", "type": "string", "facet": True},
        {"name": "state_code", "type": "string", "facet": True},
        {"name": "sale_consideration", "type": "float"},
        {"name": "cagr", "type": "float", "optional": True},
        {"name": "rate_per_sqft", "type": "float", "optional": True},
        {"name": "coordinates", "type": "float[]", "optional": True},
        {"name": "registration_date", "type": "string", "optional": True, "sort": True},
        {"name": "survey_number", "type": "string", "optional": True},
    ],
    "default_sorting_field": "sale_consideration"
}


def load_all_property_records() -> List[Dict[str, Any]]:
    """Loads and transforms property history records from data files into Typesense documents.

    Returns:
        List[Dict[str, Any]]: Transformed document dicts ready for Typesense indexing.
    """
    documents = []

    files_to_check = [
        DATA_DIR / "property_history.json",
        DATA_DIR / "telangana" / "property_history.json",
        DATA_DIR / "andhra_pradesh" / "property_history.json",
    ]

    seen_ids = set()

    for file_path in files_to_check:
        if not file_path.exists():
            continue

        try:
            content = json.loads(file_path.read_text(encoding="utf-8"))
            properties = content.get("properties", [])
            for p in properties:
                prop_id = p.get("property_id")
                if not prop_id or prop_id in seen_ids:
                    continue
                seen_ids.add(prop_id)

                state_raw = p.get("state", "").lower()
                state_code = "TS" if "telangana" in state_raw else "AP"

                latest_sale = p.get("sale_history", [{}])[-1]
                latest_price = latest_sale.get(
                    "sale_price_inr",
                    p.get("price_summary", {}).get("latest_price_inr", 0)
                )
                rate_sqft = latest_sale.get("price_per_sqft_inr", 0)
                cagr_val = p.get("price_summary", {}).get("cagr_pct", 0.0)

                doc = {
                    "id": prop_id,
                    "property_title": p.get("name", "Property Record"),
                    "locality": p.get("address", "").split(",")[-1].strip() or p.get("mandal", ""),
                    "mandal": p.get("mandal", ""),
                    "district": p.get("district", ""),
                    "state_code": state_code,
                    "sale_consideration": float(latest_price),
                    "cagr": float(cagr_val),
                    "rate_per_sqft": float(rate_sqft),
                    "coordinates": [p.get("lat", 0.0), p.get("lng", 0.0)],
                    "registration_date": latest_sale.get("sale_date", "2026-07-01"),
                    "survey_number": p.get("rera_id", "N/A"),
                }
                documents.append(doc)
        except Exception as err:
            print(f"Warning: Could not process {file_path}: {err}")

    return documents


def index_documents(
    documents: List[Dict[str, Any]],
    host: str = "localhost",
    port: str = "8108",
    protocol: str = "http",
    api_key: str = "xyz123-crowncorridor-key",
    dry_run: bool = False
) -> int:
    """Creates schema and imports documents into Typesense.

    Args:
        documents (List[Dict[str, Any]]): List of property document dicts.
        host (str): Typesense host name.
        port (str): Typesense port.
        protocol (str): Protocol ('http' or 'https').
        api_key (str): Typesense API key.
        dry_run (bool): If True, skips network call and returns document count.

    Returns:
        int: Count of indexed documents.
    """
    if dry_run:
        print(f"[DRY RUN] Transformed {len(documents)} documents for Typesense indexing.")
        for doc in documents:
            print(f"  - Document ID: {doc['id']} | Title: {doc['property_title']} | State: {doc['state_code']}")
        return len(documents)

    client = typesense.Client({
        'nodes': [{
            'host': host,
            'port': port,
            'protocol': protocol
        }],
        'api_key': api_key,
        'connection_timeout_seconds': 5
    })

    try:
        client.collections[COLLECTION_NAME].retrieve()
    except Exception:
        print(f"Creating Typesense collection: {COLLECTION_NAME}")
        client.collections.create(COLLECTION_SCHEMA)

    results = client.collections[COLLECTION_NAME].documents.import_(
        documents,
        {'action': 'upsert'}
    )
    indexed_count = len([r for r in results if r.get('success', True)])
    print(f"Successfully indexed {indexed_count}/{len(documents)} documents to Typesense.")
    return indexed_count


def main():
    """Main execution function for CLI usage."""
    parser = argparse.ArgumentParser(description="Index CrownCorridor property data into Typesense.")
    parser.add_argument("--host", default=os.getenv("TYPESENSE_HOST", "localhost"), help="Typesense host")
    parser.add_argument("--port", default=os.getenv("TYPESENSE_PORT", "8108"), help="Typesense port")
    parser.add_argument("--protocol", default=os.getenv("TYPESENSE_PROTOCOL", "http"), help="Typesense protocol")
    parser.add_argument("--api-key", default=os.getenv("TYPESENSE_API_KEY", "xyz123-crowncorridor-key"), help="API key")
    parser.add_argument("--dry-run", action="store_true", help="Simulate transformation without API calls")

    args = parser.parse_args()

    docs = load_all_property_records()
    index_documents(
        documents=docs,
        host=args.host,
        port=args.port,
        protocol=args.protocol,
        api_key=args.api_key,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
