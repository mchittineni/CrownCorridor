# 🎯 Benchmark Directory — Ground-Truth Datasets & Test Scenarios

## 📋 Directory Overview

The `benchmark/` directory contains the controlled ground-truth evaluation datasets and external validation scenarios used by **IaCSecBench** to assess IaC security scanners and Policy-as-Code engines.

---

## 📁 Directory Structure & Key Files

```text
benchmark/
├── internal/                          # Controlled Internal Benchmark Suite (44 cases present)
│   ├── metadata.json                  # Canonical Labelled Ground-Truth Annotations
│   ├── cases/                         # 12 Domain HCL Configurations
│   └── baselines/                     # Secure Infrastructure Baselines
├── external/                          # External collection: 175 DECLARED, 4 present
│   ├── terraform_registry/            # metadata declares 50; modules/ is empty
│   │   └── metadata.json
│   ├── secureflag/                    # metadata declares 75; terraform/ is empty
│   │   └── metadata.json
│   └── cis_examples/                  # metadata declares 50; aws/ holds 4 .tf files
│       └── metadata.json

(There is no reports/ directory. See section 3 below.)
```

---

## ⚙️ Key Components Explained

### 1. Internal Controlled Benchmark (`benchmark/internal/`)
- Contains **44 labelled cases present on disk** (22 vulnerable / 22 compliant) across 8 domains: IAM, NET, STO, ENC, CMP, MON, SEC, SRV. The designed taxonomy targets 345 cases across 12 domains; the four remaining domains (K8S, ID, PII, TF) have no cases yet and nothing is measured over them.
- **Metadata Annotation Schema (`metadata.json`)**: Formats each case with canonical attributes: `case_id`, `domain`, `severity`, `target_resource_urn`, and ground-truth `status` (`VIOLATION` vs. `COMPLIANT`).

### 2. External Validation Collection (`benchmark/external/`)
Each `metadata.json` here declares more cases than there are configurations on
disk. The manifests are left unmodified on purpose: `evaluation/corpus.py` reads
the declared count precisely so it can report the gap, and correcting the
manifests would erase the evidence of it.

- **`terraform_registry/`**: declares 50 modules. `modules/` is empty — **0 usable cases.**
- **`secureflag/`**: declares 75 scenarios. `terraform/` is empty — **0 usable cases.**
- **`cis_examples/`**: declares 50 controls. `aws/` holds **4** Terraform configurations, and those 4 are the entire external contribution to every measurement in this repository.

A manifest entry with no configuration behind it is a citation, not a case, and
is never counted as one.

### 3. Generated Evaluation Telemetry — now under `results/`
Measured output lives in [`results/`](../results/), not here. `benchmark/reports/`
previously held `experiment_results.json`, written by `pipeline/run_experiments.py`
from hardcoded per-tool rates rather than from any scanner execution; it has been
deleted, and the stage that wrote it now refuses to run without
`IACSECBENCH_ALLOW_SYNTHETIC=1`.

Execution outputs, timing data, confusion matrices and precision/recall statistics
are in `results/run_manifest.json` and `results/evaluation.json`. See
[`results/README.md`](../results/README.md).

---

## Ground-truth labelling and its independent check

Labels are derived mechanically by `generate_corpus.py` from per-control
specifications, so rater disagreement is impossible by construction and
**specification error** is the threat that replaces it.

[`labelling/`](labelling/) records a blind second labelling pass run against that
threat: 47 of 48 cases agreed (Cohen's κ = 0.958, before reconciliation), and the
single disagreement was a genuine defect — a control whose stated text was weaker
than the requirement its label encoded. Read
[`labelling/README.md`](labelling/README.md) for the method, the reconciliation, and
the limitations that bound what κ means here.

## 🔗 Related Knowledge Base Links
- [[Research/RQ1-Internal-Metrics|📊 RQ1: Internal Controlled Benchmark Performance]]
- [[Research/RQ5-External-Generalizability|🌐 RQ5: External Validation Collection]]
- [[Project-Structure|📐 View Project Architecture]]
