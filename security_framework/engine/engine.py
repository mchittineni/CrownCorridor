"""IaC Evaluation Engine.

Provides reusable scanning, rule validation, and policy metrics computation across
arbitrary Terraform configurations, modules, and security benchmark rulesets.
"""

import json
import math
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

    def _is_high_entropy_secret(self, value: str) -> bool:
        if len(value) < 20:
            return False
        freq = {}
        for char in value:
            freq[char] = freq.get(char, 0) + 1
        entropy = -sum((count / len(value)) * math.log2(count / len(value)) for count in freq.values())
        return entropy >= 3.5 and len(set(value)) >= 8

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
                r"(?i)aws_access_key_id\s*=\s*['\"](?!\$\{)[A-Za-z0-9/+=]{16,}['\"]",
                "AWS Access Key ID",
            ),
            (
                r"(?i)password\s*=\s*['\"](?!var\.|random_|http)[^'\"]{8,}['\"]",
                "Hardcoded DB Password",
            ),
            (
                r"(?i)api_key\s*=\s*['\"](?!var\.|random_)[^'\"]{16,}['\"]",
                "Hardcoded API Key",
            ),
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "Personal Email Address"),
        ]

        allowlist = [r"\bvar\.\b", r"\bmodule\.\b", r"\brandom_", r"\bhttp", r"\$\{"]

        violations = []
        for root, _, files in os.walk(self.target_dir):  # pylint: disable=too-many-nested-blocks
            for file in files:
                if file.endswith((".tf", ".tfvars", ".hcl")):
                    filepath = os.path.join(root, file)
                    with open(filepath, encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        stripped = line.strip()
                        if stripped.startswith("#") or stripped.startswith("//"):
                            continue
                        line_has_secret = False
                        for pattern, desc in secret_patterns:
                            if re.search(pattern, line):
                                if any(re.search(allow, line) for allow in allowlist):
                                    continue
                                line_has_secret = True
                                violations.append(
                                    {
                                        "file": os.path.relpath(filepath, self.target_dir),
                                        "line": idx,
                                        "rule": desc,
                                        "type": "SECRET_LEAK",
                                    }
                                )
                        if line_has_secret:
                            continue

                        for literal in re.findall(r'["\']([^"\']{20,})["\']', line):
                            if any(re.search(allow, literal) for allow in allowlist):
                                continue
                            if self._is_high_entropy_secret(literal):
                                violations.append(
                                    {
                                        "file": os.path.relpath(filepath, self.target_dir),
                                        "line": idx,
                                        "rule": "High Entropy Secret",
                                        "type": "SECRET_LEAK",
                                    }
                                )
                                break
        return violations

    def evaluate_cis_policies(self) -> list[dict[str, Any]]:
        """Evaluates CIS AWS benchmark policies on target IaC configuration.

        Returns:
            List of policy evaluation result dictionaries.
        """
        violations = []
        tf_contents = []
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith((".tf", ".tfvars", ".hcl")):
                    filepath = os.path.join(root, file)
                    with open(filepath, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    tf_contents.append((filepath, content))

        if not tf_contents:
            return []

        if not tf_contents:
            return []

        if not tf_contents:
            return []

        if not tf_contents:
            return []

        if not tf_contents:
            return []

        if not tf_contents:
            return []

        if not tf_contents:
            return []

        if not tf_contents:
            return []

        if not tf_contents:
            return []
        combined_code = "\n".join(content for _, content in tf_contents)

        def _matches(pattern: str) -> bool:
            return bool(re.search(pattern, combined_code, flags=re.IGNORECASE))

        if not _matches(r"aws_s3_bucket_public_access_block"):
            violations.append(
                {
                    "rule": "CIS 2.1",
                    "description": "Missing S3 public access block configuration.",
                    "type": "CIS_AWS",
                }
            )
        if not _matches(r"aws_s3_bucket_versioning"):
            violations.append(
                {
                    "rule": "CIS 2.1.3",
                    "description": "S3 buckets must enforce versioning.",
                    "type": "CIS_AWS",
                }
            )
        if not _matches(r"server_side_encryption_configuration"):
            violations.append(
                {
                    "rule": "CIS 2.1",
                    "description": "S3 buckets must enforce server-side encryption.",
                    "type": "CIS_AWS",
                }
            )
        if not _matches(r"aws_db_instance"):
            violations.append(
                {
                    "rule": "CIS 2.3",
                    "description": "RDS instance configuration not found.",
                    "type": "CIS_AWS",
                }
            )
        elif not _matches(r"storage_encrypted\s*=\s*true"):
            violations.append(
                {
                    "rule": "CIS 2.3",
                    "description": "RDS instances must enforce storage_encrypted = true.",
                    "type": "CIS_AWS",
                }
            )
        if not _matches(r"publicly_accessible\s*=\s*false"):
            violations.append(
                {
                    "rule": "CIS 2.3",
                    "description": "RDS instances must not be publicly accessible.",
                    "type": "CIS_AWS",
                }
            )
        if not _matches(r"aws_cloudtrail"):
            violations.append(
                {
                    "rule": "CIS 3.2",
                    "description": "CloudTrail configuration not found.",
                    "type": "CIS_AWS",
                }
            )
        elif not _matches(r"enable_log_file_validation\s*=\s*true"):
            violations.append(
                {
                    "rule": "CIS 3.2",
                    "description": "CloudTrail must enable log file validation.",
                    "type": "CIS_AWS",
                }
            )
        if not _matches(r"aws_guardduty_detector"):
            violations.append(
                {
                    "rule": "CIS 4.1",
                    "description": "GuardDuty detector must be enabled.",
                    "type": "CIS_AWS",
                }
            )
        if not _matches(r"aws_securityhub_account"):
            violations.append(
                {
                    "rule": "CIS 4.2",
                    "description": "Security Hub account must be enabled.",
                    "type": "CIS_AWS",
                }
            )
        if not _matches(r"aws_flow_log"):
            violations.append(
                {
                    "rule": "CIS 3.9",
                    "description": "VPC Flow Logs must be enabled.",
                    "type": "CIS_AWS",
                }
            )
        if _matches(r"aws_cloudfront_distribution") and not _matches(r"viewer_protocol_policy\s*=\s*\"redirect-to-https\""):
            violations.append(
                {
                    "rule": "CIS 2.4",
                    "description": "CloudFront must enforce redirect-to-https.",
                    "type": "CIS_AWS",
                }
            )

        if _matches(r"mfa_configuration\s*=\s*\"OPTIONAL\"|mfa_configuration\s*=\s*\"OFF\""):
            violations.append(
                {
                    "rule": "AUTH-001",
                    "description": "Cognito user pool should require MFA for stronger authentication.",
                    "type": "AUTHENTICATION",
                }
            )

        return violations


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
        cis_violations = self.engine.evaluate_cis_policies()
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        status = "PASSED"
        if secret_violations or cis_violations:
            status = "VIOLATIONS_FOUND"

        return {
            "target_dir": self.engine.target_dir,
            "execution_time_ms": elapsed_ms,
            "secret_violations_count": len(secret_violations),
            "cis_violations_count": len(cis_violations),
            "secret_violations": secret_violations,
            "cis_violations": cis_violations,
            "status": status,
        }


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "."
    runner = BenchmarkEngineRunner(target)
    results = runner.run_full_evaluation()
    print(json.dumps(results, indent=2))
