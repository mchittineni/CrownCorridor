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

    records = []
    for i in range(count):
        consideration = random.randint(500_000, 50_000_000)
        tax_rate = 0.075 if state == "Andhra Pradesh" else 0.06
        records.append({
            "document_id": f"DOC-{date.replace('-', '')}-{random.randint(100000, 999999)}",
            "registered_date": date,
            "state": state,
            "district": random.choice(districts),
            "property_type": random.choice(prop_types),
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
        "--state",
        choices=["andhra_pradesh", "telangana", "all"],
        default="all",
        help="State to fetch for (default: all)",
    )
    args = parser.parse_args()

    print(f"Crown Corridor SRO Fetcher — date={args.date}, dry_run={args.dry_run}")

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
