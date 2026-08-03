# 📊 Experiments Directory — One-Command Reproducibility Suite (`experiments/`)

## 📋 Directory Overview

The `experiments/` directory provides one-command reproducibility scripts for executing complete end-to-end benchmark experiments, running baseline tool scans, generating performance figures, and synchronizing workspace data with Obsidian.

---

## 📁 Directory Structure & Key Files

```text
experiments/
├── run_all.sh             # Master One-Command Reproduction Shell Script
├── run_baselines.sh       # Baseline Evaluation Runner Script
├── generate_charts.py     # Benchmark Performance Chart & Visual Figure Generator
├── environment.yml        # Conda / Virtual Environment specification
└── requirements.txt       # Python dependencies for experiments
```

---

## ⚙️ Key Execution Scripts

### 1. One-Command Reproduction Script (`run_all.sh`)
Three stages, none of which fabricates anything:
1. **Data Integrity & IaC Security Validation** — `validate_data.py` and `validate_iac.py`.
2. **Pytest Verification** — the unit test suite. No `IACSECBENCH_ALLOW_SYNTHETIC` is
   exported: tests that exercise a fabricating stage opt in individually, and one
   asserts those stages refuse without it.
3. **Measurement** — delegates to `run_baselines.sh`.

It no longer runs `score.py`, `run_experiments.py`, `generate_charts.py` or
`sync_to_obsidian.py`. The first three derive metrics from hardcoded rates and used
to overwrite measured results with them; the fourth publishes outside the
repository, which is a deliberate act rather than a build step. All four still work
and are invoked by hand — the first three only under
`IACSECBENCH_ALLOW_SYNTHETIC=1`.

### 2. Baseline Evaluation Shell Script (`run_baselines.sh`)
**The only script that produces results.** Four stages: corpus admissibility,
scanner execution with repeats, a control-map audit against the rule identifiers
actually emitted, then statistics and LaTeX table generation. Requires Checkov,
tfsec, OPA and Terraform; a tool that is absent is reported as absent and excluded,
never assigned an assumed detection rate.

Takes tens of minutes, largely in `terraform init`/`validate` per case.

> **Measure latency on an idle machine.** It is the one metric that reflects the
> host rather than the tool. The same corpus produced a Checkov standard deviation
> of 155 ms idle and 897 ms under load — a sixfold difference from the environment
> alone, with the mean barely moving. Detection counts are deterministic; latency
> is not.

### 3. In CI
`.github/workflows/benchmark.yml` runs this harness on manual dispatch and weekly,
installing all four tools and uploading `results/` as an artefact. It deliberately
does **not** commit results back, because CI latency would overwrite the only
publishable figures. Pull requests get the fast checks in `ci.yml` instead.

---

## 🚀 Running Experiments

```bash
# Run baseline evaluation suite
bash experiments/run_baselines.sh

# Run complete reproduction pipeline
bash experiments/run_all.sh
```
