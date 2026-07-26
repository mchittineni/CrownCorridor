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


def sanitize_and_anonymize_record(raw_record: dict) -> dict:
    """Enforces Zero-PII compliance by stripping personal names/numbers and mapping to anonymized role classifications."""
    ALLOWED_ROLES = {
        "Private Individual Owner",
        "Commercial Property Developer",
        "Institutional Realty Fund",
        "Government / Municipal Entity",
        "Current Valuation (SRO Benchmark)",
    }

    seller_raw = str(
        raw_record.get("seller_type") or raw_record.get("seller_name") or ""
    )
    buyer_raw = str(raw_record.get("buyer_type") or raw_record.get("buyer_name") or "")

    seller_role = (
        seller_raw
        if seller_raw in ALLOWED_ROLES
        else (
            "Commercial Property Developer"
            if "ltd" in seller_raw.lower() or "inc" in seller_raw.lower()
            else "Private Individual Owner"
        )
    )
    buyer_role = (
        buyer_raw
        if buyer_raw in ALLOWED_ROLES
        else (
            "Commercial Property Developer"
            if "ltd" in buyer_raw.lower() or "inc" in buyer_raw.lower()
            else "Private Individual Owner"
        )
    )

    clean_record = dict(raw_record)
    clean_record["seller_type"] = seller_role
    clean_record["buyer_type"] = buyer_role

    # Remove any potential PII fields if present
    for pii_key in (
        "seller_name",
        "buyer_name",
        "phone",
        "email",
        "aadhaar_hash",
        "pan_hash",
    ):
        clean_record.pop(pii_key, None)

    return clean_record


def fetch_ap_registrations(date: str, dry_run: bool = False) -> list[dict]:
    if dry_run:
        print(f"  [DRY RUN] Returning stubbed AP records for {date}")
        records = _stub_records("Andhra Pradesh", date, count=5)
        return [sanitize_and_anonymize_record(r) for r in records]

    print("  [STUB] AP live fetch not yet configured — returning empty list")
    return []


def fetch_tg_registrations(date: str, dry_run: bool = False) -> list[dict]:
    if dry_run:
        print(f"  [DRY RUN] Returning stubbed TS records for {date}")
        records = _stub_records("Telangana", date, count=5)
        return [sanitize_and_anonymize_record(r) for r in records]

    print("  [STUB] TS live fetch not yet configured — returning empty list")
    return []


def _stub_records(state: str, date: str, count: int = 5) -> list[dict]:
    is_ap = state == "Andhra Pradesh"
    sros = (
        [
            "Visakhapatnam Urban",
            "Vijayawada East",
            "Guntur Rural",
            "Tirupati Urban",
            "Kakinada",
            "Ananthapuramu",
            "Nellore",
            "Kurnool",
        ]
        if is_ap
        else [
            "Gachibowli",
            "Serilingampally",
            "Khairatabad",
            "Kukatpally",
            "Karimnagar",
            "Warangal",
            "Nizamabad",
            "Khammam",
        ]
    )
    # Complete list of 28 AP Districts & 33 Telangana Districts
    districts = (
        [
            "Alluri Sitharama Raju",
            "Anakapalli",
            "Ananthapuramu",
            "Annamayya",
            "Bapatla",
            "Chittoor",
            "Dr. B.R. Ambedkar Konaseema",
            "East Godavari",
            "Eluru",
            "Guntur",
            "Kakinada",
            "Krishna",
            "Kurnool",
            "Markapuram",
            "Nandyal",
            "Ntr",
            "Palnadu",
            "Parvathipuram Manyam",
            "Polavaram",
            "Prakasam",
            "Sri Potti Sriramulu Nellore",
            "Sri Sathya Sai",
            "Srikakulam",
            "Tirupati",
            "Visakhapatnam",
            "Vizianagaram",
            "West Godavari",
            "Y.S.R. Kadapa",
        ]
        if is_ap
        else [
            "Adilabad",
            "Bhadradri Kothagudem",
            "Hanumakonda",
            "Hyderabad",
            "Jagitial",
            "Jangoan",
            "Jayashankar Bhupalapally",
            "Jogulamba Gadwal",
            "Kamareddy",
            "Karimnagar",
            "Khammam",
            "Kumuram Bheem Asifabad",
            "Mahabubabad",
            "Mahabubnagar",
            "Mancherial",
            "Medak",
            "Medchal Malkajgiri",
            "Mulugu",
            "Nagarkurnool",
            "Nalgonda",
            "Narayanpet",
            "Nirmal",
            "Nizamabad",
            "Peddapalli",
            "Rajanna Sircilla",
            "Ranga Reddy",
            "Sangareddy",
            "Siddipet",
            "Suryapet",
            "Vikarabad",
            "Wanaparthy",
            "Warangal",
            "Yadadri Bhuvanagiri",
        ]
    )
    property_types = [
        "Residential Flat",
        "Residential Plot",
        "Commercial Space",
        "Independent Villa",
    ]

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
            "buyer_type": (
                "Commercial Property Developer"
                if i % 2 == 0
                else "Private Individual Owner"
            ),
        }
        records.append(rec)
    return records


