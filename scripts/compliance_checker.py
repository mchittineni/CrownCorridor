#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

FRAMEWORKS = ["soc2", "pci-dss", "hipaa", "gdpr"]

CHECKS = {
    "soc2": [
        ("security_policy", ["SECURITY.md", "security_framework"]),
        ("ci_security_checks", [".github/workflows/ci.yml"]),
        ("precommit_hooks", [".pre-commit-config.yaml"]),
        ("secret_scanning", ["security_framework/engine/engine.py"]),
    ],
    "pci-dss": [
        ("security_policy", ["SECURITY.md"]),
        ("ci_security_checks", [".github/workflows/ci.yml"]),
        ("no_debug_builds", [".github/workflows/ci.yml"]),
        ("dependency_audit", ["package-lock.json", "pyproject.toml"]),
    ],
    "hipaa": [
        ("security_policy", ["SECURITY.md"]),
        ("ci_security_checks", [".github/workflows/ci.yml"]),
        ("data_protection", ["security_framework"]),
    ],
    "gdpr": [
        ("privacy_policy", ["SECURITY.md"]),
        ("data_inventory", ["benchmark/", "infrastructure/"]),
        ("incident_response", ["SECURITY.md"]),
    ],
}


def check_path_exists(path):
    if isinstance(path, (list, tuple)):
        return any(check_path_exists(item) for item in path)
    if isinstance(path, Path):
        return path.exists()
    return Path(path).exists()


def evaluate_framework(framework, root):
    checks = CHECKS.get(framework, [])
    passed = 0
    details = []
    for label, paths in checks:
        existing = False
        for candidate in paths:
            if check_path_exists(root / candidate):
                existing = True
                break
        if existing:
            passed += 1
            details.append({"check": label, "status": "pass", "target": paths})
        else:
            details.append({"check": label, "status": "fail", "target": paths})
    score = int((passed / len(checks)) * 100) if checks else 0
    if score >= 90:
        status = "compliant"
    elif score >= 50:
        status = "non-compliant"
    else:
        status = "critical"
    return {"framework": framework, "score": score, "status": status, "details": details}


def render_text(result):
    lines = [
        f"Compliance Checker Report for {result['framework'].upper()}",
        f"Status: {result['status']}",
        f"Score: {result['score']}%",
        "",
    ]
    for detail in result["details"]:
        lines.append(f"- {detail['check']}: {detail['status']} ({', '.join(detail['target'])})")
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description="Compliance checker stub for standard frameworks.")
    parser.add_argument("target", nargs="?", default=".", help="Repository root path.")
    parser.add_argument(
        "--framework", choices=FRAMEWORKS, required=True, help="Compliance framework to evaluate."
    )
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--output", type=Path, help="Write the report to a file.")
    return parser.parse_args()


def main():
    args = parse_args()
    root = Path(args.target)
    result = evaluate_framework(args.framework, root)
    if args.json:
        output = json.dumps(result, indent=2)
    else:
        output = render_text(result)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)
    if result["status"] == "critical":
        sys.exit(2)
    if result["status"] == "non-compliant":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
