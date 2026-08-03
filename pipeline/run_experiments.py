"""Reproducible Experiment Runner.

Executes comparative benchmarks across IaC security tools and outputs telemetry data
and markdown summary reports for reproducibility.
"""

import json
import os
import sys
import time
from typing import Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from evaluation.score import run_benchmark_scoring
from evaluation.synthetic_guard import GUARD_ENV, refuse_unless_explicitly_allowed
from security_framework.engine.comparative_eval import ComparativeEvaluator
from security_framework.engine.engine import BenchmarkEngineRunner

# Output paths are module constants rather than expressions inlined at the write
# site so a test can redirect them. A test that exercises this stage otherwise
# overwrites the repository's real result files with fabricated ones as a side
# effect -- the same hazard the synthetic guard exists to prevent, arriving
# through the test suite instead of through run_all.sh.
EXPERIMENT_RESULTS_PATH = os.path.join(
    PROJECT_ROOT, "benchmark", "reports", "experiment_results.json"
)
BENCHMARK_RESULTS_PATH = os.path.join(PROJECT_ROOT, "results", "benchmark_results.json")


def run_experiments() -> dict[str, Any]:
    """Runs all benchmark experiment suites and gathers execution telemetry.

    Returns:
        Dictionary containing experiment telemetry, comparative metrics, and environment details.
    """
    # The comparative stage below does not execute Checkov, tfsec or OPA. It
    # multiplies corpus counts by the hardcoded profile rates in
    # ComparativeEvaluator.run_comparative_suite and writes the product to
    # results/benchmark_results.json -- a filename a reader has every reason to
    # take for measured output. Gate it before anything is written, not after.
    refuse_unless_explicitly_allowed(
        "comparative tool metrics from hardcoded per-tool profile rates",
        writes="results/benchmark_results.json, benchmark/reports/experiment_results.json",
        override_hint=f"{GUARD_ENV}=1 python pipeline/run_experiments.py",
    )
    print("============================================================")
    print("IaC Security Benchmark Framework — Reproducible Experiments")
    print("============================================================\n")

    start_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # 1. Target repository scanning experiment
    print("[1] Running Benchmark Engine scan on infrastructure/ directory...")
    infra_dir = os.path.join(PROJECT_ROOT, "infrastructure")
    runner = BenchmarkEngineRunner(infra_dir)
    engine_results = runner.run_full_evaluation()
    print(f"    ✓ Scan finished in {engine_results['execution_time_ms']} ms")
    print(f"    ✓ Violations detected: {engine_results['secret_violations_count']}\n")

    # 2. Comparative tool evaluation experiment
    print("[2] Running Comparative Tool Benchmark (Checkov, tfsec, Sentinel, Terratest)...")
    benchmark_dataset_path = os.path.join(PROJECT_ROOT, "benchmark", "datasets", "benchmarks.json")
    if not os.path.exists(benchmark_dataset_path):
        benchmark_dataset_path = os.path.join(PROJECT_ROOT, "data", "benchmarks", "benchmarks.json")
    evaluator = ComparativeEvaluator(benchmark_dataset_path)
    tool_results = evaluator.run_comparative_suite()

    print(f"    ✓ Evaluated {len(tool_results)} tools against benchmark dataset.")
    for res in tool_results:
        print(
            f"      - {res.tool_name:<30} | Acc: {res.accuracy_pct:>5.1f}% | Latency: {res.execution_time_ms:>6.1f} ms"
        )

    # 3. Leaderboard scoring protocol
    print("\n[3] Running Evaluation Protocol & Leaderboard Scoring...")
    leaderboard_metrics = run_benchmark_scoring()

    # 4. Output artifact generation
    output_data = {
        "timestamp": start_timestamp,
        "engine_scan": engine_results,
        "comparative_benchmarks": [r.__dict__ for r in tool_results],
        "leaderboard_metrics": leaderboard_metrics,
        "markdown_matrix": evaluator.generate_comparison_matrix_markdown(),
    }

    for path in (EXPERIMENT_RESULTS_PATH, BENCHMARK_RESULTS_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)

    print(
        "\n[3] Experiment telemetry saved to: benchmark/reports/experiment_results.json & results/benchmark_results.json"
    )
    print("\n============================================================")
    print("EXPERIMENTS COMPLETED SUCCESSFULLY ✓")
    print("============================================================")
    return output_data


if __name__ == "__main__":
    run_experiments()
