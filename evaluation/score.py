"""DEPRECATED — derives a leaderboard from assumed accuracy rates.

This module does not evaluate any security tool. It multiplies the corpus class
counts by hardcoded per-tool rates (``"tp": int(insecure_count * 0.90)`` and
similar) and pins the reference implementation to a perfect score. The latency
column is a set of constants. Its output, ``leaderboard/results.synthetic.csv``,
is therefore a projection of its own assumptions, not a measurement. The measured
leaderboard is ``leaderboard/results.csv``, written by evaluation/analyze.py.

Replaced by the measuring pipeline:

    experiments/run_baselines.sh

which is built from evaluation/run_baselines.py (execution), evaluation/normalize.py
(finding normalization), evaluation/stats.py (exact intervals and tests) and
evaluation/analyze.py (aggregation and LaTeX emission).

To run this module anyway, set IACSECBENCH_ALLOW_SYNTHETIC=1.
"""

import csv
import json
import os
import sys
from pathlib import Path

# This module is executed directly (`python evaluation/score.py`), so the project
# root is not on sys.path yet and the intra-project imports below cannot resolve
# until it is. The insert therefore has to precede them, not follow them.
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# isort: off
from evaluation.metrics import calculate_metrics  # noqa: E402
from evaluation.synthetic_guard import GUARD_ENV as _GUARD_ENV  # noqa: E402
from evaluation.synthetic_guard import (  # noqa: E402
    refuse_unless_explicitly_allowed,
)

# isort: on


def _refuse_unless_explicitly_allowed() -> None:
    """Blocks accidental generation of a synthetic leaderboard."""
    refuse_unless_explicitly_allowed(
        "leaderboard metrics, with the reference tool pinned to a perfect score",
        writes="leaderboard/results.synthetic.csv",
        override_hint=f"{_GUARD_ENV}=1 python evaluation/score.py",
    )


def load_dataset(dataset_path: str) -> list[dict]:
    """Loads benchmark dataset from file or returns baseline suite."""
    if os.path.exists(dataset_path):
        with open(dataset_path, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("test_cases", [])
    return []


def run_benchmark_scoring() -> list[dict]:
    """Executes benchmark scoring protocol across tool profiles.

    Returns:
        List of tool metric dictionaries.
    """
    _refuse_unless_explicitly_allowed()
    dataset_file = ROOT / "benchmark" / "benchmark.json"
    if not dataset_file.exists():
        dataset_file = ROOT / "benchmark" / "datasets" / "benchmarks.json"

    cases = load_dataset(str(dataset_file))
    total_cases = len(cases) if cases else 300

    # Split cases into secure / insecure baseline counts if missing
    insecure_count = sum(
        1 for c in cases if c.get("expected_result") == "FAIL" or c.get("has_violation")
    )
    secure_count = total_cases - insecure_count

    if insecure_count == 0:
        insecure_count = 150
        secure_count = 150

    tool_profiles = [
        {
            "name": "Checkov",
            "category": "AST Static Analysis",
            "tp": int(insecure_count * 0.90),
            "fp": int(secure_count * 0.08),
            "tn": int(secure_count * 0.92),
            "fn": int(insecure_count * 0.10),
            "latency": 1420.0,
        },
        {
            "name": "tfsec",
            "category": "HCL Lexical Scanner",
            "tp": int(insecure_count * 0.88),
            "fp": int(secure_count * 0.06),
            "tn": int(secure_count * 0.94),
            "fn": int(insecure_count * 0.12),
            "latency": 310.0,
        },
        {
            "name": "OPA / Sentinel",
            "category": "Rego Policy Engine",
            "tp": int(insecure_count * 0.92),
            "fp": int(secure_count * 0.05),
            "tn": int(secure_count * 0.95),
            "fn": int(insecure_count * 0.08),
            "latency": 650.0,
        },
        {
            "name": "IaCSecBench Engine",
            "category": "Multi-Engine Validation",
            "tp": insecure_count,
            "fp": 0,
            "tn": secure_count,
            "fn": 0,
            "latency": 185.0,
        },
    ]

    metrics_list = []
    for profile in tool_profiles:
        m = calculate_metrics(
            tool_name=profile["name"],
            category=profile["category"],
            total_cases=total_cases,
            true_positives=profile["tp"],
            false_positives=profile["fp"],
            true_negatives=profile["tn"],
            false_negatives=profile["fn"],
            execution_time_ms=profile["latency"],
        )
        metrics_list.append(m.to_dict())

    # Write to results.synthetic.csv, NOT results.csv.
    #
    # This module used to write leaderboard/results.csv -- the same path
    # evaluation/analyze.py now writes from measured confusion matrices. The guard
    # above stops an accidental run, but a deliberate one still silently replaced
    # real measurements with assumed rates, and the two files are
    # indistinguishable afterwards. Separating the paths makes the collision
    # impossible rather than merely unlikely.
    leaderboard_dir = ROOT / "leaderboard"
    leaderboard_dir.mkdir(exist_ok=True)
    csv_file = leaderboard_dir / "results.synthetic.csv"

    fieldnames = [
        "tool_name",
        "category",
        "total_cases",
        "accuracy_pct",
        "precision_pct",
        "recall_pct",
        "f1_score_pct",
        "fpr_pct",
        "fnr_pct",
        "execution_time_ms",
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(metrics_list)

    print("============================================================")
    print("IaCSecBench Leaderboard & Evaluation Protocol Results")
    print("============================================================")
    print(
        f"{'Tool':<20} | {'Category':<22} | {'Recall':<8} | {'Precision':<10} | {'F1':<8} | {'Latency':<10}"
    )
    print("-" * 90)
    for m in metrics_list:
        print(
            f"{m['tool_name']:<20} | {m['category']:<22} | {m['recall_pct']:>6.1f}% | {m['precision_pct']:>8.1f}% | {m['f1_score_pct']:>6.1f}% | {m['execution_time_ms']:>8.1f} ms"
        )
    print("============================================================")
    print(f"✓ Leaderboard results saved to: {csv_file}")
    return metrics_list


if __name__ == "__main__":
    run_benchmark_scoring()
