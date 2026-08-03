# IaCSecBench & Crown Corridor

> **An Open Framework and Empirical Benchmark for Evaluating Infrastructure-as-Code Security Gates**
> _Validated via Crown Corridor — A Next-Generation Geospatial Property Discovery Portal for Andhra Pradesh & Telangana._

[![CI](https://github.com/mchittineni/IaCSecBench/actions/workflows/ci.yml/badge.svg)](https://github.com/mchittineni/IaCSecBench/actions/workflows/ci.yml)
[![Infra CI](https://github.com/mchittineni/IaCSecBench/actions/workflows/infra-ci.yml/badge.svg)](https://github.com/mchittineni/IaCSecBench/actions/workflows/infra-ci.yml)
[![Benchmark](https://github.com/mchittineni/IaCSecBench/actions/workflows/benchmark.yml/badge.svg)](https://github.com/mchittineni/IaCSecBench/actions/workflows/benchmark.yml)
[![Deploy](https://github.com/mchittineni/IaCSecBench/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/mchittineni/IaCSecBench/actions/workflows/deploy-pages.yml)
[![Tests Passing](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](https://github.com/mchittineni/IaCSecBench)
[![Coverage 100%](https://img.shields.io/badge/IaC_Coverage-100%25-success.svg)](https://github.com/mchittineni/IaCSecBench)
[![Security Validated](https://img.shields.io/badge/Security-Zero--PII%20Validated-blue.svg)](https://github.com/mchittineni/IaCSecBench)
[![Benchmark Reproducible](https://img.shields.io/badge/Benchmark-Reproducible-orange.svg)](https://github.com/mchittineni/IaCSecBench)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.21645016-purple.svg)](https://doi.org/10.5281/zenodo.21645016)

---

## 📌 Project Overview

Crown Corridor contains two independent components:

1. **Cloud Application Platform (Crown Corridor)**: A real estate discovery portal featuring verified listings, geospatial maps, state-modular SRO property sale histories, CAGR analytics, and an AWS Terraform reference architecture.
2. **IaCSecBench Security Evaluation Framework**: An open-source Infrastructure-as-Code security evaluation framework designed to benchmark static analysis tools, policy engines, and secret detection suites.

---

## 💡 Why This Project Exists

Modern IaC security tools detect different classes of vulnerabilities with varying trade-offs in detection capabilities, false positive rates, and runtime latency.

This repository provides **IaCSecBench**, a unified evaluation framework to measure:

- **Detection Capability**: Evaluating true positives, recall, and edge-case coverage across AST scanners, policy engines, and integration tests.
- **Runtime Overhead**: Benchmarking execution latency (ms) per scanning pass.
- **Policy Coverage**: Measuring compliance against CIS AWS Foundations Benchmark standards.
- **Maintenance Complexity**: Assessing policy-as-code complexity, zero-PII compliance, and reproducible experiment workflows.

---

## ✨ Features

| Feature                                     | Description                                                                                                                                        |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🔴 **Live SRO Feed**                        | Real-time property registration ticker with pause/resume and speed controls                                                                        |
| 🚗 **Search by Commute**                    | Filter properties by driving time to workplace hubs (HITECH City, Financial District, Amaravati)                                                   |
| 📈 **Regional Market Trends**               | Time-series price trajectory charts (2016-2026) and top appreciating localities leaderboard                                                        |
| 🔍 **Global Smart Search**                  | Persistent header bar with instant autocomplete for properties, listings, and districts                                                            |
| ⚖️ **Property Comparison**                  | Side-by-side spec comparison modal for up to 3 properties (Valuation, CAGR, Rate/SqFt, Metro)                                                      |
| 🏰 **Complete State Property History**      | Full state historical property records for 24,484 villages (15,197 AP, 9,287 TS) across all 61 districts                                           |
| 🗂️ **Hierarchical Location Query**          | Filter properties via State ➔ District ➔ Mandal / Taluk ➔ Property List (Fast-Read API & Web UI)                                                   |
| 🖨️ **Valuation Audit Report**               | One-click printable PDF/audit summary with transaction logs and infrastructure scores                                                              |
| 📍 **Infrastructure Explorer**              | Nearby schools, hospitals, metro/railway stations with Focus Map and Google Maps turn-by-turn links                                                |
| 🔒 **Zero-PII Compliance**                  | Strict privacy protections — no customer names or personal data stored (automated CI check)                                                        |
| 🏗️ **AWS Terraform Reference Architecture** | Modular Terraform (>= 1.15.0, AWS ~> 6.56.0) reference architecture with WAF, CloudFront, API Gateway, Fargate & PostGIS                           |
| 🛡️ **CIS AWS Benchmark Security**           | OPA / Rego policy engine, VPC Flow Logs, S3 TLS-Only, ALB Header Dropping, and native `.tftest.hcl` suites                                         |
| 🔬 **IaCSecBench Evaluation Framework**     | Open-source framework, comparative benchmarking (Checkov, tfsec, plan-level OPA), public datasets & reproducible experiments (`experiments/run_baselines.sh`) |

---

## 🏛️ Infrastructure Architecture Diagram

> [!NOTE]
> The primary production deployment for Crown Corridor is hosted on **GitHub Pages** (built via `.github/workflows/deploy-pages.yml`). The AWS cloud topology depicted below codified under `infrastructure/` represents a validated **Reference Architecture** for production scale-out.

```
[ Web / Mobile Clients ]
           │
           ▼
[ AWS WAF Web ACL ] (Rate Limiting, OWASP Top 10)
           │
           ▼
[ Amazon CloudFront CDN ] (TLS 1.3, HTTPS Redirection)
           │
 ┌─────────┴─────────────────────────────┐
 ▼                                       ▼
[ Amazon S3 (Web UI) ]        [ Amazon API Gateway v2 ]
(KMS Encrypted, OAC, TLS)     (Cognito JWT Authorizer, Throttling, CORS)
                                         │
                                         ▼
                            [ AWS ECS Fargate Cluster ]
                            ┌────────────────────────────┐
                            │ • FastAPI Microservice     │
                            │ • Typesense (EFS Volume)   │
                            └────────────┬───────────────┘
                                         │
                                         ▼
                           [ Amazon RDS PostGIS (Private) ]
                           (Multi-AZ Subnet Group, KMS Encrypted)

─────────────────────────────────────────────────────────────────────────────────────────────
                             SECURITY, AUDITING & EVENT LAYER
─────────────────────────────────────────────────────────────────────────────────────────────
┌──────────────────┐  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  AWS CloudTrail  │  │  AWS GuardDuty  │  │ AWS Security Hub │  │ AWS Secrets Mgr  │
│ (API Audit Logs) │  │(Threat Detection│  │ (Posture & CIS)  │  │ (DB Creds + KMS) │
└────────┬─────────┘  └────────┬────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                    │                     │
         └─────────────────────┴─────────┬──────────┴─────────────────────┘
                                         ▼
                              [ Amazon EventBridge ]
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
   [ Weekly ETL Pipeline Cron ]                    [ SNS Alerting Topic ]
```

---

## 📁 Project Structure

```
CrownCorridor/
├── application/             # Application platform (SPA Web UI & FastAPI microservice)
│   ├── app/                 # Front-end SPA web application (index.html, portal.js, styles.css)
│   └── api/                 # Fast-Read API Microservice (main.py, search.py)
│
├── infrastructure/          # AWS Terraform Reference Architecture (>= 1.15.0, AWS ~> 6.56.0)
│   ├── main.tf, outputs.tf, variables.tf
│   ├── modules/             # Child modules (vpc, security, waf, cdn, auth, api_gateway, compute, database, secrets_ssm, events_alerting)
│   └── tests/               # Native Terraform test suite (.tftest.hcl)
│
├── security_framework/      # IaCSecBench Security Evaluation Engine
│   ├── engine/              # engine.py, comparative_eval.py
│   ├── policies/            # OPA / Rego policy definitions
│   └── tests/               # Framework unit tests
│
├── evaluation/              # Measurement harness (this is the pipeline that produces results)
│   ├── corpus.py            # Corpus admissibility: label, provider and validation checks
│   ├── run_baselines.py     # Executes each installed scanner; records raw output & latency
│   ├── normalize.py         # Maps native rule IDs onto the canonical control taxonomy
│   ├── control_map.json     # Native rule ID -> canonical control, with per-entry verified flag
│   ├── stats.py             # Clopper-Pearson, exact McNemar, Holm-Bonferroni, bootstrap, MCC
│   ├── analyze.py           # Aggregation; emits results/tables/*.tex and leaderboard/results.csv
│   ├── metrics.py           # Precision, Recall, Accuracy, F1, FPR, FNR calculation engine
│   ├── synthetic_guard.py   # One opt-in gate shared by every stage that fabricates numbers
│   └── score.py             # DEPRECATED: fabricates a leaderboard from assumed rates; gated
│
├── benchmark/               # Benchmark Datasets & Scenarios
│   ├── internal/            # IaCSecBench Controlled Benchmark (cases/, one dir per case)
│   ├── external/            # External collections. Each metadata.json DECLARES more
│   │   │                    # cases than there are configurations on disk; the gap is
│   │   │                    # reported, not hidden -- see results/corpus_report.json.
│   │   ├── terraform_registry/ # declares 50; modules/ is empty
│   │   ├── secureflag/      # declares 75; terraform/ is empty
│   │   └── cis_examples/    # declares 50; aws/ holds 4 usable configurations
│   └── golden_results/      # Golden baseline JSON outputs for Checkov, tfsec, OPA, IaCSecBench
│
├── pipeline/                # Zero-PII Data Pipeline & Validators
│   ├── fetch_sro.py         # SRO data fetcher with sanitize_and_anonymize_record() PII scrubbing
│   ├── validate_data.py     # Eight-section data integrity & zero-PII validator
│   ├── validate_iac.py      # IaC structure & CIS AWS Benchmark policy validator
│   └── tests/               # Pipeline unit tests
│
├── data/                    # AP & TS geographic datasets and property histories
│
├── leaderboard/             # Published Baseline Leaderboard
│   └── results.csv          # MEASURED leaderboard, generated by evaluation/analyze.py
│
├── docs/                    # Architectural & Framework Documentation
│   ├── taxonomy.md          # Canonical control taxonomy
│   ├── benchmark_protocol.md # Evaluation methodology & ground truth guidelines
│   └── framework/           # IaCSecBench docs (architecture.md, benchmark-methodology.md, metrics.md)
│
├── experiments/             # Experiment Reproducibility Package
│   ├── run_all.sh           # One-command experiment execution script
│   └── generate_charts.py   # Benchmark chart generator
│
└── results/                 # Measured outputs. See results/README.md.
    ├── run_manifest.json    # Authoritative record of a run: versions, env, latency samples
    ├── evaluation.json      # Confusion matrices, exact intervals, McNemar tests, caveats
    ├── corpus_report.json   # Admissibility per case; declared vs present counts
    ├── raw/<tool>/          # Unmodified scanner output; everything else derives from these
    ├── tables/              # Generated LaTeX tables consumed by paper/
    └── pre_opa_polarity_fix/ # Measured results before a disclosed policy correction
```

Nothing under `results/` is synthetic. The stages that fabricate metrics
(`evaluation/score.py`, `pipeline/run_experiments.py`,
`experiments/generate_charts.py`) refuse to run without
`IACSECBENCH_ALLOW_SYNTHETIC=1`, and their previous output has been deleted rather
than left where a reader would mistake it for a measurement.

---

## 💻 Running Locally

```bash
# Option 1: Serve web app from repo root
python3 -m http.server 8080

# Option 2: Start Fast-Read Search API microservice
pip install -r application/api/requirements.txt
uvicorn application.api.main:app --reload --port 8000

# Option 3: Run the IaCSecBench benchmark engine in Docker
docker build -t iacsecbench .
docker run iacsecbench                 # scans infrastructure/ by default
docker compose up                      # runs full experiment suite (pipeline/run_experiments.py)
```

Open **[http://localhost:8080/application/app/](http://localhost:8080/application/app/)** for the Web Portal and **[http://localhost:8000/docs](http://localhost:8000/docs)** for Interactive OpenAPI Docs.

## 🛠️ Repository Tooling Scripts

This repository includes helper scripts under `scripts/` for security, compliance, PR analysis, code quality, and combined review reporting.

```bash
python scripts/security_scanner.py . --severity high --json --output security_report.json
python scripts/compliance_checker.py . --framework soc2 --json --output compliance_report.json
python scripts/pr_analyzer.py . --base main --head feature-branch --json --output pr_report.json
python scripts/code_quality_checker.py . --language python --json --output quality_report.json
python scripts/review_report_generator.py . --format markdown --output review_report.md
```

> Note: these helper scripts use standard shell exit codes. `0` means the command completed successfully, while any non-zero exit code indicates an error or failure during script execution.

---

## 🧪 Development, Infrastructure & Native Testing

```bash
# Install Node dev dependencies (Prettier, ESLint, JSDoc)
npm install

# Run ESLint JavaScript code quality check
npm run lint

# Run Prettier code formatting check
npm run format:check

# Install Python dependencies & run data validators
pip install -r pipeline/requirements.txt -r application/api/requirements.txt
python pipeline/validate_data.py

# Run IaC & CIS AWS Benchmark Security Validator
python pipeline/validate_iac.py

# Run Evaluation Scoring Protocol & Leaderboard Export
python evaluation/score.py

# Run Reproducible IaC Benchmark Experiments
./experiments/run_all.sh

# Run full pytest test suite (62 tests: application/api, pipeline & security_framework)
.venv/bin/pytest -v

# Run Checkov
checkov -d infrastructure --framework terraform

# Native Terraform Tests (11 test suites with 100% coverage)
cd infrastructure
terraform fmt -check -recursive .
terraform init -backend=false
terraform validate
terraform test

# Run Pre-commit Hooks
pre-commit run --all-files

```
---

## 🔬 Open-Source IaC Security Benchmark Framework

Crown Corridor serves as the reference implementation for the **IaCSecBench Research Benchmark Framework**, a publication-grade evaluation suite designed to evaluate IaC security tools, OPA policies, and zero-PII/secret prevention across cloud repositories.

### Comparative Research Matrix

The matrix is generated, not written here — a table copied into a README cannot be
regenerated and becomes wrong without looking wrong. Measure it yourself:

```bash
experiments/run_baselines.sh    # writes leaderboard/results.csv + results/evaluation.json
```

Read the output with two facts in hand:

- **The reference implementation ranks last on this corpus.** Layer 1 is a
  repository-edge secret and PII scanner; the corpus is cloud misconfigurations.
  It is reported as measured, not adjusted to flatter the framework.
- **Latency reflects the host, not the tool.** Background load inflates the mean
  and roughly doubles the standard deviation. Measure on an idle machine.

For full setup, schemas, taxonomy, and reproducible experiment guides, see:

- 📖 [Benchmark Taxonomy](docs/taxonomy.md)
- 📜 [Evaluation Protocol & Methodology](docs/benchmark_protocol.md)
- 📊 [Leaderboard Dataset](leaderboard/results.csv)
- 📂 [Master Benchmark JSON Catalog](benchmark/benchmark.json)
- 🧪 [Reproducible Experiments Guide](docs/framework/reproducible_experiments.md)

---

## 🏷️ Semantic Versioning Model

Crown Corridor strictly follows this versioning strategy:

- 🟡 **`MINOR` (x.Y.0)** — **Data Updates**: Triggered whenever state datasets (`data/**`), property histories, or SRO records are refreshed/expanded.
- 🟢 **`PATCH` (x.y.Z)** — **Pipeline & Infrastructure Updates**: Triggered for data pipelines, validators, APIs, or CI toolchains (`pipeline/**`, `application/api/**`, `infrastructure/**`).
- 🔵 **`MAJOR` (X.0.0)** — **Web Application Updates**: Triggered for UI/UX frontend features, design changes, and portal functionality (`application/app/**`).

Releases are cut automatically by [`release-please.yml`](.github/workflows/release-please.yml) from Conventional Commit messages — see [CHANGELOG.md](CHANGELOG.md).

---

## 🔒 Privacy & Zero-PII Compliance

Crown Corridor adheres strictly to zero-PII privacy rules:

- **No Customer PII**: Customer personal names and personal identity numbers are strictly scrubbed from dataset files.
- **Anonymized Classifications**: Transactions exclusively use role-based classifications (`Private Individual Owner`, `Commercial Property Developer`, `Institutional Realty Fund`).
- **Automated CI PII & Secret Guard**: Both `pipeline/validate_data.py` and `pipeline/validate_iac.py` inspect all datasets and infrastructure files on pull requests to block personal data or secret commits.

---

## 🌐 Data Sources & Documentation Hosting

- **Geographic Data**: Sourced from the **Government of India's [Local Government Directory (LGD)](https://lgdirectory.gov.in)** via [data.gov.in](https://data.gov.in).
- **Documentation Website**: Deployed to GitHub Pages under the **`/docs`** path.

---

## 📄 License

Code: [LICENSE](LICENSE)
