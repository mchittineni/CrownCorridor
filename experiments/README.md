# 📊 Experiments Directory — One-Command Reproducibility Suite (`experiments/`)

## 📋 Directory Overview

The `experiments/` directory provides one-command reproducibility scripts for executing complete end-to-end benchmark experiments, running baseline tool scans, generating performance figures, and synchronizing workspace data with Obsidian.

---

## 📁 Directory Structure & Key Files

```text
experiments/
├── run_all.sh             # Master One-Command Reproduction Shell Script
├── run_baselines.sh       # Baseline Evaluation Runner Script
├── generate_charts.py     # Benchmark Performance Chart & Visual Figure Generator
├── environment.yml        # Conda / Virtual Environment specification
└── requirements.txt       # Python dependencies for experiments
```

---

## ⚙️ Key Execution Scripts

### 1. One-Command Reproduction Script (`run_all.sh`)
Executes the full paper evaluation pipeline:
1. **Data Integrity & IaC Security Validation**: Executes `validate_data.py` and `validate_iac.py`.
2. **Pytest Verification**: Runs the complete unit test suite with `IACSECBENCH_ALLOW_SYNTHETIC=1 pytest`.
3. **Comparative Evaluation**: Executes `score.py` and `run_experiments.py`.
4. **Figure Generation**: `generate_charts.py` charts *assumed* per-tool rates, not measurements. It refuses to run without `IACSECBENCH_ALLOW_SYNTHETIC=1`, and its former output (`results/metrics.csv`, `results/charts/`) has been deleted. Measured figures come from `results/evaluation.json`.
5. **Obsidian Sync**: Runs `pipeline/sync_to_obsidian.py` to synchronize notes and indexes.

### 2. Baseline Evaluation Shell Script (`run_baselines.sh`)
Runs baseline benchmarks across static analysis tools and policy engines.

---

## 🚀 Running Experiments

```bash
# Run baseline evaluation suite
bash experiments/run_baselines.sh

# Run complete reproduction pipeline
bash experiments/run_all.sh
```
