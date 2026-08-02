# Contributing to IaCSecBench & Crown Corridor

Thank you for your interest in contributing to **IaCSecBench: An Infrastructure-as-Code Security Benchmark Framework** and the **Crown Corridor** platform!

---

## 🚀 How to Contribute

We welcome contributions across several areas:

1. **Adding Benchmark Scenarios**: Adding self-contained test cases to `benchmark/internal/metadata.json` and `benchmark/internal/cases/`.

2. **Policy Extensions**: Adding OPA / Rego security policy rules under `security_framework/policies/`.
3. **Scanner & Metric Enhancements**: Extending static analysis, scoring protocols (`evaluation/score.py`), and secret detection engines under `security_framework/engine/`.
4. **Bug Reports & Feature Requests**: Submitting issues with reproducible steps.

---

## 🛠️ Local Development & Testing Workflow

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/mchittineni/IaCSecBench.git
cd IaCSecBench
python3 -m venv .venv
source .venv/bin/activate
pip install -r pipeline/requirements.txt -r application/api/requirements.txt
pip install pre-commit && pre-commit install

# Node.js toolchain (ESLint, Prettier, JSDoc)
npm install
```

### 2. Run Quality Checks & Tests

Before submitting a Pull Request, ensure all verification steps pass cleanly:

```bash
# 1. Run zero-PII data validator
python3 pipeline/validate_data.py

# 2. Run IaC security & policy validator
python3 pipeline/validate_iac.py

# 3. Run evaluation protocol & leaderboard scoring
IACSECBENCH_ALLOW_SYNTHETIC=1 python3 evaluation/score.py

# 4. Run full test suite (63 tests: application/api, pipeline, evaluation & security_framework)
IACSECBENCH_ALLOW_SYNTHETIC=1 .venv/bin/pytest -v

# 5. Run one-command reproducible experiment suite
./experiments/run_all.sh

# 6. Run pre-commit hook checks & JSDoc documentation generator
pre-commit run --all-files
npm run docs

# 7. Run JavaScript lint & formatting checks
npm run lint
npm run format:check

# 8. Run Obsidian Vault Knowledge Base & Research Sync
python3 pipeline/sync_to_obsidian.py
```

---

## 📋 Pull Request Submission Guidelines

1. **Commit Message Format**: Use clear, imperative titles (e.g., `feat(benchmark): add S3 ACL vulnerability scenario`).
2. **Zero-PII Compliance**: Ensure no customer names, personal phone numbers, or real identities are added to code or dataset files.
3. **Tests Required**: Every bugfix or feature must include corresponding test cases under `security_framework/tests/` or `pipeline/tests/`.
4. **Documentation**: Update markdown documentation under `docs/framework/` if introducing new CLI flags or metrics.
