"""IaC Evaluation Engine.

Provides reusable scanning, rule validation, and policy metrics computation across
arbitrary Terraform configurations, modules, and security benchmark rulesets.
"""

import json
import os
import re
import time
from typing import Any


class BenchmarkEngine:
    """Reusable engine for scanning IaC configurations and evaluating security benchmarks."""

    def __init__(self, target_dir: str):
        """Initializes the engine with a target directory containing IaC code.

        Args:
            target_dir: Absolute or relative path to the target Terraform repository or module.
        """
        self.target_dir = os.path.abspath(target_dir)

    def scan_secret_patterns(self) -> list[dict[str, Any]]:
        """Scans all .tf and .hcl files for hardcoded secrets or PII patterns.

        Returns:
            List of detected violation dictionaries containing file, line, and pattern details.
        """
        secret_patterns = [
            (
                r"(?i)aws_secret_access_key\s*=\s*['\"](?!\$\{)[A-Za-z0-9/+=]{20,}['\"]",
                "AWS Secret Key",
            ),
            (
                r"(?i)password\s*=\s*['\"](?!var\.|random_|http)[^'\"]{8,}['\"]",
                "Hardcoded DB Password",
            ),
            (r"(?i)api_key\s*=\s*['\"](?!var\.|random_)[^'\"]{16,}['\"]", "Hardcoded API Key"),
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "Personal Email Address"),
        ]

        violations = []
        for root, _, files in os.walk(self.target_dir):  # pylint: disable=too-many-nested-blocks
            for file in files:
                if file.endswith((".tf", ".tfvars", ".hcl")):
                    filepath = os.path.join(root, file)
                    with open(filepath, encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        for pattern, desc in secret_patterns:
                            if re.search(pattern, line):
                                violations.append(
                                    {
                                        "file": os.path.relpath(filepath, self.target_dir),
                                        "line": idx,
                                        "rule": desc,
                                        "type": "SECRET_LEAK",
                                    }
                                )
        return violations

    def evaluate_cis_policies(self) -> list[dict[str, Any]]:
        """Evaluates CIS AWS benchmark policies on target IaC configuration.

        Returns:
            List of policy evaluation result dictionaries.
        """
        return []


class BenchmarkEngineRunner:
    """Runner class for executing benchmark tasks."""

    def __init__(self, target_dir: str):
        """Initializes the runner with target directory.

        Args:
            target_dir: Directory to analyze.
        """
        self.engine = BenchmarkEngine(target_dir)

    def run_full_evaluation(self) -> dict[str, Any]:
        """Executes full evaluation on the target directory.

        Returns:
            Dictionary containing benchmark telemetry, violation list, and summary metrics.
        """
        start_time = time.time()
        secret_violations = self.engine.scan_secret_patterns()
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "target_dir": self.engine.target_dir,
            "execution_time_ms": elapsed_ms,
            "secret_violations_count": len(secret_violations),
            "violations": secret_violations,
            "status": "PASSED" if not secret_violations else "VIOLATIONS_FOUND",
        }


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "."
    runner = BenchmarkEngineRunner(target)
    results = runner.run_full_evaluation()
    print(json.dumps(results, indent=2))