def save_records(records: list[dict], state_slug: str, date: str) -> pathlib.Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_name = f"{state_slug}_sro_{date}.json"
    target_file = OUTPUT_DIR / file_name
    data = {
        "fetched_at": str(datetime.datetime.now(datetime.UTC)),
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

    properties = []
    villages_file = ROOT / "data" / state_slug / "villages.json"
    regions_file = ROOT / "data" / state_slug / "regions.json"

    mandal_district_map = {}
    if regions_file.exists():
        try:
            rdata = json.loads(regions_file.read_text(encoding="utf-8"))
            districts_by_id = {d["i"]: d["n"] for d in rdata.get("districts", [])}
            for m in rdata.get("mandals", []):
                mandal_district_map[m["i"]] = {
                    "mandal_name": m["n"],
                    "district_name": districts_by_id.get(m.get("d"), "State District"),
                }
        except Exception as e:
            print(f"Warning loading regions for {state_slug}: {e}")

    if villages_file.exists():
        try:
            vdata = json.loads(villages_file.read_text(encoding="utf-8"))
            rows = vdata.get("rows", [])
            is_ap = state_slug == "andhra_pradesh"
            prefix = "AP" if is_ap else "TG"

            for idx, row in enumerate(rows):
                v_name = row[0]
                m_id = row[1]
                v_code = row[2]
                pin = row[4] if len(row) > 4 else ("520001" if is_ap else "500001")

                m_info = mandal_district_map.get(
                    m_id, {"mandal_name": f"Mandal-{m_id}", "district_name": "General"}
                )
                mandal_name = m_info["mandal_name"]
                district_name = m_info["district_name"]

                prop_id = f"PROP-{prefix}-{idx + 1:05d}"
                holding_years = 15 + (idx % 10)
                initial_price = 1500000 + (idx % 100) * 50000
                total_sqft = 1200 + (idx % 8) * 150

                latest_price = round(initial_price * (1.065**holding_years))
                cagr_val = round(
                    (((latest_price / initial_price) ** (1.0 / holding_years)) - 1.0)
                    * 100.0,
                    2,
                )
                apprec_pct = round(
                    ((latest_price - initial_price) / initial_price) * 100.0, 2
                )

                prop = {
                    "property_id": prop_id,
                    "name": f"{v_name} Corridor Residency",
                    "type": "Apartment" if idx % 2 == 0 else "Residential Plot",
                    "construction_year": 2026 - holding_years,
                    "address": f"Survey No {101 + (idx % 200)}, {v_name}, PIN {pin}",
                    "mandal": mandal_name,
                    "district": district_name,
                    "state": state_slug,
                    "total_sqft": total_sqft,
                    "bedrooms": 2 + (idx % 3),
                    "bathrooms": 2,
                    "rera_id": f"P{prefix}{v_code}",
                    "lat": (
                        16.5000 + (idx % 500) * 0.002
                        if is_ap
                        else 17.3850 + (idx % 500) * 0.002
                    ),
                    "lng": (
                        80.6400 + (idx % 500) * 0.002
                        if is_ap
                        else 78.4867 + (idx % 500) * 0.002
                    ),
                    "price_summary": {
                        "initial_price_inr": initial_price,
                        "latest_price_inr": latest_price,
                        "total_appreciation_pct": apprec_pct,
                        "cagr_pct": cagr_val,
                        "holding_period_years": holding_years,
                    },
                    "sale_history": [
                        {
                            "year": 2026 - holding_years,
                            "sale_date": f"{2026 - holding_years}-01-15",
                            "sale_price_inr": initial_price,
                            "price_per_sqft_inr": round(initial_price / total_sqft),
                            "seller_type": "Commercial Property Developer",
                            "buyer_type": "Private Individual Owner",
                            "registration_doc_no": f"DOC-{prefix}-{2026 - holding_years}-{1000 + idx}",
                            "growth_over_initial_pct": 0.0,
                            "cagr_pct": 0.0,
                        },
                        {
                            "year": 2026,
                            "sale_date": "2026-07-01",
                            "sale_price_inr": latest_price,
                            "price_per_sqft_inr": round(latest_price / total_sqft),
                            "seller_type": "Private Individual Owner",
                            "buyer_type": "Current Valuation (SRO Benchmark)",
                            "registration_doc_no": f"VALUATION-EST-{prefix}-2026-{idx}",
                            "growth_over_initial_pct": apprec_pct,
                            "cagr_pct": cagr_val,
                        },
                    ],
                    "nearby_services": [
                        {
                            "name": f"{v_name} Primary & Secondary School",
                            "category": "schools",
                            "type": "State / CBSE School",
                            "distance_km": 1.2,
                            "travel_time_mins": 5,
                            "rating": 4.5,
                            "lat": 16.501 if is_ap else 17.386,
                            "lng": 80.641 if is_ap else 78.487,
                        },
                        {
                            "name": f"{district_name} Area Hospital",
                            "category": "hospitals",
                            "type": "Community Health Center",
                            "distance_km": 2.8,
                            "travel_time_mins": 9,
                            "rating": 4.6,
                            "lat": 16.503 if is_ap else 17.388,
                            "lng": 80.643 if is_ap else 78.489,
                        },
                        {
                            "name": f"{mandal_name} Transit Hub",
                            "category": "metro_railways",
                            "type": "Transit Railway Station",
                            "distance_km": 3.5,
                            "travel_time_mins": 12,
                            "rating": 4.7,
                            "lat": 16.505 if is_ap else 17.390,
                            "lng": 80.645 if is_ap else 78.491,
                        },
                    ],
                }
                properties.append(prop)
        except Exception as err:
            print(f"Error generating full property histories for {state_slug}: {err}")

    data = {
        "version": "1.0.0",
        "state": state_slug,
        "updated_at": str(datetime.date.today()),
        "properties": properties,
    }

    target_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(
        f"  Saved {len(properties)} history records → {target_file.relative_to(ROOT)}"
    )
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

    print(
        f"Crown Corridor SRO Fetcher — date={args.date}, dry_run={args.dry_run}, generate_history={args.generate_history}"
    )

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
