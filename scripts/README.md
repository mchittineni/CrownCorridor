# 🛠️ Scripts Directory — Code Quality & Compliance Utilities

## 📋 Directory Overview

The `scripts/` directory contains developer tools, pre-commit hooks, and compliance utilities used to maintain code quality, styling standards, and documentation verification across the project.

---

## 📁 Directory Structure & Key Files

```text
scripts/
├── check_compliance.py    # Pre-commit Compliance & Style Standard Verification
└── generate_docs.sh       # Automated JSDoc API Documentation Builder
```

---

## ⚙️ Key Components Explained

### 1. Code Quality Checker (`check_compliance.py`)
- Enforces PEP 8 standards (100-character line length limit, Google-style docstrings for Python).
- Validates ES2021 JavaScript formatting rules and JSDoc requirements in `application/app/portal.js`.
- Verifies Zero-PII compliance across modified data files.

### 2. Documentation Generator (`generate_docs.sh`)
- Builds JSDoc HTML documentation using `npx jsdoc -c jsdoc.json --pedantic`.

---

## 🔗 Related Knowledge Base Links
- [[Project-Structure|📐 View Project Architecture]]
