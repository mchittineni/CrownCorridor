"""DEPRECATED — synthesises baseline results from assumed accuracy rates.

This script does not execute Checkov, tfsec or OPA. It fabricates a
per-case outcome vector for each tool from a hardcoded recall constant using
``detected = (idx % 100) < int(recall_rate * 100)``, and hardcodes the reference
implementation at recall 1.00 with a 0.00 false-positive rate. The latency values
are likewise constants, not measurements.

Output from this script must never be reported as an experimental result. It is
retained only so that previously published figures can be traced to their origin.

The replacement measures real tool behaviour:

    experiments/run_baselines.sh

which executes each installed scanner over the admissible corpus, records raw
output and per-execution wall-clock samples, and refuses to emit a table when no
case is admissible. See evaluation/run_baselines.py.

To run this script anyway, set IACSECBENCH_ALLOW_SYNTHETIC=1. The guard exists
because the generated files are indistinguishable from measured ones once
written to disk.
"""

import json
import os
import sys

_GUARD_ENV = "IACSECBENCH_ALLOW_SYNTHETIC"


def _refuse_unless_explicitly_allowed():
    """Blocks accidental generation of synthetic results."""
    if os.environ.get(_GUARD_ENV) == "1":
        print(
            f"WARNING: {_GUARD_ENV}=1 -- generating SYNTHETIC results from assumed "
            "accuracy rates. These are not measurements and must not be published.",
            file=sys.stderr,
        )
        return
    sys.exit(
        "refusing to run: this script fabricates benchmark results.\n"
        "  It does not invoke any scanner; outcomes come from hardcoded recall\n"
        "  constants and the reference tool is pinned to a perfect score.\n\n"
        "  Measure instead:  experiments/run_baselines.sh\n"
        f"  Override (not for publication):  {_GUARD_ENV}=1 python "
        "scratch/generate_golden_results.py"
    )


def generate_golden_results():
    _refuse_unless_explicitly_allowed()
    with open("benchmark/benchmark.json", encoding="utf-8") as f:
        catalog = json.load(f)

    cases = catalog.get("test_cases", [])
    total_cases = len(cases)
    golden_dir = "benchmark/golden_results"
    os.makedirs(golden_dir, exist_ok=True)

    tools = [
        ("checkov", "Checkov", 0.90, 0.08, 1420.0),
        ("tfsec", "tfsec", 0.88, 0.06, 310.0),
        ("opa", "OPA / Sentinel", 0.92, 0.05, 650.0),
        ("iacsecbench", "IaCSecBench Engine", 1.00, 0.00, 185.0),
    ]

    for file_prefix, tool_name, recall_rate, fp_rate, latency in tools:
        results = []
        for idx, case in enumerate(cases):
            expected = case["expected_result"]
            if expected == "FAIL":
                detected = (idx % 100) < int(recall_rate * 100)
                fp = False
            else:
                detected = False
                fp = (idx % 100) < int(fp_rate * 100)

            results.append(
                {
                    "benchmark_id": case["id"],
                    "category": case["benchmark_category"],
                    "expected_result": expected,
                    "tool_detected": detected or fp,
                    "is_true_positive": detected and expected == "FAIL",
                    "is_false_positive": fp and expected == "PASS",
                    "is_true_negative": (not fp) and expected == "PASS",
                    "is_false_negative": (not detected) and expected == "FAIL",
                }
            )

        output_data = {
            "tool_name": tool_name,
            "total_benchmark_cases": total_cases,
            "execution_time_ms": latency,
            "results": results,
        }

        with open(os.path.join(golden_dir, f"{file_prefix}.json"), "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)

    print(f"✓ Generated golden reference results in {golden_dir}/")


if __name__ == "__main__":
    generate_golden_results()
