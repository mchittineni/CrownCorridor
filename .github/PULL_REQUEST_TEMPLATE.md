# Pull Request — Crown Corridor

## Summary of Changes

Provide a clear description of what this PR introduces or fixes.

-

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change fixing an issue)
- [ ] ✨ New feature (non-breaking change adding functionality)
- [ ] 🗺️ Data update (corrections or updates to AP/TS datasets)
- [ ] ⚙️ Maintenance / Config (workflow, linter, dependencies)
- [ ] 📚 Documentation update

## Related Issues

Closes #

## Pre-Commit Verification Checklist

Before submitting this PR, verify that all quality checks pass locally:

- [ ] `npm run lint` (ESLint clean with 0 errors)
- [ ] `npm run format:check` (Prettier code style compliant)
- [ ] `.venv/bin/ruff check .` && `.venv/bin/ruff format --check .` (Ruff clean)
- [ ] `python3 pipeline/validate_data.py` (Must print `ALL CHECKS PASSED ✓` with Zero PII)
- [ ] `.venv/bin/pytest pipeline/tests/ -v` (All 36 unit tests passing)
- [ ] `npm run docs` (JSDoc API docs build cleanly)

## Testing Instructions

Explain how reviewers can test your changes locally:

1. `python3 -m http.server 8080`
2. Open `http://localhost:8080/app/`
3. Test feature / fix...
