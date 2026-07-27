#!/usr/bin/env bash
set -e

echo "============================================================"
echo "IaCSecBench — One-Command Experiment Reproducibility Suite"
echo "============================================================"
echo ""

# 1. Run Data Validator & IaC Security Scan
echo "[Step 1/4] Running Data Integrity & IaC Security Validation..."
python3 pipeline/validate_data.py
python3 pipeline/validate_iac.py

# 2. Execute Pytest Test Suite
echo ""
echo "[Step 2/4] Executing Framework & Unit Tests with Coverage..."
.venv/bin/pytest security_framework/tests/ pipeline/tests/ --cov=security_framework -v

# 3. Run Experiment Pipeline & Generate Benchmark Results
echo ""
echo "[Step 3/4] Running IaCSecBench Comparative Experiments..."
python3 pipeline/run_experiments.py

# 4. Generate Visual Charts & CSV Telemetry
echo ""
echo "[Step 4/4] Generating Benchmark Performance Figures & Metrics CSV..."
python3 experiments/generate_charts.py

echo ""
echo "============================================================"
echo "SUCCESS: All experiments executed and results generated!"
echo "Outputs stored in results/ & benchmark/reports/"
echo "============================================================"
