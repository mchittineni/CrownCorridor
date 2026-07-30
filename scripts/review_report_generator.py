#!/usr/bin/env python3
import argparse
import json
import subprocess  # nosec B404
import sys
from pathlib import Path

SCRIPTS = [
    "scripts/security_scanner.py",
    "scripts/code_quality_checker.py",
    "scripts/pr_analyzer.py",
    "scripts/compliance_checker.py",
]


def run_command(command):
    result = subprocess.run(  # nosec B603
        command,
        shell=False,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def get_report(report_entry):
    if isinstance(report_entry, dict):
        if "report" in report_entry:
            return report_entry["report"]
        return report_entry
    return report_entry


def generate_markdown(report_data):
    lines = [
        f"# Review Report for {report_data['target']}",
        "",
    ]

    security_report = get_report(report_data.get("security", {}))
    if security_report and "error" not in security_report:
        lines.extend(
            [
                "## Security Scanner",
                f"- Risk: {security_report.get('risk', 'unknown')}",
                f"- Findings: {security_report.get('total_findings', 'unknown')}",
                "",
            ]
        )
    elif security_report.get("error"):
        lines.extend(["## Security Scanner", f"- Error: {security_report['error']}", ""])

    quality_report = get_report(report_data.get("quality", {}))
    if quality_report and "error" not in quality_report:
        lines.extend(
            [
                "## Code Quality Checker",
                f"- Language: {quality_report.get('language', 'unknown')}",
                f"- Total issues: {quality_report.get('total_issues', 'unknown')}",
                "",
            ]
        )
    elif quality_report.get("error"):
        lines.extend(["## Code Quality Checker", f"- Error: {quality_report['error']}", ""])

    pr_report = get_report(report_data.get("pr", {}))
    if pr_report and "error" not in pr_report:
        lines.extend(
            [
                "## PR Analyzer",
                f"- Complexity score: {pr_report.get('complexity_score', 'unknown')}/10",
                f"- Risk: {pr_report.get('risk', 'unknown')}",
                "",
            ]
        )
    elif pr_report.get("error"):
        lines.extend(["## PR Analyzer", f"- Error: {pr_report['error']}", ""])

    compliance_report = get_report(report_data.get("compliance", {}))
    if compliance_report and "error" not in compliance_report:
        lines.extend(
            [
                "## Compliance Checker",
                f"- Framework: {compliance_report.get('framework', 'unknown')}",
                f"- Status: {compliance_report.get('status', 'unknown')}",
                f"- Score: {compliance_report.get('score', 'unknown')}%",
                "",
            ]
        )
    elif compliance_report.get("error"):
        lines.extend(["## Compliance Checker", f"- Error: {compliance_report['error']}", ""])

    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a combined review report from repo analysis tools."
    )
    parser.add_argument("target", nargs="?", default=".", help="Repository root path.")
    parser.add_argument(
        "--format", choices=["markdown", "json"], default="markdown", help="Output format."
    )
    parser.add_argument("--output", type=Path, help="Write report to a file.")
    parser.add_argument(
        "--framework",
        choices=["soc2", "pci-dss", "hipaa", "gdpr"],
        default="soc2",
        help="Compliance framework to evaluate.",
    )
    parser.add_argument("--base", help="Base branch or commit for PR analysis.")
    parser.add_argument("--head", help="Head branch or commit for PR analysis.")
    return parser.parse_args()


def main():
    args = parse_args()
    target = str(Path(args.target).resolve())
    report_data = {"target": target}

    security_cmd = [sys.executable, "scripts/security_scanner.py", target, "--json"]
    quality_cmd = [
        sys.executable,
        "scripts/code_quality_checker.py",
        target,
        "--language",
        "python",
        "--json",
    ]
    pr_cmd = [sys.executable, "scripts/pr_analyzer.py", target, "--json"]
    if args.base and args.head:
        pr_cmd.extend(["--base", args.base, "--head", args.head])
    compliance_cmd = [
        sys.executable,
        "scripts/compliance_checker.py",
        target,
        "--framework",
        args.framework,
        "--json",
    ]

    for name, cmd in [
        ("security", security_cmd),
        ("quality", quality_cmd),
        ("pr", pr_cmd),
        ("compliance", compliance_cmd),
    ]:
        code, out, err = run_command(cmd)
        if out:
            try:
                report_data[name] = json.loads(out)
            except json.JSONDecodeError:
                report_data[name] = {"error": err or out}
        else:
            report_data[name] = {"error": err or "unknown error"}

    if args.format == "json":
        output = json.dumps(report_data, indent=2)
    else:
        output = generate_markdown(report_data)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        try:
            print(output)
        except BrokenPipeError:
            pass

    sys.exit(0)


if __name__ == "__main__":
    main()
