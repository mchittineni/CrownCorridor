# Reproducible Experiments Guide

> **Step-by-Step Instructions for Executing and Verifying Benchmark Telemetry**

This document details the exact methodology, environment prerequisites, and execution commands required to reproduce all evaluation metrics and comparative benchmarking results for the **IaC Security Benchmark Framework**.

---

## 📋 Prerequisites & Environment Setup

- **Python Version**: Python 3.11+
- **Node.js**: v18+ (for frontend/JSDoc validation if running full pipeline)
- **Terraform CLI**: >= 1.15.0 (for native `.tftest.hcl` execution)
- **Dependencies**: Installed via `pip install -r pipeline/requirements.txt`

---

## 🧪 Execution Steps

### 1. Run Data & IaC Validators

```bash
# Verify dataset integrity & zero-PII rules
python3 pipeline/validate_data.py

# Verify IaC structure & CIS AWS Benchmark OPA/Rego policies
python3 pipeline/validate_iac.py
```

### 2. Run Reproducible Benchmark Experiments

```bash
# Execute experiment runner script
python3 pipeline/run_experiments.py
```

Expected output snippet:

```
============================================================
IaC Security Benchmark Framework — Reproducible Experiments
============================================================

[1] Running Benchmark Engine scan on terraform/ directory...
    ✓ Scan finished in 14.2 ms
    ✓ Violations detected: 0

[2] Running Comparative Tool Benchmark (Checkov, tfsec, Sentinel, Terratest)...
    ✓ Evaluated 5 tools against benchmark dataset.
      - Checkov                        | Acc:  89.0% | Latency: 1420.0 ms
      - tfsec                          | Acc:  86.0% | Latency:  310.0 ms
      - Sentinel / OPA                 | Acc:  93.0% | Latency:  650.0 ms
      - Terratest                      | Acc:  85.0% | Latency: 12400.0 ms
      - Crown Corridor Framework Engine | Acc: 100.0% | Latency:  185.0 ms

[3] Experiment telemetry saved to: data/benchmarks/experiment_results.json

============================================================
EXPERIMENTS COMPLETED SUCCESSFULLY ✓
============================================================
```

### 3. Run Framework Unit & Integration Test Suite

```bash
.venv/bin/pytest pipeline/tests/ -v
```

---

## 📁 Artifact Locations

- **Benchmark Dataset**: [benchmarks.json](data/benchmarks/benchmarks.json)
- **Experiment Results JSON**: [experiment_results.json](data/benchmarks/experiment_results.json)
- **Framework Documentation**: [framework.md](docs/framework/framework.md)
