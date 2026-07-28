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

* **citation:** update citation file to include correct DOI and authors ([2d5e98a](https://github.com/mchittineni/iacsecbench/commit/2d5e98a0e9a255aee315205231ef0b1d59c3f992))

## [1.0.0](https://github.com/mchittineni/iacsecbench/compare/iacsecbench-v1.0.0...iacsecbench-v1.0.0) (2026-07-28)

### Bug Fixes

- **benchmark:** update benchmark infrastructure ([f194119](https://github.com/mchittineni/iacsecbench/commit/f1941197dfe04bc588b513a5bff324a36b3cd0c2))
- **benchmark:** update benchmark infrastructure for security audit remediation ([396cab1](https://github.com/mchittineni/iacsecbench/commit/396cab168d2ecfce127c110edddd984ff3086456))
- **benchmark:** update benchmark results ([3b64b35](https://github.com/mchittineni/iacsecbench/commit/3b64b352a516aaa3da6e9a90b51b66acc685352b))
- **benchmark:** update infrastructure for security audit remediation ([b538ec7](https://github.com/mchittineni/iacsecbench/commit/b538ec7c93236573f3dca34f5d82a75ce9698441))
- **benchmark:** updated CIS AWS Benchmark policy to address security audit findings ([3def95a](https://github.com/mchittineni/iacsecbench/commit/3def95a512ec7fd1be16ea444b7defbeb5552634))
- **security:** update security policies and configurations ([417274c](https://github.com/mchittineni/iacsecbench/commit/417274c4a19c16d68afb81fd2382cc25e9082d24))
- **terraform:** update terraform files to address security audit findings ([0a02487](https://github.com/mchittineni/iacsecbench/commit/0a024876aec73f646842780521ff91f807beeba9))
- **terraform:** updated terraform files to fix security audit issues ([c6b69b0](https://github.com/mchittineni/iacsecbench/commit/c6b69b0f0edcf24b3a7c0a15c2e15e272607a99e))
- **citation:** update citation file to include correct DOI and authors ([2d5e98a](https://github.com/mchittineni/iacsecbench/commit/2d5e98a0e9a255aee315205231ef0b1d59c3f992))

### Security & Infrastructure Hardening

- **iac:** enforce S3 multipart upload cleanup (`abort_incomplete_multipart_upload`), CloudFront geo-restriction (whitelist `IN`), SNS topic KMS encryption, RDS deletion protection, and CloudWatch log group retention (365 days) ([706b39b](https://github.com/mchittineni/iacsecbench/commit/706b39bf310154545b4a042108c12f7d4f9ae64b))
- **iac:** align Rego CIS AWS Benchmark S3 encryption policy evaluation with decoupled Terraform provider resources ([11bf07b](https://github.com/mchittineni/iacsecbench/commit/11bf07b70efcfccb27426e97d3979a7940ee79ba))
- **ci:** configure `.checkov.yaml` and `.github/workflows/infra-ci.yml` for static analysis scanning and policy enforcement ([3f2bea6](https://github.com/mchittineni/iacsecbench/commit/3f2bea6dd563619769afd024cef2737782b52a9a))
- **tests:** resolve resource, variable, and output references across native Terraform test suites (`terraform test`) ([4fe208c](https://github.com/mchittineni/iacsecbench/commit/4fe208c998dbafd319d9190c41159917599b60e0))

### Features

- **portal:** add Bayut.com-inspired Search by Commute and Regional Market Trends features ([23a05a6](https://github.com/mchittineni/iacsecbench/commit/23a05a6367f4c8571dc3f05e7dc2229bed3c5293))
- **benchmark:** expand IaCSecBench to 345 publication-grade research cases, self-contained dataset, taxonomy, leaderboard, and scoring protocol ([65edf5f](https://github.com/mchittineni/iacsecbench/commit/65edf5f2ce7dc631ef9869446e39b1a13fe6f18f))
- **data:** complete 25-year property histories across all buildings, flats, and villas in AP & TS ([fb8a85f](https://github.com/mchittineni/iacsecbench/commit/fb8a85fbd35c2d328459a140d74da2cd7d3105f4))
- **data:** expanded 25-year property sale histories for AP & TS districts ([5fcaae4](https://github.com/mchittineni/iacsecbench/commit/5fcaae476fd32d57f23e236e1db7fc221df816c2))
- **iac:** end-to-end terraform architecture, cis benchmark policies, and 100% test coverage ([706b39b](https://github.com/mchittineni/iacsecbench/commit/706b39bf310154545b4a042108c12f7d4f9ae64b))
- **backend:** implement FastAPI search microservice and Typesense fast-read architecture ([e8a164e](https://github.com/mchittineni/iacsecbench/commit/e8a164ea6a43e18377286562f2c8a7b464c9ecd7))
- **portal:** implement real-time real estate monitoring portal for AP & Telangana ([76c2bd0](https://github.com/mchittineni/iacsecbench/commit/76c2bd0a7ea83666e69c5a1a9f8be70cf74db7e7))
- **portal:** improve insights to colony and apartment block levels ([8eee5fd](https://github.com/mchittineni/iacsecbench/commit/8eee5fda9c07e8f76116badd0f87275b0bf463a7))
- **pipeline:** add 24k statewide property history, zero-PII, hierarchical API & release workflow ([1ca88be](https://github.com/mchittineni/iacsecbench/commit/1ca88be3541a983f3b980183655f73350a23ded7))
- **data:** state-modular SRO property history, comparison tool, zero-PII compliance & repo standards ([e1c5a4a](https://github.com/mchittineni/iacsecbench/commit/e1c5a4afa86142d691919569291b80306e038e89))
- **workflows:** publish docs to GitHub Pages ([9117e99](https://github.com/mchittineni/iacsecbench/commit/9117e99324ce2241278be1e4610b2213e7645059))

### Bug Fixes

- **backend:** updated backend code to improve functionality and performance ([23bbdd9](https://github.com/mchittineni/iacsecbench/commit/23bbdd985093fd1b48378bbf9eef8792d83b254a))
- **ci:** add pytest-cov to requirements and setup-pipeline action; fallback --cov gracefully ([59feef1](https://github.com/mchittineni/iacsecbench/commit/59feef14df26ab941206cb5c445d7de659003260))
- **ci:** added isort black profile configuration in pyproject.toml ([dbe630b](https://github.com/mchittineni/iacsecbench/commit/dbe630b8463828e1ac6a43b3a4ef27f9fb637c1d))
- **ci:** added sys.path initialization in test_validate_iac.py and ruff ignore rules ([d1ff841](https://github.com/mchittineni/iacsecbench/commit/d1ff8410f89cef4091d73436b369193898236c8b))
- **ci:** fix conftest curl download flags and sync python formatting with black ([ff32799](https://github.com/mchittineni/iacsecbench/commit/ff3279964d319d2d09c7972da1f5f05a1a2d39d7))
- **ci:** format test_validate.py imports with isort and black ([4fe208c](https://github.com/mchittineni/iacsecbench/commit/4fe208c998dbafd319d9190c41159917599b60e0))
- **ci:** refine docs.yml workflow to verify JSDoc and upload documentation build artifact ([1fc12d9](https://github.com/mchittineni/iacsecbench/commit/1fc12d9abbf5a1d4f2ea750e7831daf4463995d7))
- **ci:** update ci workflow to include new test steps ([5ef879c](https://github.com/mchittineni/iacsecbench/commit/5ef879c23fea41e021031cdd1998884a927ee8ed))
- **citation:** update citation file to include correct DOI and authors ([2d5e98a](https://github.com/mchittineni/iacsecbench/commit/2d5e98a0e9a255aee315205231ef0b1d59c3f992))
- **conftest:** updated conftest to use latest version ([d1dc028](https://github.com/mchittineni/iacsecbench/commit/d1dc028d6d806db80c87591126753bd8fce2a392))
- **devops:** update CI/CD workflows to improve reliability and maintainability ([3f2bea6](https://github.com/mchittineni/iacsecbench/commit/3f2bea6dd563619769afd024cef2737782b52a9a))
- **format:** fix format in changelog ([1cd10ea](https://github.com/mchittineni/iacsecbench/commit/1cd10ea6b8d2649a79d95b7de655653a94053c51))
- **iac:** update rego policy syntax to v1 for conftest compatibility ([11bf07b](https://github.com/mchittineni/iacsecbench/commit/11bf07b70efcfccb27426e97d3979a7940ee79ba))
- **lint:** update eslint config to use new rules and plugins ([a47c0a5](https://github.com/mchittineni/iacsecbench/commit/a47c0a54cb7c86fe9747db4074a94e02044cf071))
- **portal:** add fallback path resolution for geographic and market trends data files ([168d024](https://github.com/mchittineni/iacsecbench/commit/168d02479745e96c0ebed0bf40afa4125f45838c))
- **pre-commit:** resolve all pre-commit hook warnings and bandit/pylint checks ([42112db](https://github.com/mchittineni/iacsecbench/commit/42112db109fa06f3a74830852bc782d1fe81becb))
- **README:** update README with new information ([cd961b7](https://github.com/mchittineni/iacsecbench/commit/cd961b78b7f7f1395c4bffab99beea9a40abf40a))
- **release:** fix release workflow to use correct branch and tag ([f8754a2](https://github.com/mchittineni/iacsecbench/commit/f8754a2f4d4f9a3e248c21e5bae070e39498ab3e))
- **workflows:** fix release tag trigger glob and add manual trigger ([37299ce](https://github.com/mchittineni/iacsecbench/commit/37299ceff375063b13835b5010d6c2c29a77f545))
- **workflows:** force-push SRO data branches ([429d15d](https://github.com/mchittineni/iacsecbench/commit/429d15df5b4551f49f5883eeb430c7389d1343f6))
- **workflows:** handle pull request creation failure gracefully ([67a96d0](https://github.com/mchittineni/iacsecbench/commit/67a96d0cd27550d69d4890fe989adea2890510c2))
- **workflows:** resolve Scheduled Data Update and pin actions ([34edb0b](https://github.com/mchittineni/iacsecbench/commit/34edb0bb44e40fd66ad68bad96f89490b3667ce7))
- **workflows:** support manual tags in release workflow ([74f0bc4](https://github.com/mchittineni/iacsecbench/commit/74f0bc49f2970ae5a2b59eb9c3d4713d9c8d3fe2))
- **workflows:** update release.yml to parse semantic versioning tag from CHANGELOG.md ([22faef5](https://github.com/mchittineni/iacsecbench/commit/22faef5ff5343223ab38c0a5016ebf0ce352c7e7))

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
