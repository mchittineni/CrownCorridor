# 🚀 Application Directory — API & Web Portal Architecture

## 📋 Directory Overview

The `application/` directory houses the core application services for the **Crown Corridor / IaCSecBench** platform, containing both the RESTful API backend and the static web UI portal.

---

## 📁 Directory Structure & Key Files

```text
application/
├── api/                   # FastAPI Backend Service
│   ├── main.py            # API Entry Point, Route Declarations & Pydantic Models
│   ├── search.py          # Typesense Client Wrapper
│   ├── Dockerfile         # Container Image Definition
│   └── tests/             # Pytest Unit & Integration Test Suite for API Endpoints
└── app/                   # Web Portal Frontend Application
    ├── index.html         # Single Page Web App Entry Point
    ├── portal.js          # Client-side Logic (ES2021 Vanilla JS)
    └── styles.css         # UI Design System & Glassmorphic CSS Styling
```

---

## ⚙️ Key Components Explained

### 1. API Service (`application/api/`)

- **`main.py`**: Configures the FastAPI application instance, CORS middleware, health check endpoints (`/health`), and spatial/property search API routes (`/api/v1/search`, `/api/v1/properties/{id}`).
- **`search.py`**: Typesense client wrapper providing the search-index interface and its
  fallback path when the index is unavailable.
- **`tests/test_api.py`**: Pytest suite covering API endpoints, error handling (503
  fallbacks), and hierarchy parameter scoping. Measured coverage is **92%** overall
  (`main.py` 91%, `search.py` 85%) — reproduce with
  `pytest application/api/tests/ --cov=application/api`.

There are no `schemas.py` or `services.py` modules. An earlier version of this file
documented both; the Pydantic request/response models are declared inline in `main.py`,
and the search-index interface lives in `search.py`. The same revision claimed 100%
test coverage, which was never measured and is not the case.

### 2. Web Portal UI (`application/app/`)

- **`index.html`**: HTML5 semantic structure for the geospatial search interface, filter sidebars, and property detail modals.
- **`portal.js`**: Vanilla JS application logic managing state, asynchronous API fetches, interactive filtering, and dynamic DOM rendering. Fully annotated with complete JSDoc docstrings (`/** */`).
- **`styles.css`**: CSS styling implementation supporting glassmorphic design aesthetics, responsive grid layouts, dynamic dark/light mode CSS variables, and micro-animations.

---

## 🔗 Related Knowledge Base Links

- [[Project-Structure|📐 View Project Architecture]]
- [[Modules/application_api_main_py|API Entry Point Module]]
- [[Modules/application_app_portal_js|Web Portal Frontend Logic]]
