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
             │   2. tfsec (HCL lexical binary scanner)                 │
             │   3. Trivy (tfsec's successor; inherits its rule set)   │
             │   4. OPA / Rego over the compiled Terraform plan        │
             │   5. IaCSecBench Layer 1 (repository-edge scanning)     │
             │                                                         │
             │   tfsec and Trivy are NOT independent: Aqua folded      │
             │   tfsec into Trivy, so the five columns above span      │
             │   four independent rule sets, not five.                 │
             │                                                         │
             │   Sentinel and Terratest are NOT evaluated. Neither has │
             │   ever been executed here and no number is reported.    │
             └────────────────────────────┬────────────────────────────┘
                                          │
                                          ▼
             ┌─────────────────────────────────────────────────────────┐
             │          Public Benchmark Dataset & Telemetry           │
             │   • benchmark/datasets/benchmarks.json                  │
             │   • results/evaluation.json  (measured)                 │
             └─────────────────────────────────────────────────────────┘
```

---

## 📁 Framework Structure

- `security_framework/engine/`: Core scanning engine (`engine.py`, including secret detection and syntax validation) and comparative driver (`comparative_eval.py`).
- `security_framework/policies/`: OPA / Rego security policy implementations.
- `security_framework/tests/`: Unit test suite for the engine's own behaviour — parsing,
  rule dispatch and output shape. It does **not** establish detection accuracy, and an
  earlier revision of this file claiming it verified "100% engine accuracy" was wrong in
  both directions: unit tests cannot measure accuracy, and the measured recall of the
  repository-edge layer on the benchmark corpus is 3.85%, not 100%. Detection
  effectiveness comes only from `experiments/run_baselines.sh`.
- `docs/framework/threat_model.md`: STRIDE-based threat modeling and attacker mitigation guidance.

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
