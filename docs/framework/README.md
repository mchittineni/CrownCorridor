# IaCSecBench: An Infrastructure-as-Code Security Benchmark Framework

> **An Open-Source Framework for IaC Security Benchmark Evaluation & Comparative Analysis**

IaCSecBench is a modular, reusable evaluation framework designed to benchmark Infrastructure-as-Code (IaC) static analysis tools, policy-as-code engines, integration testing suites, and zero-PII/secret scanners across cloud infrastructure definitions.

---

## 🏛️ Framework Architecture

```
                       [ Target IaC Modules & Configurations ]
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │    IaCSecBench Engine (engine.py)     │
                      │  • Secret / Zero-PII Regex Scanner   │
                      │  • HCL Syntax & Structure Check      │
                      │  • CIS AWS OPA / Rego Validator      │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
             ┌─────────────────────────────────────────────────────────┐
             │         Comparative Evaluator (comparative_eval.py)     │
             │                                                         │
             │   Evaluates:                                            │
             │   1. Checkov (AST Static Analysis Engine)               │
             │   2. tfsec (HCL AST Binary Scanner)                     │
             │   3. Sentinel / OPA Rego (Policy-as-Code Engines)       │
             │   4. Terratest (Go Integration Testing)                 │
             │   5. IaCSecBench Engine (Unified Benchmark Framework)   │
             └────────────────────────────┬────────────────────────────┘
                                          │
                                          ▼
             ┌─────────────────────────────────────────────────────────┐
             │          Public Benchmark Dataset & Telemetry           │
             │   • benchmark/datasets/benchmarks.json                  │
             │   • benchmark/reports/experiment_results.json           │
             └─────────────────────────────────────────────────────────┘
```

---

## 📁 Framework Structure

- `security_framework/engine/`: Core scanning engine (`engine.py`) and comparative driver (`comparative_eval.py`).
- `security_framework/policies/`: OPA / Rego security policy implementations.
- `security_framework/scanners/`: Secret detection and syntax validators.
- `security_framework/tests/`: Unit test suite verifying 100% engine accuracy.

---

## 💻 CLI Quickstart

```bash
# 1. Scan any target Terraform module directory
python3 -m security_framework.engine.engine infrastructure/

# 2. Run comparative tool benchmarking
python3 -m security_framework.engine.comparative_eval

# 3. Docker execution
docker run iacsecbench
```
