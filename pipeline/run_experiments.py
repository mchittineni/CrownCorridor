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

from security_framework.engine.comparative_eval import ComparativeEvaluator
from security_framework.engine.engine import BenchmarkEngineRunner


def run_experiments() -> dict[str, Any]:
    """Runs all benchmark experiment suites and gathers execution telemetry.

    Returns:
        Dictionary containing experiment telemetry, comparative metrics, and environment details.
    """
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

    # 3. Output artifact generation
    output_data = {
        "timestamp": start_timestamp,
        "engine_scan": engine_results,
        "comparative_benchmarks": [r.__dict__ for r in tool_results],
        "markdown_matrix": evaluator.generate_comparison_matrix_markdown(),
    }

    results_path = os.path.join(PROJECT_ROOT, "benchmark", "reports", "experiment_results.json")
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    res_alt_path = os.path.join(PROJECT_ROOT, "results", "benchmark_results.json")
    os.makedirs(os.path.dirname(res_alt_path), exist_ok=True)
    with open(res_alt_path, "w", encoding="utf-8") as f:
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
