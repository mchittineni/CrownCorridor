# Crown Corridor

> **Real Estate at Your Fingertips** — A next-generation property discovery portal for Andhra Pradesh & Telangana.  
> Features verified listings, interactive geospatial maps, state-modular SRO property sale histories, CAGR analytics, nearby infrastructure scoring, zero-PII privacy compliance, reusable Terraform AWS infrastructure, and strict code quality standards.

[![CI](https://github.com/mchittineni/CrownCorridor/actions/workflows/ci.yml/badge.svg)](https://github.com/mchittineni/CrownCorridor/actions/workflows/ci.yml)
[![Infra CI](https://github.com/mchittineni/CrownCorridor/actions/workflows/infra-ci.yml/badge.svg)](https://github.com/mchittineni/CrownCorridor/actions/workflows/infra-ci.yml)
[![Deploy](https://github.com/mchittineni/CrownCorridor/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/mchittineni/CrownCorridor/actions/workflows/deploy-pages.yml)

---

## ✨ Features

| Feature                             | Description                                                                                                |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 🔴 **Live SRO Feed**                | Real-time property registration ticker with pause/resume and speed controls                                |
| 🚗 **Search by Commute**            | Filter properties by driving time to workplace hubs (HITECH City, Financial District, Amaravati)           |
| 📈 **Regional Market Trends**       | Time-series price trajectory charts (2016-2026) and top appreciating localities leaderboard                |
| 🔍 **Global Smart Search**          | Persistent header bar with instant autocomplete for properties, listings, and districts                    |
| ⚖️ **Property Comparison**          | Side-by-side spec comparison modal for up to 3 properties (Valuation, CAGR, Rate/SqFt, Metro)              |
| 🏰 **Property Sale History**        | State-modular chronological registry audit since construction with price growth CAGR analytics             |
| 🖨️ **Valuation Audit Report**       | One-click printable PDF/audit summary with transaction logs and infrastructure scores                      |
| 📍 **Infrastructure Explorer**      | Nearby schools, hospitals, metro/railway stations, parks with drive times and ratings                      |
| 🎛️ **Visual Filter Presets**        | Quick filter pills (_"Near Metro"_, _"High CAGR > 10%"_, _"Luxury Villas"_, _"AP"_, _"TS"_)                |
| 🔒 **Zero-PII Compliance**          | Strict privacy protections — no customer names or personal data stored (automated CI check)                |
| 🏗️ **AWS Terraform Infrastructure** | Production-ready modular Terraform (>= 1.15.0, AWS ~> 6.56.0) with WAF, API Gateway, Fargate & PostGIS     |
| 🛡️ **CIS AWS Benchmark Security**   | OPA / Rego policy engine, VPC Flow Logs, S3 TLS-Only, ALB Header Dropping, and native `.tftest.hcl` suites |
| 📐 **Draw.io AWS Architecture**     | Full Draw.io XML diagram using official AWS Architecture Icons (`docs/architecture.drawio`)                |

---

## 🏛️ Infrastructure Architecture Diagram

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
├── app/                     # Front-end web application (SPA)
│   ├── index.html           # Dashboard entry point
│   ├── portal.js            # Main application logic (maps, API search & fallback, comparison)
│   └── styles.css           # Glassmorphism dark & light theme design system
│
├── api/                     # Fast-Read API Microservice (FastAPI)
│   ├── main.py              # Async FastAPI search, health, and property endpoints
│   ├── search.py            # Typesense connection wrapper & query builder
│   └── requirements.txt     # API microservice dependencies
│
├── data/                    # State-Modular Datasets
│   ├── andhra_pradesh/      # AP regions, villages, coords, GeoJSON, property_history.json
│   ├── telangana/           # TS regions, villages, coords, GeoJSON, property_history.json
│   └── sro_feed/            # Daily SRO registration archives
│
├── pipeline/                # Python Data Pipeline, Validation & IaC Security
│   ├── fetch_sro.py         # SRO data fetcher & state-modular history aggregator (--generate-history)
│   ├── index_to_typesense.py# Syncs property records to Typesense index (--dry-run)
│   ├── validate_data.py     # Data integrity & zero-PII validator
│   ├── validate_iac.py      # Infrastructure as Code, HCL syntax & CIS AWS Benchmark validator
│   ├── requirements.txt     # Python dependencies
│   └── tests/               # pytest test suite (includes test_api.py & test_validate_iac.py)
│
├── terraform/               # Production-Ready AWS Terraform Infrastructure (>= 1.15.0, AWS ~> 6.56.0)
│   ├── main.tf              # Master module orchestrator
│   ├── providers.tf         # HashiCorp AWS provider (~> 6.56.0) & local offline testing configuration
│   ├── variables.tf         # Global input variables
│   ├── outputs.tf           # Endpoints, CDN URLs, User Pool IDs, DB connections
│   ├── terraform.tfvars.example # Sample environment variable settings
│   ├── graph.dot / graph.png# Terraform visual execution plan graph
│   ├── architecture.drawio  # Official AWS Icons Draw.io XML diagram file
│   ├── policies/            # Open Policy Agent (OPA) Rego CIS AWS Foundations Benchmark policies
│   ├── tests/               # Centralized Native Terraform test directory (11 .tftest.hcl suites, 100% coverage)
│   └── modules/             # Reusable child modules (vpc, security, waf, cdn, auth, api_gateway, compute, database, secrets_ssm, events_alerting)
│
├── docs/                    # Hosted Documentation Website (/docs path)
│   ├── index.md             # Architecture overview & documentation hub
│   ├── user-guide.md        # Step-by-step non-technical user guide
│   ├── graph.png / graph.svg# Visual Terraform execution plan graph
│   ├── architecture.drawio  # Official AWS Icons Draw.io XML diagram file
│   └── api/                 # JSDoc generated API documentation
│
└── .github/
    ├── ISSUE_TEMPLATE/      # Structured issue forms (bug, feature, config, data correction)
    ├── PULL_REQUEST_TEMPLATE.md # Pull request checklist & guide
    ├── dependabot.yml       # Weekly dependency update rules (actions, npm, pip)
    ├── actions/             # Shared composite GitHub Actions
    └── workflows/           # CI/CD workflows (ci.yml, infra-ci.yml, deploy-pages.yml, etc.)
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

# Run pytest test suite (44 test cases)
.venv/bin/pytest pipeline/tests/ -v

# Native Terraform Tests (11 test suites with 100% coverage)
cd terraform
terraform fmt -check -recursive .
terraform init -backend=false
terraform validate
terraform test
```

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
