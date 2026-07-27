"""Generate Visual & ASCII Benchmark Charts for Research & Documentation.

Generates detection accuracy and runtime performance comparison charts saved into results/charts/.
"""

import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from security_framework.engine.comparative_eval import ComparativeEvaluator


def generate_charts():
    """Generates ASCII and markdown figures for benchmark performance metrics."""
    evaluator = ComparativeEvaluator()
    results = evaluator.run_comparative_suite()

    charts_dir = os.path.join(PROJECT_ROOT, "results", "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # 1. Detection rate ASCII comparison chart
    detection_lines = [
        "============================================================",
        "Figure 1: Detection Rate Comparison Across IaC Security Tools",
        "============================================================\n",
    ]
    for r in results:
        bar_len = int(r.recall_pct / 10)
        bar = "█" * bar_len
        detection_lines.append(f"{r.tool_name:<20} {bar:<10} ({r.recall_pct:.1f}%)")

    detection_chart_str = "\n".join(detection_lines) + "\n"
    with open(os.path.join(charts_dir, "detection_comparison.txt"), "w", encoding="utf-8") as f:
        f.write(detection_chart_str)

    # 2. Runtime latency comparison chart
    runtime_lines = [
        "============================================================",
        "Figure 2: Execution Runtime Latency (ms) Comparison",
        "============================================================\n",
    ]
    max_latency = max(r.execution_time_ms for r in results)
    for r in results:
        bar_len = max(1, int((r.execution_time_ms / max_latency) * 20))
        bar = "█" * bar_len
        runtime_lines.append(f"{r.tool_name:<20} {bar:<20} ({r.execution_time_ms:.1f} ms)")

    runtime_chart_str = "\n".join(runtime_lines) + "\n"
    with open(os.path.join(charts_dir, "runtime_comparison.txt"), "w", encoding="utf-8") as f:
        f.write(runtime_chart_str)

    # 3. Save CSV metrics report
    csv_lines = ["Tool,Category,Cases,Accuracy,Precision,Recall,Latency_ms"]
    for r in results:
        csv_lines.append(
            f'"{r.tool_name}","{r.category}",{r.total_benchmark_cases},{r.accuracy_pct},{r.precision_pct},{r.recall_pct},{r.execution_time_ms}'
        )

    with open(os.path.join(PROJECT_ROOT, "results", "metrics.csv"), "w", encoding="utf-8") as f:
        f.write("\n".join(csv_lines) + "\n")

    print("[Charts] Generated detection_comparison.txt, runtime_comparison.txt, and metrics.csv in results/")


if __name__ == "__main__":
    generate_charts()
