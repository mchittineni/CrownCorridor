# 🎯 Benchmark Directory — Ground-Truth Datasets & Test Scenarios

## 📋 Directory Overview

The `benchmark/` directory contains the controlled ground-truth evaluation datasets and external validation scenarios used by **IaCSecBench** to assess IaC security scanners and Policy-as-Code engines.

---

## 📁 Directory Structure & Key Files

```text
benchmark/
├── internal/                          # Controlled Internal Benchmark Suite (345 Cases)
│   ├── metadata.json                  # Canonical Labelled Ground-Truth Annotations
│   ├── cases/                         # 12 Domain HCL Configurations
│   └── baselines/                     # Secure Infrastructure Baselines
├── external/                          # External Generalizability Collection (175 Cases)
│   ├── terraform_registry/            # 50 Real-World Public Registry Modules
│   │   └── metadata.json
│   ├── secureflag/                    # 75 Vulnerability Scenarios
│   │   └── metadata.json
│   └── cis_examples/                  # 50 CIS AWS Foundations Benchmark Scenarios
│       └── metadata.json
└── reports/                           # Generated Benchmark Telemetry & Evaluation Reports
    ├── experiment_results.json        # Execution Telemetry
    └── comparative_matrix.md          # Generated Summary Matrix
```

---

## ⚙️ Key Components Explained

### 1. Internal Controlled Benchmark (`benchmark/internal/`)
- Contains 345 labelled test cases across 12 infrastructure domains (176 vulnerable configurations and 169 secure baselines).
- **Metadata Annotation Schema (`metadata.json`)**: Formats each case with canonical attributes: `case_id`, `domain`, `severity`, `target_resource_urn`, and ground-truth `status` (`VIOLATION` vs. `COMPLIANT`).

### 2. External Validation Collection (`benchmark/external/`)
- **`terraform_registry/`**: 50 independent Terraform Registry modules evaluating real-world HCL complexity, dynamic blocks, and variable interpolation.
- **`secureflag/`**: 75 real-world security vulnerability scenarios covering public S3 buckets, open security groups, and excessive IAM policies.
- **`cis_examples/`**: 50 Terraform configurations derived from CIS AWS Foundations Benchmark v3.0 compliance controls.

### 3. Generated Evaluation Telemetry (`benchmark/reports/`)
- Stores execution outputs, timing data, confusion matrices, and precision/recall statistics produced during benchmark evaluation runs.

---

## 🔗 Related Knowledge Base Links
- [[Research/RQ1-Internal-Metrics|📊 RQ1: Internal Controlled Benchmark Performance]]
- [[Research/RQ5-External-Generalizability|🌐 RQ5: External Validation Collection]]
- [[Project-Structure|📐 View Project Architecture]]
