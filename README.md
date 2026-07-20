# Crown Corridor

> A next-generation real estate and property discovery portal for Andhra Pradesh & Telangana.  
> Features verified listings, interactive geospatial maps, state-modular SRO property sale histories, CAGR analytics, nearby infrastructure scoring, zero-PII privacy compliance, and strict code quality standards.

[![CI](https://github.com/mchittineni/CrownCorridor/actions/workflows/ci.yml/badge.svg)](https://github.com/mchittineni/CrownCorridor/actions/workflows/ci.yml)
[![Deploy](https://github.com/mchittineni/CrownCorridor/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/mchittineni/CrownCorridor/actions/workflows/deploy-pages.yml)

---

## ✨ Features

| Feature                        | Description                                                                                      |
| ------------------------------ | ------------------------------------------------------------------------------------------------ |
| 🔴 **Live SRO Feed**           | Real-time property registration ticker with pause/resume and speed controls                      |
| 🚗 **Search by Commute**       | Filter properties by driving time to workplace hubs (HITECH City, Financial District, Amaravati) |
| 📈 **Regional Market Trends**  | Time-series price trajectory charts (2016-2026) and top appreciating localities leaderboard      |
| 🔍 **Global Smart Search**     | Persistent header bar with instant autocomplete for properties, listings, and districts          |
| ⚖️ **Property Comparison**     | Side-by-side spec comparison modal for up to 3 properties (Valuation, CAGR, Rate/SqFt, Metro)    |
| 🏰 **Property Sale History**   | State-modular chronological registry audit since construction with price growth CAGR analytics   |
| 🖨️ **Valuation Audit Report**  | One-click printable PDF/audit summary with transaction logs and infrastructure scores            |
| 📍 **Infrastructure Explorer** | Nearby schools, hospitals, metro/railway stations, parks with drive times and ratings            |
| 🎛️ **Visual Filter Presets**   | Quick filter pills (_"Near Metro"_, _"High CAGR > 10%"_, _"Luxury Villas"_, _"AP"_, _"TS"_)      |
| 🧭 **GPS "Locate Me"**         | Geolocation finder calculating real-time distance from user to properties and POIs               |
| 🔒 **Zero-PII Compliance**     | Strict privacy protections — no customer names or personal data stored (automated CI check)      |
| ☀️ **Theme Switcher**          | Glassmorphic Dark Mode and Light Mode theme toggle                                               |
| 🧮 **Stamp Duty Calculator**   | Registration tax breakdown (AP 7.5%, TS 6.0%)                                                    |
| 📔 **Guide Value Directory**   | Official SRO government guidance valuations by district & mandal                                 |
| 💻 **Developer API Sandbox**   | Queryable JSON sandbox and webhook alert configuration                                           |

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
├── pipeline/                # Python Data Pipeline & Validation
│   ├── fetch_sro.py         # SRO data fetcher & state-modular history aggregator (--generate-history)
│   ├── index_to_typesense.py# Syncs property records to Typesense index (--dry-run)
│   ├── validate_data.py     # Data integrity & zero-PII validator
│   ├── requirements.txt     # Python dependencies
│   └── tests/               # pytest test suite (includes test_api.py)
│
├── docs/                    # Hosted Documentation Website (/docs path)
│   ├── index.md             # Architecture overview & documentation hub
│   ├── user-guide.md        # Step-by-step non-technical user guide
│   └── api/                 # JSDoc generated API documentation
│
└── .github/
    ├── ISSUE_TEMPLATE/      # Structured issue forms (bug, feature, config, data correction)
    ├── PULL_REQUEST_TEMPLATE.md # Pull request checklist & guide
    ├── dependabot.yml       # Weekly dependency update rules (actions, npm, pip)
    ├── actions/             # Shared composite GitHub Actions
    └── workflows/           # CI/CD workflows with SHA-pinned actions
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

## 🧪 Development, Code Quality & Testing

```bash
# Install Node dev dependencies (Prettier, ESLint, JSDoc)
npm install

# Run ESLint JavaScript code quality check
npm run lint

# Run Prettier code formatting check
npm run format:check

# Format code automatically
npm run format

# Install Python dependencies & run data validator
pip install -r pipeline/requirements.txt -r api/requirements.txt
python pipeline/validate_data.py

# Run Typesense index dry-run
python pipeline/index_to_typesense.py --dry-run

# Run pytest test suite
.venv/bin/pytest pipeline/tests/ -v
```

---

## 🔒 Privacy & Zero-PII Compliance

Crown Corridor adheres strictly to zero-PII privacy rules:

- **No Customer PII**: Customer personal names and personal identity numbers are strictly scrubbed from dataset files.
- **Anonymized Classifications**: Transactions exclusively use role-based classifications (`Private Individual Owner`, `Commercial Property Developer`, `Institutional Realty Fund`).
- **Automated CI PII Guard**: `pipeline/validate_data.py` inspects all datasets on pull requests to block personal data commits.

---

## 🌐 Data Sources & Documentation Hosting

- **Geographic Data**: Sourced from the **Government of India's [Local Government Directory (LGD)](https://lgdirectory.gov.in)** via [data.gov.in](https://data.gov.in).
- **Documentation Website**: Deployed to GitHub Pages under the **`/docs`** path.

---

## 📄 License

Code: [LICENSE](LICENSE)
