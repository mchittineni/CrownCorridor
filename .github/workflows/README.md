# Workflows

| Workflow | Trigger | Purpose |
| :--- | :--- | :--- |
| `ci.yml` | every PR + push to main | Lint, format, security audit, unit tests, data validation, fast corpus check, synthetic-guard assertion |
| `infra-ci.yml` | PR/push touching `infrastructure/`, `security_framework/`, `benchmark/`, `evaluation/`, `leaderboard/`, `experiments/` | Terraform fmt/validate/test, conftest policy evaluation, Checkov scan, Rego parse + format, corpus admissibility, tests |
| `benchmark.yml` | manual dispatch + weekly cron | **The full measurement.** Installs Checkov, tfsec, OPA, Terraform; runs `experiments/run_baselines.sh`; uploads `results/` as an artefact |
| `docs.yml` | PR/push touching `application/app/`, `docs/`, `jsdoc.json` | JSDoc build |
| `deploy-pages.yml` | push to main | GitHub Pages deployment |
| `release-please.yml` | push to main | Release automation; packages a replication archive |
| `update-data.yml` | schedule | SRO dataset refresh |

## Two invariants worth knowing before editing these

### 1. Never export `IACSECBENCH_ALLOW_SYNTHETIC` at job or workflow scope

Three stages in this repository do not execute a scanner. They multiply corpus
counts by hardcoded per-tool rates and write the product to the same paths a real
run uses:

- `evaluation/score.py`
- `pipeline/run_experiments.py`
- `experiments/generate_charts.py`

Each refuses unless `IACSECBENCH_ALLOW_SYNTHETIC=1` is set for that specific
invocation. `ci.yml` and `infra-ci.yml` previously exported it job-wide, which
switched the guard off for everything in the job — including the test that asserts
the guard works. Tests that need it set it per test.

`ci.yml` has a step that runs all three with the variable absent and fails if any
of them succeeds. If you find yourself wanting to set the variable to make a job
pass, the job is trying to publish fabricated numbers.

### 2. CI cannot produce publishable latency

Detection counts are deterministic and transfer between machines. Latency does not:
it reflects whatever else the host is doing. Measured locally on the same corpus,
Checkov's standard deviation was 155 ms on an idle machine and 897 ms under load —
a sixfold difference from the environment alone, with the mean barely moving.

`benchmark.yml` therefore uploads results as an **artefact** and never commits them.
Committing would replace locally measured latency, the only publishable kind, with
runner noise. Its job summary states this next to the numbers, so a reader meets the
caveat before the table.

## Where the expensive checks live

Corpus admissibility in Terraform mode runs `terraform init` and `validate` once per
case — the only check that catches a case referencing a resource type the provider
does not define, and roughly twenty minutes of work.

- `ci.yml` runs the **structural** variant: seconds, still catches a missing,
  contradictory, or ambiguous ground-truth label.
- `infra-ci.yml` runs the **Terraform** variant.
- `benchmark.yml` runs it as stage one of the full measurement.

## Tool versions

`benchmark.yml` and `infra-ci.yml` pin OPA and tfsec to the versions recorded in
`results/run_manifest.json`, which is the authoritative record of the published run.
When you bump a pin, expect detection results to move and re-measure — upstream rule
sets change independently of this repository, which is why `benchmark.yml` also runs
on a weekly schedule.

Note that OPA `1.9.0` and `1.19.0` are different releases and easy to transpose. The
manifest is the reference.
