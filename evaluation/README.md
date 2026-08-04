# 🧪 Evaluation Directory — Scoring Protocol & Baseline Evaluation Suite (`evaluation/`)

## 📋 Directory Overview

The `evaluation/` directory contains the evaluation protocol, statistical analysis tools, normalization engines, and baseline execution tools responsible for calculating precision, recall, F1 scores, latency metrics, zero-PII compliance, and generating leaderboard outputs for IaC scanners.

---

## 📁 Directory Structure & Key Files

```text
evaluation/
├── score.py               # Evaluation Protocol & Synthetic Leaderboard Guard Engine
├── run_baselines.py       # Baseline Evaluation Runner across IaC scanners
├── analyze.py             # Evaluation Analysis & Metric Summary Aggregator (CLI entry point)
├── tables.py              # LaTeX table emitters + the generated-table structural guard
├── metrics.py             # Metric dataclass for the deprecated score.py path only
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
  **four** distinct rule sets, of which only **two** are independent _third-party_ ones: Checkov's and the
  tfsec/Trivy lineage. Plan-level OPA and the repository-edge layer are this project's own. The manuscript
  reports the two-third-party figure, and that is the number any comparative claim rests on. Sentinel and Terratest are _not_ evaluated; an earlier version of
  this file listed them, and no measurement against either has ever been recorded.
- Measures detection counts with exact Clopper-Pearson intervals, and per-case scan latency (ms) over repeats.
- A tool that is not installed is reported as absent and omitted from every table. It is never assigned an
  assumed detection rate.

### 2. Statistical Implementation (`stats.py`)

Pure standard library, so the replication package runs on a bare interpreter. Every
method is exact or explicitly labelled an approximation, and each is pinned by a
test to independently derived values rather than to its own output.

- Exact **Clopper-Pearson** intervals for recall, precision and specificity. Chosen
  for the coverage guarantee, not for width: coverage is never below nominal,
  whereas score and adjusted-Wald intervals undercover near the boundary, which is
  where most of these estimates sit. `wilson` is also provided so a reader who
  prefers the score interval can obtain it.
- The **exact binomial McNemar** test, used in preference to the chi-square
  approximation, which the module flags invalid when a discordant cell is small.
- `minimum_detectable_discordance` — the smallest $|b-c|$ the exact test could have
  called significant at a given discordant count, or `None` when no split could.
  This distinguishes "the tools are similar" from "the comparison had no power":
  at five or fewer discordant pairs the smallest attainable two-sided $p$ is
  0.0625, so no outcome can reject. Both McNemar tables carry it as a $d_{\min}$
  column.
- **Holm-Bonferroni** correction, Haldane-Anscombe-corrected odds ratios so a zero
  cell stays finite, Cohen's $g$, and MCC.

### 2a. Deprecated Scoring Path (`score.py`, `metrics.py`)

- `score.py` derives leaderboard metrics from hardcoded per-tool rates rather than
  from measurement, and `metrics.py` is the metric implementation it uses. Both are
  retained only so the gated path keeps working; **prefer `stats.py` and
  `analyze.py` for anything reported.**
- Running `score.py` requires `IACSECBENCH_ALLOW_SYNTHETIC=1`. CI asserts that it
  **refuses** without the opt-in, so the guard cannot rot unnoticed.

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
