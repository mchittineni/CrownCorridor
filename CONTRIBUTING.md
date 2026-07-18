# Contributing to Crown Corridor

Thank you for your interest in improving Crown Corridor! 🇮🇳🏙️

Crown Corridor is a real-time real estate monitoring portal for Andhra Pradesh & Telangana. Contributions that improve the portal UI, data pipeline, geographic datasets, or CI/CD workflows are all welcome.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Getting Started Locally](#getting-started-locally)
3. [Running Tests](#running-tests)
4. [Contribution Areas](#contribution-areas)
5. [Branch & Commit Conventions](#branch--commit-conventions)
6. [Pull Request Guidelines](#pull-request-guidelines)
7. [Code Style](#code-style)

---

## Project Structure

```
CrownCorridor/
├── app/
│   ├── index.html      # Dashboard entry point (tabbed SPA)
│   ├── portal.js       # All portal logic — maps, charts, listings, calculator, API console
│   └── styles.css      # Dark glassmorphism design system
│
├── data/
│   ├── andhra_pradesh/ # regions.json, villages.json, coords.json, districts.geojson, …
│   └── telangana/      # same structure
│
├── pipeline/
│   ├── validate_data.py     # Data integrity checker — run on every PR
│   ├── fetch_sro.py         # SRO registration data fetcher scaffold
│   ├── requirements.txt     # pip dependencies (requests, pytest)
│   └── tests/
│       └── test_validate.py # pytest suite (23 cases)
│
├── docs/
│   └── index.md        # Architecture overview and navigation hub
│
└── .github/
    ├── actions/        # Shared composite steps (setup-pipeline, datagov-fetch, …)
    └── workflows/      # CI, deploy-pages, update-data, release, docs
```

---

## Getting Started Locally

### Prerequisites

- Python 3.11+ (for pipeline validation)
- A modern browser (Chrome/Firefox/Safari)

### Serving the portal

The portal loads geographic data via `fetch()`, so you must serve it from a local
HTTP server to avoid CORS issues:

```bash
# From the repo root
python3 -m http.server 8080
```

Open **[http://localhost:8080/app/](http://localhost:8080/app/)**.

### Installing Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r pipeline/requirements.txt
```

---

## Running Tests

```bash
# Standalone data integrity check (human-readable output)
python pipeline/validate_data.py

# Full pytest suite with verbose output
pytest pipeline/tests/ -v
```

The CI workflow (`ci.yml`) runs both automatically on every pull request.

---

## Contribution Areas

| Area | What to look for |
|------|-----------------|
| **Portal UI** | Improvements to `app/portal.js` or `app/styles.css` — maps, charts, listings, calculator |
| **Data pipeline** | `pipeline/validate_data.py` checks, `fetch_sro.py` SRO integration once APIs become available |
| **Geographic data** | Corrections to `data/andhra_pradesh/` or `data/telangana/` sourced from the LGD |
| **CI/CD** | Workflow improvements in `.github/workflows/` or `.github/actions/` |
| **Documentation** | `README.md`, `docs/`, or inline comments in `app/portal.js` |

---

## Branch & Commit Conventions

### Branch names

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/<description>` | `feat/live-sro-websocket` |
| Bug fix | `fix/<description>` | `fix/calculator-ap-rate` |
| Documentation | `docs/<description>` | `docs/api-reference` |
| Chore | `chore/<description>` | `chore/update-deps` |

Branch off `develop` (not `main`). `main` is for releases only.

### Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add real-time WebSocket SRO feed
fix: correct Telangana stamp duty rate to 4%
docs: add JSDoc to updateCadastralVectorLayer
chore: bump actions/setup-node to v7
```

---

## Pull Request Guidelines

1. **Open PRs against `develop`**, not `main`.
2. Describe **what** changed and **why** in the PR body.
3. Ensure **all CI checks pass** (data validator + pytest + JSDoc build).
4. Keep PRs focused — one logical change per PR.
5. Reference any related issue with `Closes #<number>`.

---

## Code Style

### JavaScript (`app/portal.js`)

- Vanilla ES2020 (no build step, no bundler).
- All public methods must have a JSDoc `/** */` block with `@param` and `@returns`.
- Use `const`/`let`, arrow functions, and template literals throughout.
- No external runtime dependencies beyond what is loaded in `app/index.html`.

### CSS (`app/styles.css`)

- Vanilla CSS with custom properties (`--var-name`) for all design tokens.
- Follow the existing glassmorphism dark-theme conventions.
- No preprocessors (no Sass/Less).

### Python (`pipeline/`)

- Python 3.11+, PEP 8 style.
- All functions must have docstrings (Google style).
- Scripts must have a `if __name__ == "__main__"` guard.

### YAML (`.github/`)

- 2-space indent.
- Every `job` and key `step` must have a `name:` field.
- Pin third-party actions to a major version tag (e.g. `actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7`).
