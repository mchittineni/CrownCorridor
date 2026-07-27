# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Releases are published automatically by [`release-please.yml`](.github/workflows/release-please.yml) adhering to CrownCorridor Semantic Versioning:

- **`MINOR` (x.Y.0)** — SRO dataset updates & historical data expansions (`data/**`).
- **`PATCH` (x.y.Z)** — Pipeline, validator, and ETL infrastructure changes (`pipeline/**`, `api/**`).
- **`MAJOR` (X.0.0)** — Web application features, layout, and UI frontend changes (`app/**`).

---

## [Unreleased]

## [2.0.0] — 2026-07-25

### Added

- **Hierarchical Location Query API & UI**: Implemented State ➔ District ➔ Mandal / Taluk ➔ Property List location scoping across the web portal (`app/index.html` & `app/portal.js`) and Fast-Read Search API (`/api/v1/hierarchy/{state_code}` and `/api/v1/hierarchy/{state_code}/{district}/{mandal}/properties`).
- **Interactive POI Map Focus & Google Maps Directions**: Added `📍 Focus Map` interactive POI centering and direct `🗺️ Google Maps ↗` turn-by-turn driving directions links for all nearby infrastructure services (schools, hospitals, metro stations, parks).
- **Statewide Village Property History Dataset Expansion**: Generated complete 25-year property histories covering **every official village** across all 61 districts in Telangana (9,287 properties) and Andhra Pradesh (15,197 properties), totaling **24,484 property records**.
- **Zero-PII Compliance Pipeline Safeguards**: Added `sanitize_and_anonymize_record()` to `pipeline/fetch_sro.py` to scrub personal buyer/seller names, phone numbers, and identity hashes while enforcing anonymized role classifications (`Private Individual Owner`, `Commercial Property Developer`, `Institutional Realty Fund`).
- **Automated Data Release Workflow**: Configured `.github/workflows/release.yml` with path-based triggers (`app/**`, `api/**`, `data/**`, `pipeline/**`) to automatically build and attach downloadable zip archives (`crown-corridor-ap-*.zip`, `crown-corridor-ts-*.zip`, `crown-corridor-all-*.zip`) on versioned releases.

### Changed

- **Native System Typography**: Switched default UI typography across the portal to the clean, native system font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`) for optimized legibility.
- **Hierarchical Selector Controls**: Replaced flat property selector in Property Sale History tab with cascading **State**, **District**, and **Mandal / Taluk** selection dropdowns.
- **Documentation & User Guide**: Updated `README.md` and `docs/user-guide.md` to reflect the v2.0.0 major release, location hierarchy, map navigation tools, and semantic versioning rules.

## [1.1.0] — 2026-07-25

### Added

- **Statewide Village Property Histories**: Generated complete property history datasets covering **every official village** across all 61 districts in Telangana (9,287 properties) and Andhra Pradesh (15,197 properties), totaling **24,484 property records**.
- **Automated Data Release Triggers**: Configured `.github/workflows/release.yml` with `data/**` path triggers to automatically publish versioned release artifacts whenever data updates are pushed to `main`.
- **Zero-PII Sanitization Helper**: Added `sanitize_and_anonymize_record()` in `pipeline/fetch_sro.py` to enforce role mapping and strip personal customer names, phone numbers, and identity hashes.

### Changed

- **All 61 District Support**: Updated `_stub_records()` in `pipeline/fetch_sro.py` to cover all 28 AP districts and all 33 TS districts.
- **Documentation**: Updated `README.md` feature matrix and JSDoc documentation to reflect statewide coverage.

### Changed

- **Global Header Search**: Refactored `initGlobalSearch()` in `app/portal.js` with debounced queries to the fast-read API endpoint and automatic fallback to in-memory dataset searching.
- **CI Toolchain Workflow**: Updated `.github/actions/setup-pipeline/action.yml` to install and cache dependencies from both `pipeline/requirements.txt` and `api/requirements.txt`.
- **GitHub Actions Infrastructure**: Upgraded all workflows to use latest action versions with validated commit SHAs for improved security and reproducibility. Updated `hashicorp/setup-terraform` from v3.1.2 to v4.0.1. Standardized `actions/checkout` (v7.0.1), `actions/setup-node` (v7.0.0), `actions/upload-artifact` (v7.0.1), `actions/upload-pages-artifact` (v5.0.0), `actions/deploy-pages` (v5.0.0), and `softprops/action-gh-release` (v3.0.2) across all 6 CI/CD workflows.

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

| Workflow             | Trigger                     | Purpose                                            |
| -------------------- | --------------------------- | -------------------------------------------------- |
| `ci.yml`             | Every PR → `main`           | Data validator + Ruff + ESLint + Pytest suite      |
| `infra-ci.yml`       | PR/Push to `main` (infra)   | Terraform test + Conftest OPA Rego policy checks   |
| `deploy-pages.yml`   | Push to `main`              | Data validation + publish _site to GitHub Pages    |
| `update-data.yml`    | Weekly Sun 01:00 UTC        | SRO data refresh → reviewed PR                     |
| `release-please.yml` | Merge to `main`             | Automated versioning, release PR & asset packaging |
| `uptime-check.yml`   | Every 6 hours               | Synthetic health & dataset availability checks     |
| `docs.yml`           | PR touching `app/portal.js` | JSDoc build-check                                  |

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
