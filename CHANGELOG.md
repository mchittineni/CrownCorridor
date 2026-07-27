# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Releases are published automatically by [`release-please.yml`](.github/workflows/release-please.yml) adhering to CrownCorridor Semantic Versioning:

- **`MINOR` (x.Y.0)** — SRO dataset updates & historical data expansions (`data/**`).
- **`PATCH` (x.y.Z)** — Pipeline, validator, and ETL infrastructure changes (`pipeline/**`, `application/api/**`).
- **`MAJOR` (X.0.0)** — Web application features, layout, and UI frontend changes (`application/app/**`).

---

## [1.0.0] — 2026-07-27

### Added — Initial Release

Crown Corridor is a next-generation real-time real estate discovery and property monitoring portal for **Andhra Pradesh & Telangana**, integrated with an Open-Source IaC Security & Evaluation Benchmark Framework.

#### Web Portal (`application/app/`)

- **Live SRO Ticker** — Real-time property registration feed across all Sub-Registrar Offices in AP & TS, updating dynamically.
- **Verified Property Listings** — Geospatially verified properties (plots, flats, villas, farm land) across real AP & TS districts with detailed inquiry features.
- **Hierarchical Location Query UI** — State ➔ District ➔ Mandal / Taluk ➔ Property List location scoping across the web portal (`application/app/index.html` & `application/app/portal.js`).
- **Interactive POI Map Focus & Google Maps Directions** — `📍 Focus Map` interactive POI centering and direct `🗺️ Google Maps ↗` turn-by-turn driving directions links for all nearby infrastructure services (schools, hospitals, metro stations, parks).
- **Boundary Explorer** — Village-level LGD coordinate drill-down; vector cadastral parcel overlays via MapLibre GL.
- **Stamp Duty Calculator** — Accurate registration tax breakdown (AP 7.5%, TS 6.0%).
- **Government Guidance Value Directory** — Official SRO guide valuations by district and mandal for both states.
- **Developer API Console** — Queryable JSON sandbox and webhook alert configuration.
- **Design System** — Dark glassmorphic design system using native system typography stack for optimized legibility and performance.

#### Backend & Fast-Read API (`application/api/`)

- **Hierarchical Location API** — High-performance endpoints (`/api/v1/hierarchy/{state_code}` and `/api/v1/hierarchy/{state_code}/{district}/{mandal}/properties`) for structured geographical search.
- **Fast-Read Search & Typesense Integration** — High-throughput property search and retrieval services.

#### IaC Security & Evaluation Benchmark Framework (`pipeline/eval_framework/`, `infrastructure/`, `security_framework/`)

- **Open-Source IaC Evaluation Engine** — Positioned IaC evaluation engine into a reusable Python framework package (`pipeline/eval_framework/`).
- **Comparative Benchmarking Engine** — Built comparative benchmark driver (`pipeline/eval_framework/comparative_eval.py`) evaluating accuracy, precision, recall, and execution latency against established tools (**Checkov**, **tfsec**, **Sentinel / OPA**, and **Terratest**).
- **Public Benchmark Datasets** — Created standardized public benchmark dataset in `data/benchmarks/benchmarks.json` across 10 cloud infrastructure modules.
- **Reproducible Experiment Suite** — Implemented `pipeline/run_experiments.py` for automated evaluation telemetry generation saved to `data/benchmarks/experiment_results.json`.
- **Infrastructure as Code & Rego Security Policies** — Complete HCL infrastructure modules (`infrastructure/`) and OPA Rego security policies (`security_framework/ policies/cis_aws_benchmark.rego`) updated to v1 syntax for conftest compatibility.

#### Geographic Data & Zero-PII Data Pipeline (`data/`, `pipeline/`)

| State          | Districts | Mandals | Villages | Source                            |
| -------------- | --------- | ------- | -------- | --------------------------------- |
| Andhra Pradesh | 28        | 684     | 15,197   | LGD via data.gov.in (15 Jul 2026) |
| Telangana      | 33        | 616     | 9,287    | LGD via data.gov.in (15 Jul 2026) |

- **Statewide Village 25-Year Property Histories** — 24,484 property records spanning all 61 districts in TS (9,287) and AP (15,197).
- **Zero-PII Privacy Safeguards** — `sanitize_and_anonymize_record()` in `pipeline/fetch_sro.py` enforcing strict anonymized role classifications (`Private Individual Owner`, `Commercial Property Developer`, `Institutional Realty Fund`) and stripping personal identifying data.
- **Eight-Section Data Integrity Validator** — `pipeline/validate_data.py` validating required files, regions integrity, village schemas, coordinate bounding boxes, GeoJSON structures, property histories, and market trends.

#### CI/CD & Repository Infrastructure (`.github/`)

| Workflow             | Trigger                     | Purpose                                            |
| -------------------- | --------------------------- | -------------------------------------------------- |
| `ci.yml`             | Every PR → `main`           | Data validator + Ruff + ESLint + Pytest suite      |
| `infra-ci.yml`       | PR/Push to `main` (infra)   | Terraform test + Conftest OPA Rego policy checks   |
| `deploy-pages.yml`   | Push to `main`              | Data validation + publish _site to GitHub Pages    |
| `update-data.yml`    | Weekly Sun 01:00 UTC        | SRO data refresh → reviewed PR                     |
| `release-please.yml` | Merge to `main`             | Automated versioning, release PR & asset packaging |
| `uptime-check.yml`   | Every 6 hours               | Synthetic health & dataset availability checks     |
| `docs.yml`           | PR touching `app/portal.js` | JSDoc build-check                                  |

#### Documentation & Project Guidelines

- `README.md` — Full feature table, architecture layout, dev instructions, zero-PII rules, and test commands.
- `CONTRIBUTING.md`, `SECURITY.md`, `CITATION.cff` — Community health, security policy, and scientific citation metadata.

---

[1.0.0]: https://github.com/mchittineni/CrownCorridor/releases/tag/v1.0.0
[releases]: https://github.com/mchittineni/CrownCorridor/releases
