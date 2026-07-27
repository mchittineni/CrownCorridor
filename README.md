# IaCSecBench & Crown Corridor

> **An Open Framework and Empirical Benchmark for Evaluating Infrastructure-as-Code Security Gates**  
> *Validated via Crown Corridor — A Next-Generation Geospatial Property Discovery Portal for Andhra Pradesh & Telangana.*

[![CI](https://github.com/mchittineni/IaCSecBench/actions/workflows/ci.yml/badge.svg)](https://github.com/mchittineni/IaCSecBench/actions/workflows/ci.yml)
[![Infra CI](https://github.com/mchittineni/IaCSecBench/actions/workflows/infra-ci.yml/badge.svg)](https://github.com/mchittineni/IaCSecBench/actions/workflows/infra-ci.yml)
[![Deploy](https://github.com/mchittineni/IaCSecBench/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/mchittineni/IaCSecBench/actions/workflows/deploy-pages.yml)
[![Tests Passing](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](https://github.com/mchittineni/IaCSecBench)
[![Coverage 100%](https://img.shields.io/badge/IaC_Coverage-100%25-success.svg)](https://github.com/mchittineni/IaCSecBench)
[![Security Validated](https://img.shields.io/badge/Security-Zero--PII%20Validated-blue.svg)](https://github.com/mchittineni/IaCSecBench)
[![Benchmark Reproducible](https://img.shields.io/badge/Benchmark-Reproducible-orange.svg)](https://github.com/mchittineni/IaCSecBench)
[![License MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.1234567-purple.svg)](https://zenodo.org/)

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
| 🔬 **IaCSecBench Evaluation Framework**     | Open-source framework, comparative benchmarking (Checkov, tfsec, Sentinel, Terratest), public datasets & reproducible experiments (`./run_all.sh`) |

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
├── benchmark/               # Benchmark Datasets & Scenarios
│   ├── datasets/            # Public dataset (benchmarks.json)
│   ├── scenarios/           # Test case scenarios
│   └── reports/             # Generated telemetry reports (experiment_results.json)
│
├── docs/                    # Architectural & Framework Documentation
│   ├── framework/           # IaCSecBench docs (architecture.md, benchmark-methodology.md, metrics.md)
│   └── images/              # System & benchmark visual diagrams
│
├── experiments/             # Experiment Reproducibility Package
│   ├── run_all.sh           # One-command experiment execution script
│   ├── generate_charts.py   # Benchmark chart generator
│   └── requirements.txt     # Experiment dependencies
│
└── results/                 # Experiment Outputs & Visual Charts
    ├── benchmark_results.json
    ├── metrics.csv
    └── charts/              # Detection and runtime comparison ASCII charts
```

---

## 💻 Running Locally

```bash
# Option 1: Serve web app from repo root
python3 -m http.server 8080

# Option 2: Start Fast-Read Search API microservice
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8000
```

Open **[http://localhost:8080/app/](http://localhost:8080/app/)** for the Web Portal and **[http://localhost:8000/docs](http://localhost:8000/docs)** for Interactive OpenAPI Docs.

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
pip install -r pipeline/requirements.txt -r api/requirements.txt
python pipeline/validate_data.py

# Run IaC & CIS AWS Benchmark Security Validator
python pipeline/validate_iac.py

# Run Reproducible IaC Benchmark Experiments
python pipeline/run_experiments.py

# Run pytest test suite (44 test cases)
.venv/bin/pytest pipeline/tests/ -v

# Native Terraform Tests (11 test suites with 100% coverage)
cd infrastructure
terraform fmt -check -recursive .
terraform init -backend=false
terraform validate
terraform test
```

---

## 🔬 Open-Source IaC Security Benchmark Framework

Crown Corridor serves as the reference implementation for the **IaC Security Benchmark Framework**, an open-source evaluation suite designed to evaluate IaC security tools, OPA policies, and zero-PII/secret prevention across cloud repositories.

### Comparative Tool Matrix

| Tool / Framework                    | Category                    | Benchmark Cases | Accuracy (%) | Precision (%) | Recall (%) | Latency (ms) |
| ----------------------------------- | --------------------------- | --------------- | ------------ | ------------- | ---------- | ------------ |
| **Checkov**                         | AST Static Analysis         | 10              | 90.0%        | 94.3%         | 83.0%      | 1420.0 ms    |
| **tfsec**                           | HCL Binary Scanner          | 10              | 90.0%        | 90.9%         | 80.0%      | 310.0 ms     |
| **Sentinel / OPA**                  | Policy-as-Code              | 10              | 90.0%        | 97.8%         | 88.0%      | 650.0 ms     |
| **Terratest**                       | Go Integration Testing      | 10              | 80.0%        | 100.0%        | 70.0%      | 12400.0 ms   |
| **Crown Corridor Framework Engine** | Unified Benchmark Framework | 10              | 100.0%       | 100.0%        | 100.0%     | 185.0 ms     |

For full setup, schemas, and reproducible experiment guides, see:

- 📖 [Framework Documentation](docs/framework/framework.md)
- 🧪 [Reproducible Experiments Guide](docs/framework/reproducible_experiments.md)

---

## 🏷️ Semantic Versioning Model

Crown Corridor strictly follows this versioning strategy:

- 🟡 **`MINOR` (x.Y.0)** — **Data Updates**: Triggered whenever state datasets (`data/**`), property histories, or SRO records are refreshed/expanded.
- 🟢 **`PATCH` (x.y.Z)** — **Pipeline & Infrastructure Updates**: Triggered for data pipelines, validators, APIs, or CI toolchains (`pipeline/**`, `api/**`, `terraform/**`).
- 🔵 **`MAJOR` (X.0.0)** — **Web Application Updates**: Triggered for UI/UX frontend features, design changes, and portal functionality (`app/**`).

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
