#!/usr/bin/env python3
import argparse
import json
import re
import subprocess  # nosec B404
import sys
from pathlib import Path

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

CHANGE_PATTERN = re.compile(
    r"(TODO|FIXME|console\.log\(|print\(|debugger;|aws_secret_access_key|api[_-]?key|password|union\s+select|<script|\.\./|\.\.\\)",
    re.I,
)
SEVERITY_OVERRIDES = {
    "aws_secret_access_key": "critical",  # nosec B105
    "api_key": "high",
    "password": "high",  # nosec B105
    "union select": "critical",
    "<script": "high",
    "console.log(": "medium",
    "debugger;": "medium",
    "TODO": "low",
    "FIXME": "low",
    "../": "critical",
}


def git_diff_files(base, head):
    try:
        result = subprocess.run(  # nosec B603, B607
            ["git", "diff", "--name-only", f"{base}...{head}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        return []


def scan_file(path):
    findings = []
    try:
        text = Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    for lineno, line in enumerate(text.splitlines(), 1):
        for match in CHANGE_PATTERN.finditer(line):
            token = match.group(1)
            severity = SEVERITY_OVERRIDES.get(token.lower(), "medium")
            findings.append(
                {
                    "file": str(path),
                    "line": lineno,
                    "pattern": token,
                    "severity": severity,
                    "text": line.strip(),
                }
            )
    return findings


def analyze_files(files, repo_root):
    all_findings = []
    file_scores = {}
    for file in files:
        path = repo_root / file
        if not path.exists() or path.is_dir():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        findings = scan_file(path)
        all_findings.extend(findings)
        file_scores[file] = {
            "lines": sum(1 for _ in path.open(encoding="utf-8", errors="ignore")),
            "findings": len(findings),
        }
    return all_findings, file_scores


def compute_complexity_score(findings, file_scores):
    base_score = min(10, max(1, len(findings) * 2))
    file_penalty = sum(min(5, score["findings"]) for score in file_scores.values())
    score = min(10, base_score + file_penalty)
    return score


def categorize_risk(score, findings):
    if any(f["severity"] == "critical" for f in findings) or score >= 8:
        return "high"
    if any(f["severity"] == "high" for f in findings) or score >= 5:
        return "medium"
    return "low"


def build_report(target, findings, file_scores):
    score = compute_complexity_score(findings, file_scores)
    risk = categorize_risk(score, findings)
    prioritized_files = sorted(
        file_scores.items(), key=lambda item: (-item[1]["findings"], -item[1]["lines"])
    )
    return {
        "target": str(target),
        "complexity_score": score,
        "risk": risk,
        "total_findings": len(findings),
        "files_analyzed": len(file_scores),
        "file_prioritization": [file for file, _ in prioritized_files],
        "findings": findings,
    }


def render_text(report):
    lines = [
        f"PR Analyzer Report for {report['target']}",
        f"Complexity score: {report['complexity_score']}/10",
        f"Risk: {report['risk']}",
        f"Total findings: {report['total_findings']}",
        f"Files analyzed: {report['files_analyzed']}",
        "",
        "File prioritization:",
    ]
    for file in report["file_prioritization"][:20]:
        lines.append(f"- {file}")
    if report["findings"]:
        lines.append("")
        lines.append("Findings:")
        for finding in report["findings"]:
            lines.append(
                f"[{finding['severity'].upper()}] {finding['file']}:{finding['line']} {finding['pattern']} - {finding['text']}"
            )
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(
        description="PR analyzer for code risk and review prioritization."
    )
    parser.add_argument("target", nargs="?", default=".", help="Repository root path.")
    parser.add_argument("--base", help="Base branch or commit.")
    parser.add_argument("--head", help="Head branch or commit.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--output", type=Path, help="Write the report to a file.")
    return parser.parse_args()


def main():
    args = parse_args()
    repo_root = Path(args.target).resolve()
    files = []
    if args.base and args.head:
        files = git_diff_files(args.base, args.head)
    else:
        files = [
            str(path.relative_to(repo_root))
            for path in repo_root.rglob("*")
            if path.is_file() and not any(part in EXCLUDED_DIRS for part in path.parts)
        ]
    findings, file_scores = analyze_files(files, repo_root)
    report = build_report(repo_root, findings, file_scores)
    if args.json:
        output = json.dumps(report, indent=2)
    else:
        output = render_text(report)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        try:
            print(output)
        except BrokenPipeError:
            pass
    if report["risk"] == "high":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
