"""DEPRECATED — derives a leaderboard from assumed accuracy rates.

This module does not evaluate any security tool. It multiplies the corpus class
counts by hardcoded per-tool rates (``"tp": int(insecure_count * 0.90)`` and
similar) and pins the reference implementation to a perfect score. The latency
column is a set of constants. The resulting ``leaderboard/results.csv`` is
therefore a projection of its own assumptions, not a measurement.

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

_GUARD_ENV = "IACSECBENCH_ALLOW_SYNTHETIC"


def _refuse_unless_explicitly_allowed() -> None:
    """Blocks accidental generation of a synthetic leaderboard."""
    if os.environ.get(_GUARD_ENV) == "1":
        print(
            f"WARNING: {_GUARD_ENV}=1 -- emitting a SYNTHETIC leaderboard derived from "
            "assumed accuracy rates. Not a measurement; must not be published.",
            file=sys.stderr,
        )
        return
    sys.exit(
        "refusing to run: this module fabricates leaderboard metrics.\n"
        "  Tool scores are corpus counts multiplied by hardcoded rates; no scanner\n"
        "  is executed and the reference tool is pinned to 100%.\n\n"
        "  Measure instead:  experiments/run_baselines.sh\n"
        f"  Override (not for publication):  {_GUARD_ENV}=1 python evaluation/score.py"
    )

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from evaluation.metrics import calculate_metrics  # isort: skip # pylint: disable=wrong-import-order


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

    # Write leaderboard results.csv
    leaderboard_dir = ROOT / "leaderboard"
    leaderboard_dir.mkdir(exist_ok=True)
    csv_file = leaderboard_dir / "results.csv"

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
