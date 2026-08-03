# 🧪 Evaluation Directory — Scoring Protocol & Baseline Evaluation Suite (`evaluation/`)

## 📋 Directory Overview

The `evaluation/` directory contains the evaluation protocol, statistical analysis tools, normalization engines, and baseline execution tools responsible for calculating precision, recall, F1 scores, latency metrics, zero-PII compliance, and generating leaderboard outputs for IaC scanners.

---

## 📁 Directory Structure & Key Files

```text
evaluation/
├── score.py               # Evaluation Protocol & Synthetic Leaderboard Guard Engine
├── run_baselines.py       # Baseline Evaluation Runner across IaC scanners
├── analyze.py             # Evaluation Analysis & Metric Summary Aggregator
├── corpus.py              # Infrastructure Corpus Analysis & Categorization
├── stats.py               # Statistical Significance & Confidence Interval Calculator
├── normalize.py           # Finding Normalization Engine & Canonical Schema Mapper
├── control_map.json       # Mapping between CIS AWS controls & benchmark test cases
└── tests/                 # Unit Tests for Evaluation Protocol & Baseline Tools
```

---

## ⚙️ Key Components & Workflows

### 1. Baseline Evaluation Suite (`run_baselines.py` & `experiments/run_baselines.sh`)

- Executes evaluations against Checkov, tfsec, Trivy, plan-level OPA, and the repository-edge IaCSecBench layer.
  Note that Trivy is tfsec's maintained successor and inherits its rule set, so the five columns represent
  **four** independent rule sets, not five. Sentinel and Terratest are _not_ evaluated; an earlier version of
  this file listed them, and no measurement against either has ever been recorded.
- Measures detection counts with exact Clopper-Pearson intervals, and per-case scan latency (ms) over repeats.
- A tool that is not installed is reported as absent and omitted from every table. It is never assigned an
  assumed detection rate.

### 2. Evaluation Protocol & Synthetic Guard (`score.py`)

- Computes Clopper-Pearson 95% confidence intervals (`CI_95%`) and McNemar's statistical significance.
- Requires `IACSECBENCH_ALLOW_SYNTHETIC=1` when running synthetic leaderboard calculations to prevent accidental publication of non-measured metrics.

### 3. Finding Normalization Engine (`normalize.py`)

- Maps heterogeneous scanner output formats (SARIF, JSON, custom CLI text) into a canonical security finding taxonomy:
  $$\mathcal{F} = \langle \text{Case\_ID}, \text{Domain}, \text{Severity}, \text{Resource\_URN}, \text{Status} \rangle$$

---

## 🧪 Testing & Execution

```bash
# Run baseline evaluation suite
python3 evaluation/run_baselines.py

# Run leaderboard scoring with synthetic override guard
IACSECBENCH_ALLOW_SYNTHETIC=1 python3 evaluation/score.py

# Run evaluation pytest suite
.venv/bin/pytest -v evaluation/tests/
```
