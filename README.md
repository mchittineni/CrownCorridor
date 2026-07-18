# Crown Corridor

> A next-generation real estate and property discovery portal for Andhra Pradesh & Telangana.  
> Features verified listings, interactive geospatial maps, government guidance value estimation, and real-time SRO transaction analytics.

[![CI](https://github.com/mchittineni/CrownCorridor/actions/workflows/ci.yml/badge.svg)](https://github.com/mchittineni/CrownCorridor/actions/workflows/ci.yml)
[![Deploy](https://github.com/mchittineni/CrownCorridor/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/mchittineni/CrownCorridor/actions/workflows/deploy-pages.yml)

---

## Features

| Feature | Description |
|---------|-------------|
| 🔴 **Live SRO Feed** | Real-time property registration ticker across all Sub-Registrar Offices in AP & TS |
| ✅ **Verified Listings** | Geospatially verified properties for sale/rent with one-click agent contact |
| 🗺 **Boundary Explorer** | Village-level LGD coordinate drill-down with PMTiles vector cadastral overlays |
| 🧮 **Stamp Duty Calculator** | Accurate registration tax breakdown (AP 7.5%, TS 6.0%) |
| 📔 **Guide Value Directory** | Official SRO government guidance valuations by district & mandal |
| 💻 **Developer API Console** | Queryable JSON sandbox and webhook alert configuration |

---

## Project Structure

```
CrownCorridor/
├── app/                     # Front-end web application
│   ├── index.html           # Dashboard entry point
│   ├── portal.js            # Portal logic — maps, charts, listings, API
│   └── styles.css           # Design system (glassmorphism dark-theme)
│
├── data/                    # Geographic reference datasets (LGD)
│   ├── andhra_pradesh/      # regions, villages, coords, GeoJSON boundaries
│   └── telangana/           # regions, villages, coords, GeoJSON boundaries
│
├── pipeline/                # Lean AP/TS data pipeline
│   ├── fetch_sro.py         # SRO registration data fetcher (exit-75 skip contract)
│   ├── validate_data.py     # Data integrity validator (runs in CI)
│   ├── requirements.txt     # requests, pytest
│   └── tests/
│       └── test_validate.py # pytest suite
│
├── docs/
│   └── cadastral-hosting.md # R2 cadastral PMTile hosting reference
│
└── .github/
    ├── actions/             # Shared composite steps
    │   ├── setup-pipeline/
    │   ├── datagov-fetch/
    │   ├── publish-data-branch/
    │   └── overlay-data-branches/
    └── workflows/
        ├── ci.yml           # PR tests (data validity + pytest)
        ├── deploy-pages.yml # GitHub Pages deployment
        ├── update-data.yml  # Weekly SRO data refresh → reviewed PR
        ├── release.yml      # Versioned release with data archives
        ├── publish-blog.yml # dev.to article on release
        └── docs.yml         # JSDoc build-check on PRs
```

---

## Running Locally

```bash
# Serve from the repo root (data/ must be at the same level as app/)
python3 -m http.server 8080
```

Open **[http://localhost:8080/app/](http://localhost:8080/app/)**.

---

## Running Tests

```bash
pip install -r pipeline/requirements.txt
python pipeline/validate_data.py      # standalone data integrity check
pytest pipeline/tests/ -v             # full test suite
```

---

## Data Sources

Geographic data is sourced from the **Government of India's [Local Government Directory (LGD)](https://lgdirectory.gov.in)** via the [Open Government Data platform](https://data.gov.in).

Data may lag recent administrative reorganisations — verify critical records directly against the LGD portal.

---

## GitHub Pages Deployment

GitHub Pages is deployed automatically on every push to `main` via the `deploy-pages.yml` workflow.  
The deployment assembles `_site/` containing `app/` + `data/` overlays so relative paths resolve correctly.

To enable Pages for the first time:
1. Go to **Settings → Pages** in the repository.
2. Set **Source** to `GitHub Actions`.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

Data: [DATA_LICENSE.md](DATA_LICENSE.md) · Code: [LICENSE](LICENSE)
