# Pull Request — IaCSecBench

## Summary of Changes

Provide a clear description of what this PR introduces or fixes.

-

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change fixing an issue)
- [ ] ✨ New feature (non-breaking change adding functionality)
- [ ] 🔬 IaCSecBench Benchmark Framework (security engine, policy, or scenario addition)
- [ ] 🧪 Corpus or control map change (new cases, new controls, rule mappings)
- [ ] 📊 Re-measurement (regenerated `results/`, no change to what is measured)
- [ ] ⚙️ Maintenance / Config (workflow, linter, dependencies, Docker)
- [ ] 📚 Documentation update

## Related Issues

Closes #

## Pre-Commit Verification Checklist

Before submitting this PR, verify that all quality checks pass locally:

- [ ] `.venv/bin/ruff check .` && `.venv/bin/ruff format --check .` (Ruff clean)
- [ ] `.venv/bin/pytest -q` (All tests passing)
- [ ] `python3 -m evaluation.corpus --report --mode structural` (Corpus admissible; seconds, no Terraform)
- [ ] `python3 -m experiments.generate_figures --check` (Figure sources match the recorded results)
- [ ] Fabricating stages still refuse: `python3 evaluation/score.py` must exit non-zero without `IACSECBENCH_ALLOW_SYNTHETIC=1`
- [ ] _Only if you changed `infrastructure/`:_ `terraform test` passes and the `.tftest.hcl` line count the paper reports is unchanged
- [ ] _Only if you changed the corpus, control map, or a policy:_ `experiments/run_baselines.sh` and commit the regenerated `results/` and `leaderboard/results.csv`. Measure on an idle machine — latency is contaminated by background load.
- [ ] _Only if you changed `paper/`:_ `make -C paper` typesets cleanly and every number traces to a file under `results/`

## Testing Instructions

Explain how reviewers can test your changes locally:

1. `python3 -m evaluation.corpus --report --mode structural` (Fast structural admissibility check)
2. `experiments/run_baselines.sh` (Full measurement: needs Checkov, tfsec, Trivy, OPA and Terraform; tens of minutes)
3. `python3 -m experiments.fetch_external --check` (Pinned third-party subset is at the recorded commits)
