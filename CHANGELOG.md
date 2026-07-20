# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Releases are published automatically by
[`release.yml`](.github/workflows/release.yml): a **data refresh** is a _patch_,
a **new feature** is a _minor_, and a breaking change is a _major_. Every
release attaches downloadable datasets; see [Releases][releases].

---

## [Unreleased]

### Added

- **Fast-Read Search API (`api/`)**: Added async FastAPI microservice (`api/main.py` & `api/search.py`) providing sub-100ms search endpoints (`/api/v1/search`, `/api/v1/properties/{id}`, `/health`) with fuzzy search, state-level filtering (`TS` / `AP`), price bounds, and CAGR filters.
- **Typesense Ingestion Pipeline**: Added `pipeline/index_to_typesense.py` to index property records and SRO feeds into Typesense search engine collections.
- **API Test Suite**: Added `pipeline/tests/test_api.py` with unit tests for API endpoints, Pydantic data model validation, and indexing dry-runs.

### Changed

- **Global Header Search**: Refactored `initGlobalSearch()` in `app/portal.js` with debounced queries to the fast-read API endpoint and automatic fallback to in-memory dataset searching.
- **CI Toolchain Workflow**: Updated `.github/actions/setup-pipeline/action.yml` to install and cache dependencies from both `pipeline/requirements.txt` and `api/requirements.txt`.

## [1.0.1] — 2026-07-19

### Fixed

- **Scheduled Data Update Workflow**: Configured git user settings globally and locally inside the target temporary clone in the `publish-data-branch` composite action, fixing the fatal `Author identity unknown (exit code 128)` error.
- **SRO Feed Generation**: Added the `--dry-run` flag to SRO fetch steps in `update-data.yml` to generate simulated records on scheduled runs where official APIs are not configured.
- **Push Conflict Resolution**: Configured automated branch pushing to use force-push (`git push -f`) in `update-data.yml` to prevent failures when pushing duplicate branch references on the same day.
- **PR Permissions Fallback**: Added custom error handling around `gh pr create` in `update-data.yml` to print setup instructions instead of failing the workflow when pull request creation is disabled by default on the token.
- **Node.js Deprecations**: Updated all workflows to run setup actions utilizing the latest secure tags and commit SHAs, elevating Node.js version target from the deprecated `20` to `24` in `docs.yml`.

### Removed

- Removed unused legacy localization data files from `data/andhra_pradesh/` and `data/telangana/` directories (`names.json`, `names_translit.json`, `regions_native.json`, `boundaries_meta.json`).

## [1.0.0] — 2026-07-18

### Added — Initial Release

Crown Corridor is a next-generation real-time real estate and property monitoring
portal for **Andhra Pradesh & Telangana**. This is the first release.

#### Portal (`app/`)

- **Live SRO Ticker** — real-time property registration feed across all Sub-Registrar
  Offices in AP & TS, updating every few seconds.
- **Verified Property Listings** — 45+ geospatially verified properties (plots, flats,
  villas, farm land) across real AP & TS districts, with inquiry forms.
- **Boundary Explorer** — village-level LGD coordinate drill-down; zoom ≥ 11 renders
  PMTiles vector cadastral parcel overlays via MapLibre GL.
- **Stamp Duty Calculator** — accurate registration tax breakdown:
  AP 7.5% (stamp 5% + registration 1% + transfer 1.5%), TS 6.0%.
- **Government Guidance Value Directory** — official SRO guide valuations by district
  and mandal for both states.
- **Developer API Console** — queryable JSON sandbox and webhook alert configuration.
- Dark glassmorphism design system with animated ticker and interactive map.

#### Geographic Data (`data/`)

| State          | Districts | Mandals | Villages | Source                            |
| -------------- | --------- | ------- | -------- | --------------------------------- |
| Andhra Pradesh | 28        | 684     | 15,197   | LGD via data.gov.in (15 Jul 2026) |
| Telangana      | 33        | 616     | 9,287    | LGD via data.gov.in (15 Jul 2026) |

Files per state: `regions.json`, `villages.json`, `coords.json`,
`districts.geojson`, `mandals.geojson`, `meta.json`.

#### Data Pipeline (`pipeline/`)

- `validate_data.py` — six-section data integrity validator (both states):
  required files, regions FK integrity, villages columnar format, coordinate bounding
  boxes, `meta.json` required fields, GeoJSON structure. Exits `0`/`1`.
- `fetch_sro.py` — SRO registration data fetcher scaffold with exit-75 outage
  contract (upstream unreachable → CI skip, not fail), `--dry-run`, `--date`,
  `--state` flags. Stub records mirror the real SRO API response shape.
- `requirements.txt` — minimal: `requests`, `pytest`.
- `tests/test_validate.py` — 23 pytest cases across 7 classes; all passing ✓.

#### CI/CD (`.github/`)

| Workflow           | Trigger                     | Purpose                                         |
| ------------------ | --------------------------- | ----------------------------------------------- |
| `ci.yml`           | Every PR → `main`/`develop` | Data validator + 23 pytest cases                |
| `deploy-pages.yml` | Push to `main`              | Build `_site/` and publish to GitHub Pages      |
| `update-data.yml`  | Weekly Sun 01:00 UTC        | SRO data refresh → reviewed PR                  |
| `release.yml`      | Tag `v*.*.*`                | Versioned release + AP/TS/combined zip archives |
| `docs.yml`         | PR touching `app/portal.js` | JSDoc build-check                               |

Four shared composite actions: `setup-pipeline`, `datagov-fetch`,
`publish-data-branch`, `overlay-data-branches`.

#### Documentation (`docs/`)

- `docs/index.md` — architecture overview and navigation hub.
- `jsdoc.json` — JSDoc config targeting `app/portal.js`.

#### Project Files

- `README.md` — full feature table, directory layout, local dev, test commands,
  data attribution, and GitHub Pages setup guide.
- `CHANGELOG.md` (this file).
- `LICENSE` — MIT for code, GODL-India for data.
- `CONTRIBUTING.md`, `SECURITY.md` — community-health files.
- `.gitignore` — excludes `.venv/`, `__pycache__/`, `data/sro_feed/`, `.pytest_cache/`.

---

[Unreleased]: https://github.com/mchittineni/CrownCorridor/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/mchittineni/CrownCorridor/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/mchittineni/CrownCorridor/releases/tag/v1.0.0
[releases]: https://github.com/mchittineni/CrownCorridor/releases
