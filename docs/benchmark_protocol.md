# IaCSecBench — Evaluation Protocol & Reproducibility Standard

This document details the evaluation protocol, scoring metrics, ground truth format, and reproducibility guidelines for the **IaCSecBench** benchmark suite.

---

## Evaluation Protocol Overview

To ensure objective and fair comparison across IaC analysis tools (**Checkov**, **tfsec**, **plan-level OPA**, and the **IaCSecBench Engine**), each tool is evaluated against the cases that are _admissible_: present on disk, carrying an unambiguous ground-truth label, and passing `terraform validate` against the declared provider.

Admissibility is the operative word. The corpus is described in two numbers that do not agree, and the protocol reports both rather than the flattering one:

1. **Declared** — what the catalogue and the external `metadata.json` manifests enumerate.
2. **Present and admissible** — what actually exists and can be scanned. This is the denominator for every metric in this repository.

The external manifests declare substantially more cases than there are configurations on disk (two of the three external collections contain no Terraform files at all). A manifest entry without a configuration is a citation, not a case, and is never counted as one. `results/corpus_report.json` reports the declared and present counts side by side, per collection.

Do not quote a corpus size from this document. Read the current one:

```bash
python -m evaluation.corpus --report --mode terraform
```

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

Every execution records its own environment into `results/run_manifest.json`:
platform, CPU count, Python version, git commit, the resolved path and reported
version of each tool, the repeat count, the validation mode, and the raw latency
samples. The manifest is the authoritative record of a run. Where this document
and the manifest disagree, the manifest is right.

The manifest also records which tools were _not_ installed. A tool that could
not be executed is reported as absent and excluded from the comparison; it is
never represented by an assumed detection rate, and never appears in a results
table as though it had scored zero.

---

## Running the Benchmark Evaluation Protocol

One command measures everything and regenerates every artefact:

```bash
experiments/run_baselines.sh            # 3 latency repeats
REPEATS=10 experiments/run_baselines.sh # more latency samples
```

It runs four stages in order: corpus admissibility, scanner execution, a
control-map audit against the rule identifiers actually emitted, and statistics
plus LaTeX table emission. Nothing in it synthesises a result.

**Measure latency on an otherwise idle machine.** Latency is the one metric that
reflects the host rather than the tool. Background load inflates the mean and
roughly doubles the standard deviation, and no amount of repeats corrects it.

### Stages that do _not_ measure anything

`evaluation/score.py`, `pipeline/run_experiments.py` and
`experiments/generate_charts.py` do not execute a scanner. They multiply corpus
counts by hardcoded per-tool rates and write the product to the same filenames a
real run uses. Each now refuses to run unless explicitly opted into:

```bash
IACSECBENCH_ALLOW_SYNTHETIC=1 python evaluation/score.py
```

Output produced this way is illustrative and must not be published or cited.
