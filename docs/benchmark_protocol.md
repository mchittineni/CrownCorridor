# IaCSecBench — Evaluation Protocol & Reproducibility Standard

This document details the evaluation protocol, scoring metrics, ground truth format, and reproducibility guidelines for the **IaCSecBench** benchmark suite.

---

## Evaluation Protocol Overview

To ensure objective and fair comparison across IaC analysis tools (**Checkov**, **tfsec**, **Terrascan**, **OPA**, and **IaCSecBench Engine**), each tool is evaluated against a standardized set of 345 benchmark cases.

### Scoring Metrics

1. **Accuracy (ACC)**: Percentage of benchmark cases correctly classified (True Positives + True Negatives) / Total Cases.
   $$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

2. **Precision (PREC)**: Percentage of reported security violations that are genuine violations.
   $$\text{Precision} = \frac{TP}{TP + FP}$$

3. **Recall (REC)**: Percentage of actual security violations detected by the tool.
   $$\text{Recall} = \frac{TP}{TP + FN}$$

4. **F1 Score**: Harmonic mean of Precision and Recall.
   $$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

5. **False Positive Rate (FPR)**: Rate of false alarms on secure/compliant benchmark cases.
   $$\text{FPR} = \frac{FP}{FP + TN}$$

6. **False Negative Rate (FNR)**: Rate of missed security vulnerabilities on insecure cases.
   $$\text{FNR} = \frac{FN}{TP + FN}$$

7. **Execution Latency (MS)**: Total wall-clock time in milliseconds taken to analyze the full benchmark suite.

---

## Ground Truth Format (`expected.json`)

Each benchmark test case specifies a ground truth definition in `expected.json`:

```json
{
  "benchmark_id": "STO-001",
  "expected_result": "FAIL",
  "severity": "HIGH",
  "violations": [
    {
      "resource": "aws_s3_bucket.data",
      "property": "acl",
      "rule_id": "CIS_AWS_2_1_1",
      "description": "S3 bucket ACL allows public read access"
    }
  ]
}
```

---

## Reproducibility Telemetry & Metadata

All benchmark executions capture systemic reproducibility metadata:

```json
{
  "system_environment": {
    "terraform_version": "1.15.0",
    "aws_provider": "6.56.0",
    "opa_version": "0.62.0",
    "os": "macOS / Linux Ubuntu 22.04 LTS",
    "runner": "IaCSecBench Experiment Harness v1.0.0"
  }
}
```

---

## Running the Benchmark Evaluation Protocol

To run the complete benchmark evaluation suite and generate the leaderboard:

```bash
# 1. Execute automated evaluation protocol
python evaluation/score.py

# 2. Execute full reproducibility suite (validation, tests, experiments, charts)
./experiments/run_all.sh
```
