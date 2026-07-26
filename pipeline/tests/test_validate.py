"""
Tests for pipeline/validate_data.py

These tests run on every PR via .github/workflows/ci.yml.
They import the validator module directly and assert each check passes
against the real data/ directory already committed to the repo.
"""

import importlib.util
import pathlib
import sys

import pytest

# Load validate_data as a module from its path
ROOT = pathlib.Path(__file__).parent.parent.parent
VALIDATOR_PATH = ROOT / "pipeline" / "validate_data.py"

spec = importlib.util.spec_from_file_location("validate_data", VALIDATOR_PATH)
validate_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_data)

DATA_ROOT = ROOT / "data"
STATES = ["andhra_pradesh", "telangana"]


class TestFilesPresent:
    def test_all_required_files_exist(self):
        missing = []
        for state in STATES:
            for fname in validate_data.REQUIRED_FILES:
                fpath = DATA_ROOT / state / fname
                if not fpath.exists():
                    missing.append(f"data/{state}/{fname}")
        assert missing == [], f"Missing files: {missing}"


class TestRegionsJson:
    @pytest.mark.parametrize("state", STATES)
    def test_districts_not_empty(self, state):
        import json

        data = json.loads((DATA_ROOT / state / "regions.json").read_text())
        assert len(data.get("districts", [])) > 0, f"{state}: districts array is empty"

    @pytest.mark.parametrize("state", STATES)
    def test_mandal_district_references_valid(self, state):
        import json

        data = json.loads((DATA_ROOT / state / "regions.json").read_text())
        district_ids = {d["i"] for d in data.get("districts", [])}
        orphaned = [
            m for m in data.get("mandals", []) if m.get("d") not in district_ids
        ]
        assert (
            orphaned == []
        ), f"{state}: {len(orphaned)} mandals reference unknown district ids"


class TestVillagesJson:
    @staticmethod
    def _load_rows(state: str) -> list:
        import json

        data = json.loads((DATA_ROOT / state / "villages.json").read_text())
        if isinstance(data, list):
            return data
        return data["rows"]  # columnar {columns, rows} format

    @pytest.mark.parametrize("state", STATES)
    def test_is_list_or_columnar(self, state):
        import json

        data = json.loads((DATA_ROOT / state / "villages.json").read_text())
        assert isinstance(
            data, (list, dict)
        ), f"{state}/villages.json is not a list or dict"
        if isinstance(data, dict):
            assert (
                "columns" in data and "rows" in data
            ), f"{state}/villages.json dict missing 'columns' or 'rows' keys"

    @pytest.mark.parametrize("state", STATES)
    def test_records_have_minimum_fields(self, state):
        import json

        data = json.loads((DATA_ROOT / state / "villages.json").read_text())
        if isinstance(data, dict):
            rows = data["rows"]
            min_fields = len(data["columns"])
        else:
            rows = data
            min_fields = 4
        malformed = [v for v in rows if not isinstance(v, list) or len(v) < min_fields]
        assert malformed == [], f"{state}: {len(malformed)} malformed village records"

    @pytest.mark.parametrize("state", STATES)
    def test_villages_not_empty(self, state):
        rows = self._load_rows(state)
        assert len(rows) > 0, f"{state}: villages list is empty"


class TestCoordsJson:
    BOUNDS = {
        "andhra_pradesh": {"lat": (12.5, 20.5), "lng": (76.7, 84.8)},
        "telangana": {"lat": (15.8, 19.9), "lng": (77.3, 81.3)},
    }

    @pytest.mark.parametrize("state", STATES)
    def test_coords_within_bounding_box(self, state):
        import json

        data = json.loads((DATA_ROOT / state / "coords.json").read_text())
        bounds = self.BOUNDS[state]
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
        assert (
            out_of_range == []
        ), f"{state}: {len(out_of_range)} coords out of bounding box"


class TestMetaJson:
    @pytest.mark.parametrize("state", STATES)
    def test_required_keys_present(self, state):
        import json

        data = json.loads((DATA_ROOT / state / "meta.json").read_text())
        missing = {"counts", "source_date"} - set(data.keys())
        assert missing == set(), f"{state}/meta.json missing keys: {missing}"

    @pytest.mark.parametrize("state", STATES)
    def test_village_count_positive(self, state):
        import json

        data = json.loads((DATA_ROOT / state / "meta.json").read_text())
        count = data.get("counts", {}).get("villages", 0)
        assert count > 0, f"{state}/meta.json: village count is zero"


class TestGeoJSON:
    @pytest.mark.parametrize("state", STATES)
    def test_feature_collection_type(self, state):
        import json

        data = json.loads((DATA_ROOT / state / "districts.geojson").read_text())
        assert (
            data.get("type") == "FeatureCollection"
        ), f"{state}/districts.geojson: type is not FeatureCollection"

    @pytest.mark.parametrize("state", STATES)
    def test_features_not_empty(self, state):
        import json

        data = json.loads((DATA_ROOT / state / "districts.geojson").read_text())
        assert (
            len(data.get("features", [])) > 0
        ), f"{state}/districts.geojson: features array is empty"


