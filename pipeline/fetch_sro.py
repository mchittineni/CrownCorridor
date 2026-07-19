"""
Crown Corridor — SRO Data Fetcher Scaffold
==========================================
Scaffold for fetching real Sub-Registrar Office (SRO) registration data
from AP Registration & Stamps Dept and Telangana Registration Dept APIs.

When official API access is available, replace the stub functions below
with real HTTP requests.

Exit codes (matching the datagov-fetch outage-skip contract):
  0  — success (or dry-run)
  75 — upstream server unreachable / rate-limited (triggers CI skip)
  1  — unexpected failure
"""

import argparse
import json
import pathlib
import sys
import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

ROOT = pathlib.Path(__file__).parent.parent
OUTPUT_DIR = ROOT / "data" / "sro_feed"

# Official endpoints (to be populated when API access is granted)
ENDPOINTS = {
    "andhra_pradesh": {
        "name": "AP Registration & Stamps Department",
        "base_url": "https://registration.ap.gov.in/",   # placeholder
        "docs": "https://registration.ap.gov.in/",
    },
    "telangana": {
        "name": "Telangana Registration & Stamps",
        "base_url": "https://registration.telangana.gov.in/",  # placeholder
        "docs": "https://registration.telangana.gov.in/",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Fetch helpers
# ─────────────────────────────────────────────────────────────────────────────

def fetch_ap_registrations(date: str, dry_run: bool = False) -> list[dict]:
    """
    Fetch real AP SRO registration records for a given date.

    Args:
        date:    Date string in YYYY-MM-DD format.
        dry_run: If True, return stubbed data without making HTTP calls.

    Returns:
        List of registration record dicts.

    Raises:
        SystemExit(75): When the upstream server is unreachable.
    """
    if dry_run:
        print(f"  [DRY RUN] Returning stubbed AP records for {date}")
        return _stub_records("Andhra Pradesh", date, count=5)

    # TODO: Replace with real HTTP GET once API access is configured.
    # try:
    #     import requests
    #     resp = requests.get(
    #         ENDPOINTS["andhra_pradesh"]["base_url"] + "/api/registrations",
    #         params={"date": date},
    #         timeout=30,
    #     )
    #     resp.raise_for_status()
    #     return resp.json()["records"]
    # except requests.exceptions.ConnectionError:
    #     print("  UPSTREAM UNREACHABLE — AP Registration portal is down", file=sys.stderr)
    #     sys.exit(75)  # exit-75: triggers CI skip contract

    print("  [STUB] AP live fetch not yet configured — returning empty list")
    return []


def fetch_tg_registrations(date: str, dry_run: bool = False) -> list[dict]:
    """
    Fetch real Telangana SRO registration records for a given date.

    Args:
        date:    Date string in YYYY-MM-DD format.
        dry_run: If True, return stubbed data without making HTTP calls.

    Returns:
        List of registration record dicts.

    Raises:
        SystemExit(75): When the upstream server is unreachable.
    """
    if dry_run:
        print(f"  [DRY RUN] Returning stubbed TS records for {date}")
        return _stub_records("Telangana", date, count=5)

    # TODO: Replace with real HTTP GET once API access is configured.
    print("  [STUB] TS live fetch not yet configured — returning empty list")
    return []


# ─────────────────────────────────────────────────────────────────────────────
# Stub data (mirrors the structure that real SRO APIs will return)
# ─────────────────────────────────────────────────────────────────────────────

def _stub_records(state: str, date: str, count: int = 3) -> list[dict]:
    """Generate structurally-correct stub registration records."""
    import random

    districts = {
        "Andhra Pradesh": ["Visakhapatnam", "Ntr", "Guntur", "Tirupati", "Krishna"],
        "Telangana": ["Hyderabad", "Ranga Reddy", "Medchal Malkajgiri", "Sangareddy"],
    }[state]

    prop_types = ["Residential Plot", "Residential Flat", "Agricultural Land",
                  "Commercial Space", "Independent Villa"]

    colonies_ap = ["MVP Colony", "Seethammadhara Layout", "Amaravati Heights", "Vidhya Nagar Colony", "Labbipet Enclave", "Kanuru Greenfields", "Balaji Nagar Layout", "Bhavani Nagar Society"]
    colonies_tg = ["Rainbow Vistas Colony", "Kavuri Hills Colony", "Lanco Hills Towers", "My Home Jewel Complex", "Gachibowli Financial Enclave", "Pragathi Nagar Layout", "Jubilee Hills Sector-3", "Srinagar Colony"]
    colonies = colonies_ap if state == "Andhra Pradesh" else colonies_tg

    records = []
    for i in range(count):
        consideration = random.randint(500_000, 50_000_000)
        tax_rate = 0.075 if state == "Andhra Pradesh" else 0.06
        ptype = random.choice(prop_types)
        colony = random.choice(colonies)
        
        if ptype == "Residential Flat":
            block_unit = f"Block {random.choice(['A', 'B', 'C', 'D'])}, Flat {random.randint(100, 499)}"
        elif ptype == "Commercial Space":
            block_unit = f"Tower {random.randint(1, 4)}, Suite {random.randint(100, 999)}"
        elif ptype == "Residential Plot":
            block_unit = f"Plot No {random.randint(1, 150)}, Sector {random.randint(1, 4)}"
        elif ptype == "Independent Villa":
            block_unit = f"Villa {random.randint(1, 80)}, Phase {random.randint(1, 3)}"
        else:
            block_unit = f"Survey Part-{random.choice(['A', 'B', 'C'])}"

        records.append({
            "document_id": f"DOC-{date.replace('-', '')}-{random.randint(100000, 999999)}",
            "registered_date": date,
            "state": state,
            "district": random.choice(districts),
            "property_type": ptype,
            "colony": colony,
            "block_unit": block_unit,
            "consideration_value_inr": consideration,
            "total_duty_inr": int(consideration * tax_rate),
            "source": "stub",
        })
    return records


# ─────────────────────────────────────────────────────────────────────────────
# Output
# ─────────────────────────────────────────────────────────────────────────────

def save_records(records: list[dict], state: str, date: str) -> pathlib.Path:
    """Persist fetched records as a dated JSON file under data/sro_feed/."""
    out_dir = OUTPUT_DIR / state
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{date}.json"
    out_file.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"  Saved {len(records)} records → {out_file.relative_to(ROOT)}")
    return out_file


def generate_state_property_history(state_slug: str) -> pathlib.Path:
    """
    Generate/update state-modular property sale history dataset under data/{state_slug}/property_history.json.
    Synthesizes multi-year transaction timeline, CAGR %, and nearby POIs for properties in the state.
    """
    state_dir = ROOT / "data" / state_slug
    state_dir.mkdir(parents=True, exist_ok=True)
    target_file = state_dir / "property_history.json"

    # If dataset already exists, read and validate it
    if target_file.exists():
        try:
            existing_data = json.loads(target_file.read_text())
            print(f"  ✓ {state_slug}/property_history.json already exists with {len(existing_data.get('properties', []))} properties")
            return target_file
        except Exception:
            pass

    # Stub data generation for state if missing
    properties = []
    if state_slug == "andhra_pradesh":
        properties = [
            {
                "property_id": "PROP-AP-VIZ-01",
                "name": "Sea Breeze Towers",
                "type": "Apartment",
                "construction_year": 2015,
                "address": "Beach Road, Pandurangapuram, Visakhapatnam",
                "mandal": "Visakhapatnam Urban",
                "district": "Visakhapatnam",
                "state": "andhra_pradesh",
                "total_sqft": 2100,
                "bedrooms": 3,
                "bathrooms": 3,
                "rera_id": "P03200000411",
                "lat": 17.7123,
                "lng": 83.3214,
                "price_summary": {
                    "initial_price_inr": 7350000,
                    "latest_price_inr": 21000000,
                    "total_appreciation_pct": 185.71,
                    "cagr_pct": 10.02,
                    "holding_period_years": 11
                },
                "sale_history": [
                    {
                        "year": 2015,
                        "sale_date": "2015-02-14",
                        "sale_price_inr": 7350000,
                        "price_per_sqft_inr": 3500,
                        "seller_type": "Coastal Apex Infra Ltd",
                        "buyer_type": "Private Individual Owner",
                        "registration_doc_no": "SRO-VIZ-2015-3301",
                        "growth_over_initial_pct": 0.0,
                        "cagr_pct": 0.0
                    },
                    {
                        "year": 2026,
                        "sale_date": "2026-07-01",
                        "sale_price_inr": 21000000,
                        "price_per_sqft_inr": 10000,
                        "seller_type": "Private Individual Owner",
                        "buyer_type": "Current Valuation (Coastal Prime Corridor)",
                        "registration_doc_no": "VALUATION-EST-2026",
                        "growth_over_initial_pct": 185.71,
                        "cagr_pct": 10.02
                    }
                ],
                "nearby_services": [
                    {
                        "name": "Timpany Senior Secondary School",
                        "category": "schools",
                        "type": "ICSE & CBSE Co-Ed School",
                        "distance_km": 1.8,
                        "travel_time_mins": 5,
                        "rating": 4.6,
                        "lat": 17.7198,
                        "lng": 83.3150
                    },
                    {
                        "name": "KIMS ICON Hospital",
                        "category": "hospitals",
                        "type": "Multi-Specialty Super Hospital",
                        "distance_km": 1.5,
                        "travel_time_mins": 5,
                        "rating": 4.7,
                        "lat": 17.7082,
                        "lng": 83.3105
                    },
                    {
                        "name": "Visakhapatnam Junction Station",
                        "category": "metro_railways",
                        "type": "Waltair Railway Division HQ",
                        "distance_km": 4.2,
                        "travel_time_mins": 12,
                        "rating": 4.5,
                        "lat": 17.7210,
                        "lng": 83.2891
                    }
                ]
            }
        ]
    else:
        properties = [
            {
                "property_id": "PROP-TG-HYD-01",
                "name": "Cyber Heights Residency",
                "type": "Apartment",
                "construction_year": 2012,
                "address": "Plot 42-45, Hitec City Main Road, Gachibowli",
                "mandal": "Serilingampally",
                "district": "Rangareddy",
                "state": "telangana",
                "total_sqft": 1850,
                "bedrooms": 3,
                "bathrooms": 3,
                "rera_id": "P02400001209",
                "lat": 17.4401,
                "lng": 78.3489,
                "price_summary": {
                    "initial_price_inr": 4255000,
                    "latest_price_inr": 19425000,
                    "total_appreciation_pct": 356.52,
                    "cagr_pct": 11.42,
                    "holding_period_years": 14
                },
                "sale_history": [
                    {
                        "year": 2012,
                        "sale_date": "2012-04-15",
                        "sale_price_inr": 4255000,
                        "price_per_sqft_inr": 2300,
                        "seller_type": "Cyber City Developers Ltd",
                        "buyer_type": "Private Individual Owner",
                        "registration_doc_no": "SRO-HYD-2012-4412",
                        "growth_over_initial_pct": 0.0,
                        "cagr_pct": 0.0
                    },
                    {
                        "year": 2026,
                        "sale_date": "2026-07-01",
                        "sale_price_inr": 19425000,
                        "price_per_sqft_inr": 10500,
                        "seller_type": "Private Individual Owner",
                        "buyer_type": "Current Valuation (SRO Benchmark)",
                        "registration_doc_no": "VALUATION-EST-2026",
                        "growth_over_initial_pct": 356.52,
                        "cagr_pct": 11.42
                    }
                ],
                "nearby_services": [
                    {
                        "name": "Oakridge International School",
                        "category": "schools",
                        "type": "K-12 IB World School",
                        "distance_km": 0.8,
                        "travel_time_mins": 3,
                        "rating": 4.8,
                        "lat": 17.4435,
                        "lng": 78.3521
                    },
                    {
                        "name": "Continental Hospitals",
                        "category": "hospitals",
                        "type": "Multi-Specialty Super Tertiary Hospital",
                        "distance_km": 1.2,
                        "travel_time_mins": 4,
                        "rating": 4.6,
                        "lat": 17.4365,
                        "lng": 78.3412
                    },
                    {
                        "name": "Raidurg Metro Station",
                        "category": "metro_railways",
                        "type": "Hyderabad Metro Blue Line Terminal",
                        "distance_km": 1.9,
                        "travel_time_mins": 6,
                        "rating": 4.9,
                        "lat": 17.4412,
                        "lng": 78.3641
                    }
                ]
            }
        ]

    data = {
        "version": "1.0.0",
        "state": state_slug,
        "updated_at": str(datetime.date.today()),
        "properties": properties
    }

    target_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"  Saved {len(properties)} history records → {target_file.relative_to(ROOT)}")
    return target_file


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Crown Corridor SRO data fetcher")
    parser.add_argument(
        "--date",
        default=str(datetime.date.today()),
        help="Date to fetch in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Return stub data without making real HTTP calls",
    )
    parser.add_argument(
        "--generate-history",
        action="store_true",
        help="Generate state-modular property sale history datasets under data/{state}/property_history.json",
    )
    parser.add_argument(
        "--state",
        choices=["andhra_pradesh", "telangana", "all"],
        default="all",
        help="State to fetch for (default: all)",
    )
    args = parser.parse_args()

    print(f"Crown Corridor SRO Fetcher — date={args.date}, dry_run={args.dry_run}, generate_history={args.generate_history}")

    if args.generate_history:
        if args.state in ("andhra_pradesh", "all"):
            generate_state_property_history("andhra_pradesh")
        if args.state in ("telangana", "all"):
            generate_state_property_history("telangana")

    if args.state in ("andhra_pradesh", "all"):
        print("\nFetching Andhra Pradesh SRO records…")
        ap_records = fetch_ap_registrations(args.date, dry_run=args.dry_run)
        if ap_records:
            save_records(ap_records, "andhra_pradesh", args.date)

    if args.state in ("telangana", "all"):
        print("\nFetching Telangana SRO records…")
        tg_records = fetch_tg_registrations(args.date, dry_run=args.dry_run)
        if tg_records:
            save_records(tg_records, "telangana", args.date)

    print("\nDone.")


if __name__ == "__main__":
    main()

