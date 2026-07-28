# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Releases are published automatically by [`release-please.yml`](.github/workflows/release-please.yml) adhering to CrownCorridor Semantic Versioning:

- **`MINOR` (x.Y.0)** — SRO dataset updates & historical data expansions (`data/**`).
- **`PATCH` (x.y.Z)** — Pipeline, validator, and ETL infrastructure changes (`pipeline/**`, `application/api/**`).
- **`MAJOR` (X.0.0)** — Web application features, layout, and UI frontend changes (`application/app/**`).

## [1.0.0](https://github.com/mchittineni/iacsecbench/compare/iacsecbench-v1.0.0...iacsecbench-v1.0.0) (2026-07-28)


### Bug Fixes

* **benchmark:** update benchmark infrastructure ([f194119](https://github.com/mchittineni/iacsecbench/commit/f1941197dfe04bc588b513a5bff324a36b3cd0c2))
* **benchmark:** update benchmark infrastructure for security audit remediation ([396cab1](https://github.com/mchittineni/iacsecbench/commit/396cab168d2ecfce127c110edddd984ff3086456))
* **benchmark:** update benchmark results ([3b64b35](https://github.com/mchittineni/iacsecbench/commit/3b64b352a516aaa3da6e9a90b51b66acc685352b))
* **benchmark:** update infrastructure for security audit remediation ([b538ec7](https://github.com/mchittineni/iacsecbench/commit/b538ec7c93236573f3dca34f5d82a75ce9698441))
* **benchmark:** updated CIS AWS Benchmark policy to address security audit findings ([3def95a](https://github.com/mchittineni/iacsecbench/commit/3def95a512ec7fd1be16ea444b7defbeb5552634))
* **security:** update security policies and configurations ([417274c](https://github.com/mchittineni/iacsecbench/commit/417274c4a19c16d68afb81fd2382cc25e9082d24))
* **terraform:** update terraform files to address security audit findings ([0a02487](https://github.com/mchittineni/iacsecbench/commit/0a024876aec73f646842780521ff91f807beeba9))
* **terraform:** updated terraform files to fix security audit issues ([c6b69b0](https://github.com/mchittineni/iacsecbench/commit/c6b69b0f0edcf24b3a7c0a15c2e15e272607a99e))

### Security & Infrastructure Hardening

- **iac:** enforce S3 multipart upload cleanup (`abort_incomplete_multipart_upload`), CloudFront geo-restriction (whitelist `IN`), SNS topic KMS encryption, RDS deletion protection, and CloudWatch log group retention (365 days)
- **iac:** align Rego CIS AWS Benchmark S3 encryption policy evaluation with decoupled Terraform provider resources
- **ci:** configure `.checkov.yaml` and `.github/workflows/infra-ci.yml` for static analysis scanning and policy enforcement
- **tests:** resolve resource, variable, and output references across native Terraform test suites (`terraform test`)

### Features

- add Bayut.com-inspired Search by Commute and Regional Market Trends features
- **benchmark:** expand IaCSecBench to 345 publication-grade research cases, self-contained dataset, taxonomy, leaderboard, and scoring protocol
- complete 25-year property histories across all buildings, flats, and villas in AP & TS
- expanded 25-year property sale histories for AP & TS districts
- **iac:** end-to-end terraform architecture, cis benchmark policies, and 100% test coverage
- implement FastAPI search microservice and Typesense fast-read architecture
- implement real-time real estate monitoring portal for AP & Telangana
- improve insights to colony and apartment block levels
- **pipeline:** add 24k statewide property history, zero-PII, hierarchical API & release workflow
- state-modular SRO property history, comparison tool, zero-PII compliance & repo standards
- **workflows:** publish docs to GitHub Pages

### Bug Fixes

- **backend:** updated backend code to improve functionality and performance
- **ci:** add pytest-cov to requirements and setup-pipeline action; fallback --cov gracefully
- **ci:** added isort black profile configuration in pyproject.toml
- **ci:** added sys.path initialization in test_validate_iac.py and ruff ignore rules
- **ci:** fix conftest curl download flags and sync python formatting with black
- **ci:** format test_validate.py imports with isort and black
- **ci:** refine docs.yml workflow to verify JSDoc and upload documentation build artifact
- **ci:** update ci workflow to include new test steps
- **conftest:** updated conftest to use latest version
- **devops:** update CI/CD workflows to improve reliability and maintainability
- **format:** fix format in changelog
- **iac:** update rego policy syntax to v1 for conftest compatibility
- **lint:** update eslint config to use new rules and plugins
- **portal:** add fallback path resolution for geographic and market trends data files
- **pre-commit:** resolve all pre-commit hook warnings and bandit/pylint checks
- **README:** update README with new information
- **release:** fix release workflow to use correct branch and tag
- **workflows:** fix release tag trigger glob and add manual trigger
- **workflows:** force-push SRO data branches
- **workflows:** handle pull request creation failure gracefully
- **workflows:** resolve Scheduled Data Update and pin actions
- **workflows:** support manual tags in release workflow
- **workflows:** update release.yml to parse semantic versioning tag from CHANGELOG.md

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

#### Research-Grade IaCSecBench Framework (`benchmark/`, `evaluation/`, `leaderboard/`, `docs/`)

- **345-Case Research Benchmark Suite** — Master catalog in `benchmark/benchmark.json` containing 345 self-contained test cases across 12 categories (`IAM`, `NET`, `STO`, `ENC`, `CMP`, `K8S`, `SRV`, `MON`, `SEC`, `ID`, `PII`, `TF`) with balanced classes (173 Pass / 172 Fail).
- **Construct Badges & Feature Metadata** — Test cases exercise advanced Terraform syntax: `dynamic_blocks`, `locals`, `for_each`, `count`, `nested_modules`, `multiple_providers`, `variable_validation`, `depends_on`, `lifecycle_rules`, `tfvars`, `opa`, `native_tests`.
- **Modular Case Architecture (`benchmark/cases/`)** — Individual self-contained case folders (`IAM-001/` through `TF-003/`) containing `main.tf`, `variables.tf`, `expected.json`, and `metadata.json`.
- **Golden Baseline Outputs (`benchmark/golden_results/`)** — Reference golden JSON outputs for Checkov, tfsec, Terrascan, OPA, and IaCSecBench Engine.
- **Automated Scoring Protocol (`evaluation/`)** — `evaluation/metrics.py` and `evaluation/score.py` calculating Recall, Precision, Accuracy, F1 Score, False Positive Rate (FPR), False Negative Rate (FNR), and Execution Latency.
- **Published Research Leaderboard (`leaderboard/results.csv`)** — Tabular comparative baseline matrix exported across 5 static analysis engines.
- **Research Taxonomy & Protocol Docs** — Added `docs/taxonomy.md` (5 top-level domains) and `docs/benchmark_protocol.md` (scoring methodology and reproducibility guidelines).
- **Reproducible Experiment Suite** — Integrated scoring protocol into `./experiments/run_all.sh` and `pipeline/run_experiments.py` generating telemetry in `results/` and `benchmark/reports/`.

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
