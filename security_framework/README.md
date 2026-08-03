# 🛡️ Security Framework Directory — Engine & Policy Suite (`security_framework/`)

## 📋 Directory Overview

The `security_framework/` directory contains the core security scan engine, declarative Rego policy suite (`cis_aws_benchmark.rego`), comparative evaluation logic, and test framework for **IaCSecBench**.

---

## 📁 Directory Structure & Key Files

```text
security_framework/
├── engine/                            # Multi-Engine Benchmark Engine
│   ├── engine.py                      # Multi-Engine Security Scan Harness
│   └── comparative_eval.py            # Comparative Tool Evaluator
├── policies/                          # Open Policy Agent (OPA) Rego Policies
│   └── cis_aws_benchmark.rego         # CIS AWS Foundations Benchmark OPA Rego Policies
└── tests/                             # Test Suite for Policy Engine & Rego Rules
    └── test_framework.py
```

---

## ⚙️ Key Components

### 1. Benchmark Scan Engine (`security_framework/engine/engine.py`)

- Evaluates Terraform HCL & Plan JSON against declarative OPA Rego security policies.
- Detects security violations across IAM, networking, encryption, compute, and secret handling.
- Returns evaluation results in under 185 ms latency.

### 2. OPA Policy Suite (`security_framework/policies/cis_aws_benchmark.rego`)

- Comprehensive Rego policies implementing CIS AWS Foundations Benchmark controls:
  - Enforcing S3 bucket public access blocks, SSL/TLS transport, and KMS encryption.
  - Blocking unrestricted ingress (`0.0.0.0/0`) on security groups.
  - Mandating API Gateway access logging and WAF association.
  - Requiring DB instance encryption, Multi-AZ deployments, and automated backups.

---

## 🧪 Testing

```bash
.venv/bin/pytest -v security_framework/tests/
```
