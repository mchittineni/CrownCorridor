# ⚙️ Pipeline Directory — Data Validation & Security Execution Engine

## 📋 Directory Overview

The `pipeline/` directory forms the core execution engine of **IaCSecBench**, containing repository data sanitizers, IaC security validators, experiment runners, and Obsidian vault synchronization tools.

---

## 📁 Directory Structure & Key Files

```text
pipeline/
├── validate_data.py       # Layer 1: Data Integrity & PII Sanitization Checker
├── validate_iac.py        # Layer 2 & 3: IaC HCL & Policy Compliance Checker
├── fetch_sro.py           # SRO Data Ingestion & ETL Fetcher
├── index_to_typesense.py  # Typesense Search Indexing Engine
├── run_experiments.py     # Experiment Execution & Scoring Harness
├── sync_to_obsidian.py    # Obsidian Vault Daily Notes & Knowledge Base Sync
└── tests/                 # Unit & Integration Test Suite for Pipeline Scripts
```

---

## ⚙️ Key Components Explained

### 1. Repository-Edge Data Validation (`validate_data.py`)

- Implements **Layer 1** security checks:
  - Schema verification across geospatial data (`regions.json`, `villages.json`, `coords.json`, `districts.geojson`).
  - **Zero-PII Privacy Rule:** Regex-based scanner ensuring customer names, phone numbers, and individual identities are never committed to repositories.
  - Returns `ALL CHECKS PASSED ✓` upon successful verification.

### 2. IaC Security Validator (`validate_iac.py`)

- Implements **Layer 2 & 3** checks:
  - Validates HCL syntax and formatting (`terraform fmt -check`).
  - Verifies CIS AWS Foundations Benchmark policies.
  - Scans for hardcoded AWS secret keys, tokens, and insecure default configurations.

### 3. Obsidian Knowledge Base Synchronizer (`sync_to_obsidian.py`)

- Automated synchronization tool extracting repository commits, AST code structures, and research papers into Obsidian markdown files:
  - **`Daily/`**: Generates daily commit notes with Mermaid workflow flowcharts.
  - **`Modules/`**: Generates individual notes for every workspace markdown file.
  - **`Research/`**: Generates paper draft workspace notes and statistical LaTeX matrices.
  - **`Project-Structure.md`**: Generates a complete codebase architecture map.

---

## 🔗 Related Knowledge Base Links

- [[Research/Threat-Model-STRIDE|🛡️ Threat Model & STRIDE Matrix]]
- [[Project-Structure|📐 View Project Architecture]]
