# Contributing to IaCSecBench

Thank you for your interest in contributing to **IaCSecBench: An Infrastructure-as-Code Security Benchmark Framework**!

---

## 🚀 How to Contribute

We welcome contributions across several areas:

1. **Adding Benchmark Cases**: Add a case *specification* to `benchmark/generate_corpus.py` and regenerate, rather than hand-writing files under `benchmark/internal/cases/`. The generator is the source of truth; a hand-edited case drifts from its spec silently.
2. **Policy Extensions**: Adding OPA / Rego security policy rules under `security_framework/policies/`.
3. **Scanner & Metric Enhancements**: Extending normalization (`evaluation/normalize.py`), statistics (`evaluation/stats.py`), and the repository-edge engine under `security_framework/engine/`.
4. **Rule Mappings**: Mapping a scanner's native rule identifier onto a canonical control in `evaluation/control_map.json`. A new mapping needs evidence — either a citation to the tool's published rule list, or an observation recorded against a purpose-built case.
5. **Bug Reports & Feature Requests**: Submitting issues with reproducible steps.

---

## 🛠️ Local Development & Testing Workflow

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/mchittineni/iacsecbench.git
cd iacsecbench
python3 -m venv .venv
source .venv/bin/activate

pip install -r experiments/requirements.txt
pip install -e '.[dev]'      # the lint, type and security gates CI runs
pre-commit install
```

The scanners under comparison are **not** Python packages and are not installed by
the above. They are invoked as subprocesses and pinned in
`results/run_manifest.json`. Confirm what is visible before measuring:

```bash
python -m evaluation.run_baselines --list-tools
```

### 2. Run Quality Checks & Tests

Before submitting a Pull Request, ensure these pass cleanly. They are the same
checks `ci.yml` runs, so a clean local run means a clean PR.

```bash
# 1. Lint and format
ruff check . && ruff format --check .
flake8 security_framework evaluation experiments benchmark scripts

# 2. Security audit
bandit -c pyproject.toml -r security_framework/ evaluation/ experiments/ benchmark/ scripts/

# 3. Test suite
pytest security_framework/tests/ evaluation/tests/ -v --cov=security_framework

# 4. Corpus admission gate (structural: seconds, no Terraform required)
python -m evaluation.corpus --report --mode structural

# 5. Figure sources still match the recorded results
python -m experiments.generate_figures --check

# 6. The fabricating stages must still refuse to run unasked
python evaluation/score.py            # must exit non-zero
IACSECBENCH_ALLOW_SYNTHETIC=1 python evaluation/score.py

# 7. All hooks, as the pre-commit gate will run them
pre-commit run --all-files
```

If you changed the corpus, the control map, or a policy, the recorded results no
longer describe the code and must be regenerated:

```bash
python -m evaluation.corpus --report --mode terraform   # authoritative gate
./experiments/run_baselines.sh                          # full measurement
```

Measure on an **idle machine**. Latency is contaminated by background load, and
the run manifest records the host, so a contaminated run is published as though
it were clean.

If you changed `infrastructure/`:

```bash
cd infrastructure && terraform test
```

---

## 📋 Pull Request Submission Guidelines

1. **Commit Message Format**: Use clear, imperative titles (e.g., `feat(benchmark): add S3 ACL vulnerability scenario`).
2. **Never Hand-Edit a Measurement**: Everything under `results/` and `leaderboard/results.csv` is written by `evaluation/analyze.py` from recorded scanner output. Editing one by hand — even to correct what looks like an obvious mistake — converts a measurement into an assertion. Re-measure instead.
3. **Zero-PII Compliance**: Ensure no customer names, personal phone numbers, or real identities are added to code or corpus files.
4. **Tests Required**: Every bugfix or feature must include corresponding test cases under `evaluation/tests/` or `security_framework/tests/`.
5. **Claims Need Evidence**: If a change alters a number the manuscript reports, update `paper/` in the same PR and say which artefact under `results/` the new number comes from.
6. **Documentation**: Update markdown documentation under `docs/framework/` if introducing new CLI flags or metrics.
