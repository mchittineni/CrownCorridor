#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from pathlib import Path

SEVERITY_ORDER = ["low", "medium", "high", "critical"]

PATTERNS = [
    {
        "name": "Hardcoded Secret",
        "pattern": re.compile(
            r"(?i)(aws_secret_access_key|aws_access_key_id|api[_-]?key|secret|password)\s*=\s*['\"][^'\"]+['\"]"
        ),
        "severity": "high",
        "category": "secret",
    },
    {
        "name": "SQL Injection",
        "pattern": re.compile(
            r"(?i)(union\s+select|select\s+.+\s+from|drop\s+table|exec\(|sp_executesql|--\s|/\*)"
        ),
        "severity": "critical",
        "category": "injection",
    },
    {
        "name": "XSS Injection",
        "pattern": re.compile(
            r"(?i)(<script|javascript:|onerror=|onload=|document\.cookie|window\.location)"
        ),
        "severity": "high",
        "category": "xss",
    },
    {
        "name": "Command Injection",
        "pattern": re.compile(
            r"(?i)(\b(exec|system|popen|subprocess\.run|subprocess\.Popen|os\.system|shell=True)\b|[;&|`]{2,})"
        ),
        "severity": "critical",
        "category": "injection",
    },
    {
        "name": "Path Traversal",
        "pattern": re.compile(r"(\.\./|\.\.\\|/etc/passwd|c:\\windows\\system32)"),
        "severity": "critical",
        "category": "path_traversal",
    },
    {
        "name": "Debug Statement",
        "pattern": re.compile(
            r"(?i)(console\.log\(|print\(|pdb\.set_trace\(|debugger;|logger\.debug\()"
        ),
        "severity": "medium",
        "category": "debug",
    },
    {
        "name": "TODO/FIXME",
        "pattern": re.compile(r"(?i)\b(TODO|FIXME)\b"),
        "severity": "low",
        "category": "comment",
    },
]

EXTENSIONS = [
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".go",
    ".php",
    ".java",
    ".c",
    ".cpp",
    ".cc",
    ".h",
    ".html",
    ".css",
    ".yaml",
    ".yml",
    ".json",
    ".tf",
    ".tfvars",
    ".hcl",
]

EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
}


def scan_file(path, min_severity):
    findings = []
    text = ""
    try:
        text = Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    for lineno, line in enumerate(text.splitlines(), 1):
        for rule in PATTERNS:
            if SEVERITY_ORDER.index(rule["severity"]) < SEVERITY_ORDER.index(min_severity):
                continue
            if rule["pattern"].search(line):
                findings.append(
                    {
                        "file": str(path),
                        "line": lineno,
                        "rule": rule["name"],
                        "category": rule["category"],
                        "severity": rule["severity"],
                        "line_text": line.strip(),
                    }
                )
    return findings


def scan_path(target, min_severity="low"):
    results = []
    target_path = Path(target)
    if target_path.is_file():
        if target_path.suffix in EXTENSIONS:
            results.extend(scan_file(target_path, min_severity))
        return results

    for root, dirs, files in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for name in files:
            path = Path(root) / name
            if path.suffix.lower() in EXTENSIONS:
                results.extend(scan_file(path, min_severity))
    return results


def categorize_risk(findings):
    if any(f["severity"] == "critical" for f in findings):
        return "critical"
    if any(f["severity"] == "high" for f in findings):
        return "high"
    if any(f["severity"] == "medium" for f in findings):
        return "medium"
    return "low"


def build_report(findings, target):
    summary = {
        "target": target,
        "total_findings": len(findings),
        "risk": categorize_risk(findings),
        "by_severity": {},
        "by_category": {},
    }
    for finding in findings:
        summary["by_severity"].setdefault(finding["severity"], 0)
        summary["by_severity"][finding["severity"]] += 1
        summary["by_category"].setdefault(finding["category"], 0)
        summary["by_category"][finding["category"]] += 1
    return summary


def render_text(report, findings):
    lines = [
        f"Security Scanner Report for {report['target']}",
        f"Risk: {report['risk']}",
        f"Total findings: {report['total_findings']}",
        "",
    ]
    for severity in ["critical", "high", "medium", "low"]:
        count = report["by_severity"].get(severity, 0)
        lines.append(f"{severity.title()}: {count}")
    lines.append("")
    for finding in findings:
        lines.append(
            f"[{finding['severity'].upper()}] {finding['file']}:{finding['line']} {finding['rule']} - {finding['line_text']}"
        )
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description="Security scanner for code and IaC files.")
    parser.add_argument("target", nargs="?", default=".", help="Path to scan.")
    parser.add_argument(
        "--severity", choices=SEVERITY_ORDER, default="low", help="Minimum severity to include."
    )
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--output", type=Path, help="Write report to a file.")
    return parser.parse_args()


def main():
    args = parse_args()
    findings = scan_path(args.target, min_severity=args.severity)
    report = build_report(findings, args.target)

    if args.json:
        output = json.dumps({"report": report, "findings": findings}, indent=2)
    else:
        output = render_text(report, findings)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        try:
            print(output)
        except BrokenPipeError:
            pass

    if report["risk"] == "critical":
        sys.exit(2)
    if report["risk"] == "high":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
