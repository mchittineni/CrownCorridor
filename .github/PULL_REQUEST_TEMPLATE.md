# Pull Request — Crown Corridor & IaCSecBench

## Summary of Changes

Provide a clear description of what this PR introduces or fixes.

-

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change fixing an issue)
- [ ] ✨ New feature (non-breaking change adding functionality)
- [ ] 🔬 IaCSecBench Benchmark Framework (security engine, policy, or scenario addition)
- [ ] 🗺️ Data update (corrections or updates to AP/TS datasets)
- [ ] ⚙️ Maintenance / Config (workflow, linter, dependencies, Docker)
- [ ] 📚 Documentation update

## Related Issues

Closes #

## Pre-Commit Verification Checklist

Before submitting this PR, verify that all quality checks pass locally:

- [ ] `npm run lint` (ESLint clean with 0 errors)
- [ ] `npm run format:check` (Prettier code style compliant)
- [ ] `.venv/bin/ruff check .` && `.venv/bin/ruff format --check .` (Ruff clean)
- [ ] `python3 pipeline/validate_data.py` (Must print `ALL CHECKS PASSED ✓` with Zero PII)
- [ ] `python3 pipeline/validate_iac.py` (Must print `ALL IAC CHECKS & POLICIES PASSED ✓`)
- [ ] `.venv/bin/pytest security_framework/tests/ pipeline/tests/ -v --cov=security_framework` (All 51 unit tests passing with 93%+ coverage)
- [ ] `./experiments/run_all.sh` (One-command reproducible experiment suite completes successfully)
- [ ] `npm run docs` (JSDoc API docs build cleanly)

## Testing Instructions

Explain how reviewers can test your changes locally:

1. `python3 -m http.server 8080` (Open `http://localhost:8080/application/app/`)
2. `./experiments/run_all.sh` (Test benchmark framework engine and experiment outputs)
3. `docker run iacsecbench` (Test Docker containerized benchmark runner)
