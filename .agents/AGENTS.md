# IaCSecBench — Workspace Coding & Quality Rules

## 1. Code Formatting & Style Standards

- **JavaScript (`application/app/portal.js`)**:
  - Standard ES2021 syntax without build step/bundler.
  - Indentation: 2 spaces. Single quotes for strings.
  - Every public method MUST include a complete JSDoc `/** */` docstring with `@param` and `@returns`.
  - Enforce strict equality (`===` / `!==`).
- **CSS (`application/app/styles.css`)**:
  - Use custom CSS variables (`--var-name`) defined in `:root`.
  - Maintain glassmorphic dark and light theme consistency.
- **Python (`pipeline/`)**:
  - Python 3.11+ compliance following PEP 8.
  - Line length: 100 characters.
  - 4-space indentation. Functions must include Google-style docstrings.
  - Scripts must include `if __name__ == "__main__":` entry points.

## 2. Zero-PII Privacy Compliance

- **Strict Privacy Rule**: NEVER store customer personal names, personal phone numbers, or individual identities in dataset files or code.
- Transactions must strictly use anonymized role classifications (`Private Individual Owner`, `Commercial Property Developer`, `Institutional Realty Fund`).
- Run `python pipeline/validate_data.py` on every data modification to verify zero-PII compliance.

## 3. Testing & Validation Workflow

- Before committing or completing any task:
  1. Run `python3 pipeline/validate_data.py` (Must print `ALL CHECKS PASSED ✓`).
  2. Run `.venv/bin/pytest -v` (All 62 tests across `application/api/tests/`, `pipeline/tests/`, and `security_framework/tests/` MUST pass).
  3. Run `npm run docs` / `npx jsdoc -c jsdoc.json --pedantic` to verify docs build.
