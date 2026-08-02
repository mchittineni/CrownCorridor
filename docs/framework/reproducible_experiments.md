# Reproducible Experiments Guide

> **Step-by-Step Instructions for Executing and Verifying Benchmark Telemetry**

This document details the exact methodology, environment prerequisites, and execution commands required to reproduce all evaluation metrics and comparative benchmarking results for the **IaC Security Benchmark Framework**.

---

## 📋 Prerequisites & Environment Setup

- **Python Version**: Python 3.11+
- **Node.js**: v18+ (for frontend/JSDoc validation if running full pipeline)
- **Terraform CLI**: >= 1.15.0 (for native `.tftest.hcl` execution)
- **Dependencies**: Installed via `pip install -r pipeline/requirements.txt -r experiments/requirements.txt`

---

## 🧪 Execution Steps

### 1. Run Data & IaC Validators

```bash
# Verify dataset integrity & zero-PII rules
python3 pipeline/validate_data.py

# Verify IaC structure & CIS AWS Benchmark OPA/Rego policies
python3 pipeline/validate_iac.py
```

### 2. Run Reproducible Benchmark Experiments & Scoring Protocol

```bash
# Execute evaluation scoring protocol
python evaluation/score.py

# Execute full one-command reproducibility suite
./experiments/run_all.sh
```

Expected output snippet:

```
============================================================
IaCSecBench Leaderboard & Evaluation Protocol Results
============================================================
Tool                 | Category               | Recall   | Precision  | F1       | Latency
------------------------------------------------------------------------------------------
Checkov              | AST Static Analysis    |   90.3% |     92.4% |   91.3% |   1420.0 ms
tfsec                | HCL Lexical Scanner    |   88.0% |     93.9% |   90.9% |    310.0 ms
OPA / Sentinel       | Rego Policy Engine     |   92.0% |     95.3% |   93.6% |    650.0 ms
IaCSecBench Engine   | Multi-Engine Validation |  100.0% |    100.0% |  100.0% |    185.0 ms
============================================================
✓ Leaderboard results saved to: leaderboard/results.csv
```

### 3. Run Framework Unit & Integration Test Suite

```bash
.venv/bin/pytest security_framework/tests/ pipeline/tests/ -v
```

---

## 📁 Artifact Locations

- **Master Benchmark Catalog**: [benchmark.json](../../benchmark/benchmark.json)
- **Benchmark Dataset Schema**: [benchmarks.json](../../benchmark/datasets/benchmarks.json)
- **Experiment Results JSON**: [experiment_results.json](../../benchmark/reports/experiment_results.json)
- **Leaderboard Export**: [results.csv](../../leaderboard/results.csv)
- **Framework Documentation**: [framework.md](framework.md)
