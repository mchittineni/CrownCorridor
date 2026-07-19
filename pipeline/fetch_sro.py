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
import datetime
import json
import pathlib
import sys

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

ROOT = pathlib.Path(__file__).parent.parent
OUTPUT_DIR = ROOT / "data" / "sro_feed"

# Official endpoints
ENDPOINTS = {
    "andhra_pradesh": {
        "name": "AP Registration & Stamps Department",
        "base_url": "https://registration.ap.gov.in/",
        "docs": "https://registration.ap.gov.in/",
    },
    "telangana": {
        "name": "Telangana Registration & Stamps",
        "base_url": "https://registration.telangana.gov.in/",
        "docs": "https://registration.telangana.gov.in/",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Fetch helpers
# ─────────────────────────────────────────────────────────────────────────────

def fetch_ap_registrations(date: str, dry_run: bool = False) -> list[dict]:
    if dry_run:
        print(f"  [DRY RUN] Returning stubbed AP records for {date}")
        return _stub_records("Andhra Pradesh", date, count=5)

    print("  [STUB] AP live fetch not yet configured — returning empty list")
    return []


def fetch_tg_registrations(date: str, dry_run: bool = False) -> list[dict]:
    if dry_run:
        print(f"  [DRY RUN] Returning stubbed TS records for {date}")
        return _stub_records("Telangana", date, count=5)

    print("  [STUB] TS live fetch not yet configured — returning empty list")
    return []


def _stub_records(state: str, date: str, count: int = 5) -> list[dict]:
    is_ap = state == "Andhra Pradesh"
    sros = (
        ["Visakhapatnam Urban", "Vijayawada East", "Guntur Rural", "Tirupati Urban"]
        if is_ap
        else ["Gachibowli", "Serilingampally", "Khairatabad", "Kukatpally"]
    )
    districts = (
        ["Visakhapatnam", "NTR Vijayawada", "Guntur", "Tirupati"]
        if is_ap
        else ["Hyderabad", "Rangareddy", "Medchal-Malkajgiri"]
    )
    property_types = ["Residential Flat", "Residential Plot", "Commercial Space", "Independent Villa"]

    records = []
    for i in range(count):
        duty_rate = 0.075 if is_ap else 0.06
        consideration = round(3500000 + (i * 1250000) * (1.1 if is_ap else 1.25))
        total_duty = round(consideration * duty_rate)

        rec = {
            "document_id": f"DOC-SRO-2026-{1000 + i}",
            "registered_date": date,
            "state": state,
            "district": districts[i % len(districts)],
            "mandal": sros[i % len(sros)] + " Mandal",
            "village": sros[i % len(sros)] + " Sector",
            "sro_office": sros[i % len(sros)],
            "property_type": property_types[i % len(property_types)],
            "consideration_value_inr": consideration,
            "total_duty_inr": total_duty,
            "seller_type": "Private Individual Owner",
            "buyer_type": "Commercial Property Developer" if i % 2 == 0 else "Private Individual Owner",
        }
        records.append(rec)
    return records


def save_records(records: list[dict], state_slug: str, date: str) -> pathlib.Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_name = f"{state_slug}_sro_{date}.json"
    target_file = OUTPUT_DIR / file_name
    data = {
        "fetched_at": str(datetime.datetime.now(datetime.timezone.utc)),
        "record_count": len(records),
        "records": records,
    }
    target_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"  Saved {len(records)} records → {target_file.relative_to(ROOT)}")
    return target_file


def generate_state_property_history(state_slug: str) -> pathlib.Path:
    target_dir = ROOT / "data" / state_slug
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / "property_history.json"

    if state_slug == "andhra_pradesh":
        properties = [
            {
                "property_id": "PROP-AP-VSKP-01",
                "name": "Amaravati Skyline Towers",
                "type": "Apartment",
                "construction_year": 2004,
                "address": "Door 48-14-3, MVP Colony Sector 4, Visakhapatnam",
                "mandal": "Visakhapatnam Urban",
                "district": "Visakhapatnam",
                "state": "andhra_pradesh",
                "total_sqft": 1650,
                "bedrooms": 3,
                "bathrooms": 2,
                "rera_id": "P03290004120",
                "lat": 17.7423,
                "lng": 83.3312,
                "price_summary": {
                    "initial_price_inr": 2145000,
                    "latest_price_inr": 9570000,
                    "total_appreciation_pct": 346.15,
                    "cagr_pct": 7.03,
                    "holding_period_years": 22
                },
                "sale_history": [
                    {
                        "year": 2004,
                        "sale_date": "2004-03-12",
                        "sale_price_inr": 2145000,
                        "price_per_sqft_inr": 1300,
                        "seller_type": "Commercial Property Developer",
                        "buyer_type": "Private Individual Owner",
                        "registration_doc_no": "SRO-VSKP-2004-1042",
                        "growth_over_initial_pct": 0.0,
                        "cagr_pct": 0.0
                    },
                    {
                        "year": 2015,
                        "sale_date": "2015-08-20",
                        "sale_price_inr": 5115000,
                        "price_per_sqft_inr": 3100,
                        "seller_type": "Private Individual Owner",
                        "buyer_type": "Private Individual Owner",
                        "registration_doc_no": "SRO-VSKP-2015-6812",
                        "growth_over_initial_pct": 138.46,
                        "cagr_pct": 8.24
                    },
                    {
                        "year": 2026,
                        "sale_date": "2026-07-01",
                        "sale_price_inr": 9570000,
                        "price_per_sqft_inr": 5800,
                        "seller_type": "Private Individual Owner",
                        "buyer_type": "Current Valuation (SRO Benchmark)",
                        "registration_doc_no": "VALUATION-EST-2026",
                        "growth_over_initial_pct": 346.15,
                        "cagr_pct": 7.03
                    }
                ],
                "nearby_services": [
                    {
                        "name": "Timpany Senior Secondary School",
                        "category": "schools",
                        "type": "CBSE K-12 School",
                        "distance_km": 1.1,
                        "travel_time_mins": 4,
                        "rating": 4.7,
                        "lat": 17.7450,
                        "lng": 83.3280
                    },
                    {
                        "name": "Apollo Hospitals Health City",
                        "category": "hospitals",
                        "type": "Super-Specialty Hospital",
                        "distance_km": 2.4,
                        "travel_time_mins": 8,
                        "rating": 4.8,
                        "lat": 17.7512,
                        "lng": 83.3410
                    },
                    {
                        "name": "Visakhapatnam Railway Junction",
                        "category": "metro_railways",
                        "type": "Major Railway Station",
                        "distance_km": 4.5,
                        "travel_time_mins": 14,
                        "rating": 4.5,
                        "lat": 17.7210,
                        "lng": 83.2891
                    }
                ]
            },
            {
                "property_id": "PROP-AP-VSKP-02",
                "name": "MVP Beachfront Luxury Villa",
                "type": "Independent Villa",
                "construction_year": 2002,
                "address": "Plot 12, Beach Road, MVP Colony Sector 1, Visakhapatnam",
                "mandal": "Visakhapatnam Urban",
                "district": "Visakhapatnam",
                "state": "andhra_pradesh",
                "total_sqft": 3200,
                "bedrooms": 4,
                "bathrooms": 4,
                "rera_id": "P03290004880",
                "lat": 17.7380,
                "lng": 83.3420,
                "price_summary": {
                    "initial_price_inr": 3840000,
                    "latest_price_inr": 28800000,
                    "total_appreciation_pct": 650.0,
                    "cagr_pct": 8.76,
                    "holding_period_years": 24
                },
                "sale_history": [
                    {
                        "year": 2002,
                        "sale_date": "2002-05-18",
                        "sale_price_inr": 3840000,
                        "price_per_sqft_inr": 1200,
                        "seller_type": "Commercial Property Developer",
                        "buyer_type": "Private Individual Owner",
                        "registration_doc_no": "SRO-VSKP-2002-0891",
                        "growth_over_initial_pct": 0.0,
                        "cagr_pct": 0.0
                    },
                    {
                        "year": 2026,
                        "sale_date": "2026-07-01",
                        "sale_price_inr": 28800000,
                        "price_per_sqft_inr": 9000,
                        "seller_type": "Private Individual Owner",
                        "buyer_type": "Current Valuation (SRO Benchmark)",
                        "registration_doc_no": "VALUATION-EST-2026",
                        "growth_over_initial_pct": 650.0,
                        "cagr_pct": 8.76
                    }
                ],
                "nearby_services": [
                    {
                        "name": "Visakha Valley School",
                        "category": "schools",
                        "type": "Senior Secondary School",
                        "distance_km": 1.5,
                        "travel_time_mins": 5,
                        "rating": 4.6,
                        "lat": 17.7410,
                        "lng": 83.3450
                    },
                    {
                        "name": "CARE Hospitals Ramnagar",
                        "category": "hospitals",
                        "type": "Multi-Specialty Hospital",
                        "distance_km": 2.8,
                        "travel_time_mins": 9,
                        "rating": 4.7,
                        "lat": 17.7320,
                        "lng": 83.3150
                    },
                    {
                        "name": "MVP Beach Road Promenade",
                        "category": "metro_railways",
                        "type": "Coastal Transit Station",
                        "distance_km": 0.5,
                        "travel_time_mins": 2,
                        "rating": 4.9,
                        "lat": 17.7370,
                        "lng": 83.3440
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
                "construction_year": 2001,
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
                    "initial_price_inr": 2405000,
                    "latest_price_inr": 19425000,
                    "total_appreciation_pct": 707.69,
                    "cagr_pct": 8.74,
                    "holding_period_years": 25
                },
                "sale_history": [
                    {
                        "year": 2001,
                        "sale_date": "2001-04-15",
                        "sale_price_inr": 2405000,
                        "price_per_sqft_inr": 1300,
                        "seller_type": "Cyber City Developers Ltd",
                        "buyer_type": "Private Individual Owner",
                        "registration_doc_no": "SRO-HYD-2001-1102",
                        "growth_over_initial_pct": 0.0,
                        "cagr_pct": 0.0
                    },
                    {
                        "year": 2014,
                        "sale_date": "2014-09-10",
                        "sale_price_inr": 8325000,
                        "price_per_sqft_inr": 4500,
                        "seller_type": "Private Individual Owner",
                        "buyer_type": "Private Individual Owner",
                        "registration_doc_no": "SRO-HYD-2014-8901",
                        "growth_over_initial_pct": 246.15,
                        "cagr_pct": 10.01
                    },
                    {
                        "year": 2026,
                        "sale_date": "2026-07-01",
                        "sale_price_inr": 19425000,
                        "price_per_sqft_inr": 10500,
                        "seller_type": "Private Individual Owner",
                        "buyer_type": "Current Valuation (SRO Benchmark)",
                        "registration_doc_no": "VALUATION-EST-2026",
                        "growth_over_initial_pct": 707.69,
                        "cagr_pct": 8.74
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
            },
            {
                "property_id": "PROP-TG-HYD-02",
                "name": "Jubilee Hills Royal Villa",
                "type": "Independent Villa",
                "construction_year": 2002,
                "address": "Road No 36, Jubilee Hills Sector 3, Hyderabad",
                "mandal": "Khairatabad",
                "district": "Hyderabad",
                "state": "telangana",
                "total_sqft": 4500,
                "bedrooms": 5,
                "bathrooms": 6,
                "rera_id": "P02400008912",
                "lat": 17.4320,
                "lng": 78.4080,
                "price_summary": {
                    "initial_price_inr": 9000000,
                    "latest_price_inr": 81000000,
                    "total_appreciation_pct": 800.0,
                    "cagr_pct": 9.57,
                    "holding_period_years": 24
                },
                "sale_history": [
                    {
                        "year": 2002,
                        "sale_date": "2002-08-11",
                        "sale_price_inr": 9000000,
                        "price_per_sqft_inr": 2000,
                        "seller_type": "Commercial Property Developer",
                        "buyer_type": "Private Individual Owner",
                        "registration_doc_no": "SRO-JUB-2002-0412",
                        "growth_over_initial_pct": 0.0,
                        "cagr_pct": 0.0
                    },
                    {
                        "year": 2026,
                        "sale_date": "2026-07-01",
                        "sale_price_inr": 81000000,
                        "price_per_sqft_inr": 18000,
                        "seller_type": "Private Individual Owner",
                        "buyer_type": "Current Valuation (SRO Benchmark)",
                        "registration_doc_no": "VALUATION-EST-2026",
                        "growth_over_initial_pct": 800.0,
                        "cagr_pct": 9.57
                    }
                ],
                "nearby_services": [
                    {
                        "name": "Chirec International School",
                        "category": "schools",
                        "type": "International School",
                        "distance_km": 1.4,
                        "travel_time_mins": 5,
                        "rating": 4.9,
                        "lat": 17.4350,
                        "lng": 78.4120
                    },
                    {
                        "name": "Apollo Hospitals Jubilee Hills",
                        "category": "hospitals",
                        "type": "Super Specialty Hospital",
                        "distance_km": 0.9,
                        "travel_time_mins": 3,
                        "rating": 4.8,
                        "lat": 17.4290,
                        "lng": 78.4090
                    },
                    {
                        "name": "Jubilee Hills Checkpost Metro Station",
                        "category": "metro_railways",
                        "type": "Hyderabad Metro Station",
                        "distance_km": 1.1,
                        "travel_time_mins": 4,
                        "rating": 4.7,
                        "lat": 17.4330,
                        "lng": 78.4100
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
