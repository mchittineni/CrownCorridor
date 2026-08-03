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
 (44 present)           (4 present)             (61 PRs)
 ├── vulnerable/        ├── terraform_registry/  (declares 50, 0 present)
 └── secure/            ├── secureflag/          (declares 75, 0 present)
                        └── cis_examples/        (declares 50, 4 present)
```

The designed taxonomy targets 345 internal and 175 external cases. The counts above
are what exists and is scanned; every metric uses the present count as its
denominator. `results/corpus_report.json` reports both side by side.

- **Checkov**: AST-based static analysis engine.
- **tfsec**: Go-compiled HCL lexical scanner. (Not an AST scanner — an earlier revision of
  this file said AST, which conflated it with Checkov and contradicted the tool labels in
  `evaluation/analyze.py`.) No longer maintained; superseded by Trivy.
- **Trivy**: Go-compiled HCL scanner, the maintained successor to tfsec. Aqua folded tfsec's
  engine and rule set into it, so tfsec and Trivy share rule provenance and their identifiers
  are the same AVD numbers spelled differently (`AVD-AWS-0086` vs `AWS-0086`). Measured
  because tfsec is retired, **not** because it supplies an independent opinion.
- **OPA / Rego**: Policy-as-Code evaluation over the compiled Terraform plan.
- **IaCSecBench Engine**: Native multi-engine policy, testing, and secret detection framework.

HashiCorp Sentinel is not evaluated: it is not open source and was never executed
here, so no figure is reported for it.

Telemetry and leaderboard rankings are measured by `experiments/run_baselines.sh`
and exported to `leaderboard/results.csv` by `evaluation/analyze.py`.
`evaluation/score.py` does **not** measure anything — it fabricates metrics from
assumed rates and is gated behind `IACSECBENCH_ALLOW_SYNTHETIC=1`.
