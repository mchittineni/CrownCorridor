# Workflows

| Workflow             | Trigger                                                                                                                | Purpose                                                                                                                                                                                                          |
| :------------------- | :--------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ci.yml`             | every PR + push to main                                                                                                | Lint, format, security audit, unit tests, data validation, fast corpus check, synthetic-guard assertion                                                                                                          |
| `infra-ci.yml`       | PR/push touching `infrastructure/`, `security_framework/`, `benchmark/`, `evaluation/`, `leaderboard/`, `experiments/` | Terraform fmt/validate/test, conftest policy evaluation, Checkov scan, Rego parse + format, corpus admissibility, tests                                                                                          |
| `benchmark.yml`      | manual dispatch + weekly cron                                                                                          | **The full measurement.** Installs Checkov, tfsec, Trivy, OPA, Terraform; runs `experiments/run_baselines.sh`; checks the manuscript's figure sources still match the results; uploads `results/` as an artefact |
| `docs.yml`           | PR/push touching `application/app/`, `docs/`, `jsdoc.json`                                                             | JSDoc build                                                                                                                                                                                                      |
| `deploy-pages.yml`   | push to main                                                                                                           | GitHub Pages deployment                                                                                                                                                                                          |
| `release-please.yml` | push to main                                                                                                           | Release automation; packages a replication archive                                                                                                                                                               |
| `update-data.yml`    | schedule                                                                                                               | SRO dataset refresh                                                                                                                                                                                              |

## Three invariants worth knowing before editing these

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

## The figure-source gate

`benchmark.yml` runs `python -m experiments.generate_figures --check` after the
harness. The manuscript's two diagrams carry the corpus size and the resolved tool
versions, and their Mermaid sources are generated from `results/evaluation.json` and
`results/run_manifest.json`. A re-measurement that moves any of those values makes
the committed sources stale, so the job fails and names the fix.

This exists because an earlier hand-drawn figure set claimed 345 cases, listed a
scanner the paper excludes, omitted one it evaluates, and quoted four tool versions
that no longer matched the manifest. None of it was detectable from the figures,
because they had no source in the repository.

`benchmark.yml` therefore uploads results as an **artefact** and never commits them.
Committing would replace locally measured latency, the only publishable kind, with
runner noise. Its job summary states this next to the numbers, so a reader meets the
caveat before the table.

### 3. A `workflow_dispatch` input never appears inside a command

Bind it to `env:` and reference the variable, then validate it before use.
`update-data.yml` used to interpolate its `date` input into a command string that
`.github/actions/datagov-fetch` splices into a `run:` block — two hops from a
dispatch field to a shell, which let anyone able to dispatch the workflow run
arbitrary commands. It now rejects anything that is not a real calendar date and
passes the flag through `$SRO_DATE_FLAG`. `benchmark.yml` validates its `repeats`
and `level` inputs the same way.

This applies to `github.event.*` fields generally, not just dispatch inputs — issue
titles, branch names and commit messages are all attacker-controlled.

## Checks that cannot fail are removed, not repointed

`ci.yml` used to run `doc8` over `docs/`, `README.md` and `CONTRIBUTING.md`. doc8
reads only `.rst` and `.txt`; every path named was Markdown, so the step passed
without opening a file, and the matching pre-commit hook reported
`(no files to check) Skipped` on every run. Both are gone. A green check that
inspects nothing is worse than an absent one, because it occupies the slot where a
missing check would be noticed.

Markdown style is enforced instead by `prettier`, which `npm run format:check`
covers. `.prettierignore` excludes `CHANGELOG.md` (written by release-please),
generated JSDoc output, and `results/`+`leaderboard/` (measured artefacts compared
byte-for-byte across runs, which reformatting would corrupt).

## Where the expensive checks live

Corpus admissibility in Terraform mode runs `terraform init` and `validate` once per
case — the only check that catches a case referencing a resource type the provider
does not define, and roughly twenty minutes of work.

- `ci.yml` runs the **structural** variant: seconds, still catches a missing,
  contradictory, or ambiguous ground-truth label.
- `infra-ci.yml` runs the **Terraform** variant.
- `benchmark.yml` runs it as stage one of the full measurement.

## Tool versions

`benchmark.yml` and `infra-ci.yml` pin OPA, tfsec and Trivy to the versions recorded
in `results/run_manifest.json`, which is the authoritative record of the published run.
When you bump a pin, expect detection results to move and re-measure — upstream rule
sets change independently of this repository, which is why `benchmark.yml` also runs
on a weekly schedule.

Note that OPA `1.9.0` and `1.19.0` are different releases and easy to transpose. The
manifest is the reference.

Trivy needs its checks bundle cached before the measurement, because the harness runs
it with `--skip-check-update` — an uncached run would either charge a registry fetch to
scanner latency or, on a fetch failure, record every case as clean. `benchmark.yml` warms
the cache and then verifies it by running the harness's exact command and failing if it
reports zero findings.

The tfsec pin is deliberately kept alongside Trivy rather than replaced by it. tfsec is
retired and Trivy is its successor, and measuring both is what lets the benchmark report
how far the shared rule set has drifted between the two products.