class TestFetchSROScaffold:
    def test_dry_run_returns_records(self):
        """Stub dry-run must return non-empty lists for both states."""
        sys.path.insert(0, str(ROOT / "pipeline"))
        import fetch_sro

        ap = fetch_sro.fetch_ap_registrations("2026-07-18", dry_run=True)
        tg = fetch_sro.fetch_tg_registrations("2026-07-18", dry_run=True)
        assert len(ap) > 0, "AP dry-run returned no records"
        assert len(tg) > 0, "TS dry-run returned no records"

    def test_stub_record_structure(self):
        sys.path.insert(0, str(ROOT / "pipeline"))
        import fetch_sro

        records = fetch_sro._stub_records("Andhra Pradesh", "2026-07-18", count=3)
        required_keys = {
            "document_id",
            "registered_date",
            "state",
            "district",
            "property_type",
            "consideration_value_inr",
            "total_duty_inr",
        }
        for rec in records:
            missing = required_keys - set(rec.keys())
            assert missing == set(), f"Stub record missing fields: {missing}"


class TestPropertyHistory:
    def test_file_exists_and_valid(self):
        import json

        files = [
            DATA_ROOT / "andhra_pradesh" / "property_history.json",
            DATA_ROOT / "telangana" / "property_history.json",
            DATA_ROOT / "property_history.json",
        ]
        found = [f for f in files if f.exists()]
        assert (
            len(found) >= 2
        ), "Expected state-modular property_history.json files in AP and TS"

        for fpath in found:
            data = json.loads(fpath.read_text())
            assert "properties" in data, f"{fpath} missing 'properties' key"
            assert (
                len(data["properties"]) >= 1
            ), f"{fpath} expected at least 1 property record"

    def test_sale_history_and_poi_categories(self):
        import json

        files = [
            DATA_ROOT / "andhra_pradesh" / "property_history.json",
            DATA_ROOT / "telangana" / "property_history.json",
            DATA_ROOT / "property_history.json",
        ]
        required_cats = {"schools", "hospitals", "metro_railways"}
        for fpath in files:
            if not fpath.exists():
                continue
            data = json.loads(fpath.read_text())
            for prop in data["properties"]:
                sales = prop.get("sale_history", [])
                assert (
                    len(sales) >= 2
                ), f"Property {prop.get('property_id')} in {fpath.name} needs at least 2 sales records"
                for sale in sales:
                    assert (
                        sale.get("sale_price_inr", 0) > 0
                    ), f"Sale price must be positive in {prop.get('property_id')}"
                    assert (
                        "registration_doc_no" in sale
                    ), f"Sale doc no missing in {prop.get('property_id')}"

                services = prop.get("nearby_services", [])
                cats = {s.get("category") for s in services}
                assert required_cats.issubset(
                    cats
                ), f"Property {prop.get('property_id')} in {fpath.name} missing service categories: {required_cats - cats}"

    def test_cagr_calculation_accuracy(self):
        import json

        files = [
            DATA_ROOT / "andhra_pradesh" / "property_history.json",
            DATA_ROOT / "telangana" / "property_history.json",
            DATA_ROOT / "property_history.json",
        ]
        for fpath in files:
            if not fpath.exists():
                continue
            data = json.loads(fpath.read_text())
            for prop in data["properties"]:
                summary = prop["price_summary"]
                initial = summary["initial_price_inr"]
                latest = summary["latest_price_inr"]
                years = summary["holding_period_years"]
                expected_cagr = ((latest / initial) ** (1.0 / years) - 1.0) * 100.0
                actual_cagr = summary["cagr_pct"]
                assert (
                    abs(expected_cagr - actual_cagr) < 0.5
                ), f"Property {prop.get('property_id')} in {fpath.name} CAGR mismatch: expected {expected_cagr:.2f}%, got {actual_cagr:.2f}%"


class TestMarketTrends:
    @pytest.mark.parametrize("state", STATES)
    def test_file_exists_and_valid(self, state):
        import json

        fpath = DATA_ROOT / state / "market_trends.json"
        assert fpath.exists(), f"Missing {state}/market_trends.json"
        data = json.loads(fpath.read_text())
        assert (
            "employment_hubs" in data
        ), f"{state}/market_trends.json missing 'employment_hubs'"
        assert (
            len(data["employment_hubs"]) >= 4
        ), f"{state}/market_trends.json expected at least 4 hubs"
        assert (
            "time_series" in data
        ), f"{state}/market_trends.json missing 'time_series'"
        ts = data["time_series"]
        assert len(ts.get("quarters", [])) >= 5, f"{state} expected at least 5 quarters"
        assert (
            len(ts.get("localities", [])) >= 4
        ), f"{state} expected at least 4 localities"
