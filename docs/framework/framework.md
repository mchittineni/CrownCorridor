# IaC Security & Evaluation Benchmark Framework

> **An Open-Source Framework for IaC Security Benchmark Evaluation & Comparative Analysis**

The **IaC Security & Evaluation Benchmark Framework** is a modular, reusable framework designed to evaluate Infrastructure as Code (IaC) security static analysis, policy-as-code enforcement, integration testing, and zero-PII/secret prevention across multiple cloud architectures and repositories.

---

## 🌟 Key Capabilities

- 🔍 **Multi-Repository & Multi-Module IaC Engine**: Generic scanning engine capable of evaluating arbitrary Terraform modules, provider constraints, and security standards.
- 📊 **Comparative Benchmark Driver**: Measures **Checkov**, **tfsec**, **Trivy**, and **plan-level OPA** against the same admissible corpus. Trivy is tfsec's maintained successor and inherits its rule set, so these represent **three** independent third-party rule sets, not four. Sentinel and Terratest are _not_ evaluated — neither was ever executed here, and no number is reported for either.
- 📦 **Public Benchmark Datasets**: Standardized, annotated test case schema stored under `benchmark/datasets/benchmarks.json`.
- 🧪 **Reproducible Experiments**: One-command measurement suite (`experiments/run_baselines.sh`) producing raw scanner output, latency samples, exact confidence intervals and LaTeX tables.
- 🔒 **Zero-PII & Secret Compliance**: Automatic scanning for customer PII, AWS secret keys, hardcoded database credentials, and tokens.

---

## 🏛️ Architecture Overview

```
                        [ Target IaC Repositories & Modules ]
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │    Benchmark Engine (engine.py)       │
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
             │   1. Checkov (AST Python Scanner)                       │
             │   2. tfsec (HCL lexical binary)                         │
             │   3. Trivy (tfsec's successor; same rule lineage)       │
             │   4. OPA / Rego over the compiled Terraform plan        │
             │   5. IaCSecBench Layer 1 (repository-edge scanning)     │
             └────────────────────────────┬────────────────────────────┘
                                          │
                                          ▼
             ┌─────────────────────────────────────────────────────────┐
             │          Public Benchmark Dataset & Telemetry           │
             │   • data/benchmarks/benchmarks.json                    │
             │   • results/evaluation.json  (measured)                 │
             └─────────────────────────────────────────────────────────┘
```

---

## 📊 Comparative Performance Matrix

Results are not reproduced in this document. A table pasted into prose cannot be
regenerated, so it silently becomes wrong the first time the corpus, the control
map or a tool version changes — and a stale table is indistinguishable from a
current one. The measured matrix lives in exactly two generated places:

| Artefact                                                   | Contents                                                                                                   |
| :--------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------- |
| [`leaderboard/results.csv`](../../leaderboard/results.csv) | Per-tool TP/FP/TN/FN, accuracy, precision, recall, F1, FPR/FNR, exact recall interval, latency mean and SD |
| `results/evaluation.json`                                  | The same, plus per-case outcomes, all three matching levels, and pairwise McNemar tests                    |

Regenerate both with:

```bash
experiments/run_baselines.sh
```

Two things to know before reading the numbers:

- **The reference implementation does not win.** Layer 1 is a repository-edge
  secret and PII scanner, so on a corpus of cloud misconfigurations it detects
  almost nothing. That is a scope result, not a defect, and it is reported as
  measured rather than adjusted.
- **Latency reflects the host.** Measure it on an idle machine or do not quote it.

---

## 🚀 Quickstart & Usage

### 1. Run Benchmark Engine Scanner

```bash
python -m security_framework.engine.engine
```

### 2. Measure the comparative evaluation and regenerate the leaderboard

```bash
experiments/run_baselines.sh
```

This is the only command that produces results. `evaluation/score.py` is deprecated:
it fabricates metrics from hardcoded rates and refuses to run without
`IACSECBENCH_ALLOW_SYNTHETIC=1`.

### 3. Run the full reproducibility suite (validation, tests, measurement)

```bash
./experiments/run_all.sh
```

---

## 📄 License & Open-Source Distribution

This framework is released under the **MIT License**. Benchmark datasets are under `benchmark/`; measured evaluation telemetry is under `results/`.
