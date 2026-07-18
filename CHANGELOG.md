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

| State | Districts | Mandals | Villages | Source |
|-------|-----------|---------|----------|--------|
| Andhra Pradesh | 28 | 684 | 15,197 | LGD via data.gov.in (15 Jul 2026) |
| Telangana | 33 | 616 | 9,287 | LGD via data.gov.in (15 Jul 2026) |

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

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Every PR → `main`/`develop` | Data validator + 23 pytest cases |
| `deploy-pages.yml` | Push to `main` | Build `_site/` and publish to GitHub Pages |
| `update-data.yml` | Weekly Sun 01:00 UTC | SRO data refresh → reviewed PR |
| `release.yml` | Tag `v*.*.*` | Versioned release + AP/TS/combined zip archives |
| `docs.yml` | PR touching `app/portal.js` | JSDoc build-check |

Four shared composite actions: `setup-pipeline`, `datagov-fetch`,
`publish-data-branch`, `overlay-data-branches`.

#### Documentation (`docs/`)

- `docs/index.md` — architecture overview and navigation hub.
- `docs/cadastral-hosting.md` — R2 cadastral PMTile hosting reference for AP & TS.
- `jsdoc.json` — JSDoc config targeting `app/portal.js`.

#### Project Files

- `README.md` — full feature table, directory layout, local dev, test commands,
  data attribution, and GitHub Pages setup guide.
- `CHANGELOG.md` (this file).
- `LICENSE` — MIT for code, GODL-India for data.
- `DATA_LICENSE.md` — full GODL-India terms and required attribution.
- `CONTRIBUTING.md`, `SECURITY.md` — community-health files.
- `.gitignore` — excludes `.venv/`, `__pycache__/`, `data/sro_feed/`, `.pytest_cache/`.

---

[Unreleased]: https://github.com/mchittineni/CrownCorridor/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/mchittineni/CrownCorridor/releases/tag/v1.0.0
[releases]: https://github.com/mchittineni/CrownCorridor/releases
