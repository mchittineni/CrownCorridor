# 🛠️ Scripts Directory — Developer Analysis Utilities

## 📋 Directory Overview

Standalone command-line utilities for local code review and repository analysis.

**None of these scripts is wired into `.pre-commit-config.yaml` or any GitHub Actions
workflow**, and none produces a number that appears in `results/`, the leaderboard, or
the paper. They are convenience tools, not gates and not part of the measured pipeline.
The checks that actually gate this repository are the pre-commit hooks (ruff, isort,
flake8, bandit, pylint) and the workflows described in
[`.github/workflows/README.md`](../.github/workflows/README.md).

---

## 📁 Directory Structure & Key Files

```text
scripts/
├── code_quality_checker.py     # File-level complexity thresholds
├── compliance_checker.py       # Framework compliance — STUB, see below
├── pr_analyzer.py              # Diff risk scoring & review prioritisation
├── review_report_generator.py  # Combined report from the tools above
└── security_scanner.py         # Pattern-based scan of code and IaC files
```

---

## ⚙️ Key Components Explained

### 1. Code Quality Checker (`code_quality_checker.py`)

Reports file-level complexity against configurable thresholds.
Arguments: a path to analyse and a language to evaluate.

### 2. Compliance Checker (`compliance_checker.py`)

**A stub.** Its own `--help` text describes it as a "compliance checker stub for standard
frameworks." It does not establish compliance with any framework, and its output must not
be cited as evidence of one. Real control-level evaluation is
`evaluation/run_baselines.py` against `evaluation/control_map.json`.

### 3. PR Analyzer (`pr_analyzer.py`)

Scores a diff for review risk and prioritisation, given a repository root and a base
branch or commit.

### 4. Review Report Generator (`review_report_generator.py`)

Combines the output of the other utilities into one report. Supports multiple output
formats.

### 5. Security Scanner (`security_scanner.py`)

Pattern-based scan over code and IaC files, filterable by minimum severity. This is not
one of the scanners under measurement — Checkov, tfsec, Trivy and the plan-level OPA layer
are, and their results come from `experiments/run_baselines.sh`.

> An earlier version of this file documented `check_compliance.py` and `generate_docs.sh`.
> Neither exists in this repository, and none of the five scripts that do exist was
> described. JSDoc is built by `npm run docs`, not by a shell script here.

---

## 🔗 Related Knowledge Base Links

- [[Project-Structure|📐 View Project Architecture]]
