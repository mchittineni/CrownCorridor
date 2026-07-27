#!/usr/bin/env bash
set -e

echo "============================================================"
echo "IaCSecBench — One-Command Experiment Reproducibility Suite"
echo "============================================================"
echo ""

# Find Python binary
if [ -f ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
elif [ -f ".venv/bin/python3" ]; then
  PYTHON=".venv/bin/python3"
else
  PYTHON="python3"
fi

# Find Pytest binary
if [ -f ".venv/bin/pytest" ]; then
  PYTEST=".venv/bin/pytest"
elif command -v pytest &> /dev/null; then
  PYTEST="pytest"
else
  PYTEST="$PYTHON -m pytest"
fi

# 1. Run Data Validator & IaC Security Scan
echo "[Step 1/4] Running Data Integrity & IaC Security Validation..."
$PYTHON pipeline/validate_data.py
$PYTHON pipeline/validate_iac.py

# 2. Execute Pytest Test Suite
echo ""
echo "[Step 2/4] Executing Framework & Unit Tests with Coverage..."
if $PYTEST --help 2>&1 | grep -q "\--cov"; then
  COV_FLAG="--cov=security_framework"
else
  COV_FLAG=""
fi
$PYTEST security_framework/tests/ pipeline/tests/ $COV_FLAG -v

# 3. Run Experiment Pipeline & Generate Benchmark Results
echo ""
echo "[Step 3/4] Running IaCSecBench Comparative Experiments..."
$PYTHON pipeline/run_experiments.py

# 4. Generate Visual Charts & CSV Telemetry
echo ""
echo "[Step 4/4] Generating Benchmark Performance Figures & Metrics CSV..."
$PYTHON experiments/generate_charts.py

echo ""
echo "============================================================"
echo "SUCCESS: All experiments executed and results generated!"
echo "Outputs stored in results/ & benchmark/reports/"
echo "============================================================"
