# IaCSecBench Architecture & Pipeline Workflow

This document details the architectural components of **IaCSecBench**, including the parsing pipeline, rule evaluation lifecycle, and telemetry generation.

---

## 1. Engine Core Pipeline

The IaCSecBench engine processes target infrastructure repositories through three sequential phases:

```
┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│ 1. AST & HCL       │ ──> │ 2. Policy-as-Code  │ ──> │ 3. Zero-PII &      │
│    Syntax Parser   │     │    OPA Evaluator   │     │    Secret Scanner  │
└────────────────────┘     └────────────────────┘     └────────────────────┘
```

1. **AST & HCL Syntax Parser**: Scans `.tf` and `.hcl` files for syntactic correctness, brace balancing, block structure integrity, and provider constraints (`>= 1.15.0`).
2. **Policy-as-Code OPA Evaluator**: Evaluates CIS AWS Foundations Benchmark policies codified in Rego (`security_framework/policies/cis_aws_benchmark.rego`).
3. **Zero-PII & Secret Scanner**: Executes regex and entropy analysis across all IaC text files to guarantee zero exposure of personal customer names, emails, DB passwords, or AWS secret keys.

---

## 2. Comparative Evaluation Engine & Dataset Architecture

`ComparativeEvaluator` and `evaluation/score.py` evaluate tools against a dual-component dataset:

```
                 IaCSecBench Evaluation Flow
                              |
        ----------------------------------------------
        |                     |                      |
 Internal Controlled    External Validation     Production Observation
 Benchmark Suite        Collection              CI Runs
 (345 cases)            (175 cases)             (61 PRs)
 ├── vulnerable/        ├── terraform_registry/
 └── secure/            ├── secureflag/
                        └── cis_examples/
```

- **Checkov**: AST-based static analysis engine.
- **tfsec**: Go-compiled HCL AST scanner.
- **Sentinel / OPA**: Policy-as-Code evaluation framework.
- **IaCSecBench Engine**: Native multi-engine policy, testing, and secret detection framework.

Telemetry and leaderboard rankings are computed automatically via `evaluation/score.py` and exported to `leaderboard/results.csv`.
