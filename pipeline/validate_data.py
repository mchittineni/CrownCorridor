"""
Crown Corridor — Data Integrity Validator
==========================================
Validates the AP & Telangana geographic reference datasets in data/.
Runs on every PR via .github/workflows/ci.yml.

Exit codes:
  0  — all checks passed
  1  — one or more validation failures
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent
DATA_ROOT = ROOT / "data"

STATES = ["andhra_pradesh", "telangana"]

REQUIRED_FILES = [
    "regions.json",
    "villages.json",
    "coords.json",
    "districts.geojson",
    "mandals.geojson",
    "meta.json",
]

ERRORS = []


def err(msg: str) -> None:
    ERRORS.append(msg)
    print(f"  ✗  {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    print(f"  ✓  {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# File presence
# ─────────────────────────────────────────────────────────────────────────────


def check_files_present() -> None:
    print("\n[1] Required file presence")
    for state in STATES:
        state_dir = DATA_ROOT / state
        for fname in REQUIRED_FILES:
            fpath = state_dir / fname
            if fpath.exists():
                ok(f"{state}/{fname}")
            else:
                err(f"Missing: data/{state}/{fname}")


# ─────────────────────────────────────────────────────────────────────────────
# regions.json structure
# ─────────────────────────────────────────────────────────────────────────────


def check_regions() -> None:
    print("\n[2] regions.json structure & counts")
    for state in STATES:
        fpath = DATA_ROOT / state / "regions.json"
        if not fpath.exists():
            err(f"Cannot validate {state}/regions.json — file missing")
            continue
        try:
            data = json.loads(fpath.read_text())
        except json.JSONDecodeError as exc:
            err(f"{state}/regions.json — invalid JSON: {exc}")
            continue

        districts = data.get("districts", [])
        mandals = data.get("mandals", [])

        if not districts:
            err(f"{state}/regions.json — 'districts' array is empty")
        else:
            ok(f"{state}/regions.json — {len(districts)} districts, {len(mandals)} mandals")

        # Every mandal should reference a valid district id
        district_ids = {d.get("i") for d in districts}
        orphaned = [m for m in mandals if m.get("d") not in district_ids]
        if orphaned:
            err(f"{state}/regions.json — {len(orphaned)} mandals reference unknown district ids")
        else:
            ok(f"{state}/regions.json — all mandal district references valid")


# ─────────────────────────────────────────────────────────────────────────────
# villages.json
# ─────────────────────────────────────────────────────────────────────────────


def check_villages() -> None:
    print("\n[3] villages.json well-formedness")
    # villages.json uses a columnar format: {"columns": [...], "rows": [[...], ...]}
    for state in STATES:
        fpath = DATA_ROOT / state / "villages.json"
        if not fpath.exists():
            err(f"Cannot validate {state}/villages.json — file missing")
            continue
        try:
            data = json.loads(fpath.read_text())
        except json.JSONDecodeError as exc:
            err(f"{state}/villages.json — invalid JSON: {exc}")
            continue

        # Accept both a plain list (legacy) and the columnar {columns, rows} format
        if isinstance(data, list):
            rows = data
            min_fields = 4
        elif isinstance(data, dict) and "columns" in data and "rows" in data:
            rows = data["rows"]
            min_fields = len(data["columns"])  # every row must have same width as header
        else:
            err(
                f"{state}/villages.json — unrecognised structure (expected list or {{columns,rows}} dict)"
            )
            continue

        if not rows:
            err(f"{state}/villages.json — rows array is empty")
            continue

        malformed = [v for v in rows if not isinstance(v, list) or len(v) < min_fields]
        if malformed:
            err(
                f"{state}/villages.json — {len(malformed)} malformed village records (expected ≥{min_fields} fields)"
            )
        else:
            ok(f"{state}/villages.json — {len(rows)} villages, all records well-formed")


# ─────────────────────────────────────────────────────────────────────────────
# coords.json
# ─────────────────────────────────────────────────────────────────────────────


def check_coords() -> None:
    print("\n[4] coords.json coordinate ranges")
    # AP bounding box: lat 12.5–20, lng 76.7–84.8
    # TS bounding box: lat 15.8–19.9, lng 77.3–81.3
    BOUNDS = {
        "andhra_pradesh": {"lat": (12.5, 20.5), "lng": (76.7, 84.8)},
        "telangana": {"lat": (15.8, 19.9), "lng": (77.3, 81.3)},
    }
    for state in STATES:
        fpath = DATA_ROOT / state / "coords.json"
        if not fpath.exists():
            err(f"Cannot validate {state}/coords.json — file missing")
            continue
        try:
            data = json.loads(fpath.read_text())
        except json.JSONDecodeError as exc:
            err(f"{state}/coords.json — invalid JSON: {exc}")
            continue

        bounds = BOUNDS[state]
        out_of_range = []
        for code, coord in data.items():
            if not isinstance(coord, list) or len(coord) < 2:
                out_of_range.append(code)
                continue
            lat, lng = coord[0], coord[1]
            if not (bounds["lat"][0] <= lat <= bounds["lat"][1]):
                out_of_range.append(code)
            elif not (bounds["lng"][0] <= lng <= bounds["lng"][1]):
                out_of_range.append(code)

        if out_of_range:
            err(
                f"{state}/coords.json — {len(out_of_range)} coordinates out of expected bounding box"
            )
        else:
            ok(f"{state}/coords.json — {len(data)} coordinates all within bounding box")


# ─────────────────────────────────────────────────────────────────────────────
# meta.json
# ─────────────────────────────────────────────────────────────────────────────


def check_meta() -> None:
    print("\n[5] meta.json fields")
    REQUIRED_KEYS = {"counts", "source_date"}
    for state in STATES:
        fpath = DATA_ROOT / state / "meta.json"
        if not fpath.exists():
            err(f"Cannot validate {state}/meta.json — file missing")
            continue
        try:
            data = json.loads(fpath.read_text())
        except json.JSONDecodeError as exc:
            err(f"{state}/meta.json — invalid JSON: {exc}")
            continue

        missing = REQUIRED_KEYS - set(data.keys())
        if missing:
            err(f"{state}/meta.json — missing required keys: {missing}")
        else:
            counts = data.get("counts", {})
            ok(
                f"{state}/meta.json — {counts.get('villages', '?')} villages, source_date={data.get('source_date')}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# GeoJSON districts
# ─────────────────────────────────────────────────────────────────────────────


def check_geojson() -> None:
    print("\n[6] districts.geojson structure")
    for state in STATES:
        fpath = DATA_ROOT / state / "districts.geojson"
        if not fpath.exists():
            err(f"Cannot validate {state}/districts.geojson — file missing")
            continue
        try:
            data = json.loads(fpath.read_text())
        except json.JSONDecodeError as exc:
            err(f"{state}/districts.geojson — invalid JSON: {exc}")
            continue

        if data.get("type") != "FeatureCollection":
            err(f"{state}/districts.geojson — top-level type is not 'FeatureCollection'")
        else:
            features = data.get("features", [])
            ok(f"{state}/districts.geojson — valid FeatureCollection with {len(features)} features")


# ─────────────────────────────────────────────────────────────────────────────
# property_history.json validator
# ─────────────────────────────────────────────────────────────────────────────


def check_property_history() -> None:
    print("\n[7] property_history.json integrity & nearby services")
    target_files = [
        DATA_ROOT / "andhra_pradesh" / "property_history.json",
        DATA_ROOT / "telangana" / "property_history.json",
        DATA_ROOT / "property_history.json",
    ]

    found_any = False
    for fpath in target_files:
        if not fpath.exists():
            continue

        found_any = True
        rel_path = fpath.relative_to(DATA_ROOT)

        try:
            data = json.loads(fpath.read_text())
        except json.JSONDecodeError as exc:
            err(f"{rel_path} — invalid JSON: {exc}")
            continue

        properties = data.get("properties", [])
        if not properties or not isinstance(properties, list):
            err(f"{rel_path} — 'properties' array is missing or empty")
            continue

        BOUNDS = {
            "andhra_pradesh": {"lat": (12.5, 20.5), "lng": (76.7, 84.8)},
            "telangana": {"lat": (15.8, 19.9), "lng": (77.3, 81.3)},
        }
        REQUIRED_PROP_KEYS = {
            "property_id",
            "name",
            "type",
            "construction_year",
            "address",
            "state",
            "total_sqft",
            "lat",
            "lng",
            "sale_history",
            "price_summary",
            "nearby_services",
        }
        REQUIRED_SERVICE_CATS = {"schools", "hospitals", "metro_railways"}

        for idx, prop in enumerate(properties):
            pid = prop.get("property_id", f"INDEX-{idx}")
            missing = REQUIRED_PROP_KEYS - set(prop.keys())
            if missing:
                err(f"{rel_path} property {pid} missing keys: {missing}")
                continue

            state = prop.get("state")
            if state not in BOUNDS:
                err(f"{rel_path} property {pid} has invalid state: '{state}'")
                continue

            # Check bounds
            lat, lng = prop.get("lat"), prop.get("lng")
            b = BOUNDS[state]
            if not (b["lat"][0] <= lat <= b["lat"][1] and b["lng"][0] <= lng <= b["lng"][1]):
                err(
                    f"{rel_path} property {pid} coordinates ({lat}, {lng}) out of bounds for {state}"
                )

            # Check sale history chronological order & valid prices & no PII
            sales = prop.get("sale_history", [])
            if not sales or not isinstance(sales, list):
                err(f"{rel_path} property {pid} sale_history must be a non-empty list")
            else:
                prev_year = 0
                for sale in sales:
                    year = sale.get("year", 0)
                    price = sale.get("sale_price_inr", 0)
                    seller = sale.get("seller_type", "")
                    buyer = sale.get("buyer_type", "")

                    if year < prev_year:
                        err(
                            f"{rel_path} property {pid} sale_history out of chronological order: {year} < {prev_year}"
                        )
                    if price <= 0:
                        err(
                            f"{rel_path} property {pid} sale history year {year} has non-positive price: {price}"
                        )

                    # PII protection check
                    import re

                    if re.search(r"\([A-Z]\.|\b(Mr|Mrs|Dr|Cmdr)\b", seller + buyer, re.I):
                        err(
                            f"{rel_path} property {pid} sale history contains potential customer PII in buyer/seller fields: '{seller}' / '{buyer}'"
                        )

                    prev_year = year

            # Check nearby services categories
            services = prop.get("nearby_services", [])
            found_cats = {s.get("category") for s in services if isinstance(s, dict)}
            missing_cats = REQUIRED_SERVICE_CATS - found_cats
            if missing_cats:
                err(
                    f"{rel_path} property {pid} nearby_services missing required categories: {missing_cats}"
                )

        ok(f"{rel_path} — {len(properties)} properties with complete sale histories and POIs")

    if not found_any:
        err("No property_history.json files found across state directories")


# ─────────────────────────────────────────────────────────────────────────────
# market_trends.json validator
# ─────────────────────────────────────────────────────────────────────────────


def check_market_trends() -> None:
    print("\n[8] market_trends.json integrity")
    for state in STATES:
        fpath = DATA_ROOT / state / "market_trends.json"
        if not fpath.exists():
            err(f"Cannot validate {state}/market_trends.json — file missing")
            continue

        try:
            data = json.loads(fpath.read_text())
        except json.JSONDecodeError as exc:
            err(f"{state}/market_trends.json — invalid JSON: {exc}")
            continue

        hubs = data.get("employment_hubs", [])
        if not hubs or not isinstance(hubs, list):
            err(f"{state}/market_trends.json — 'employment_hubs' array missing or empty")

        time_series = data.get("time_series", {})
        quarters = time_series.get("quarters", [])
        localities = time_series.get("localities", [])

        if not quarters or not localities:
            err(f"{state}/market_trends.json — 'time_series' missing quarters or localities")
        else:
            ok(
                f"{state}/market_trends.json — {len(hubs)} employment hubs, {len(localities)} localities across {len(quarters)} quarters"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Crown Corridor — Data Integrity Validator")
    print("=" * 60)

    check_files_present()
    check_regions()
    check_villages()
    check_coords()
    check_meta()
    check_geojson()
    check_property_history()
    check_market_trends()

    print("\n" + "=" * 60)
    if ERRORS:
        print(f"FAILED — {len(ERRORS)} error(s) detected:")
        for e in ERRORS:
            print(f"  • {e}")
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED ✓")
        sys.exit(0)
