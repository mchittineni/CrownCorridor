# IaCSecBench — Documentation

An open framework and empirical benchmark for evaluating Infrastructure-as-Code
security gates.

## Start here

- [Benchmark protocol](benchmark_protocol.md) — how a measurement run is defined and reproduced
- [Control taxonomy](taxonomy.md) — the canonical controls scanner output is normalized onto
- [Framework documentation](framework/README.md) — architecture, methodology, metrics, threat model

## Reproducing a measurement

```bash
python -m evaluation.corpus --report --mode terraform   # corpus admissibility
./experiments/run_baselines.sh                          # full measurement
python -m experiments.generate_figures                  # regenerate figure sources
```

Results land in `results/` — `evaluation.json` for the machine-readable result
set, `tables/*.tex` for the manuscript, and `raw/<tool>/` for unmodified scanner
output. Nothing in the paper is hand-copied from a run; every figure and table is
generated from those files.

## The manuscript

`paper/` holds the LaTeX source and its generated figures. See
`paper/README.md` for the build, and `paper/figures/README.md` for how the two
diagrams are generated and rendered.
