#!/usr/bin/env python3
import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path

LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx", ".ts", ".tsx", ".mjs"],
    "java": [".java"],
    "go": [".go"],
}

EXCLUDED_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", "dist", "build"}

THRESHOLDS = {
    "long_function": 50,
    "large_file": 500,
    "god_class": 20,
    "too_many_params": 5,
    "deep_nesting": 4,
    "high_complexity": 10,
}


def compute_python_metrics(source):
    metrics = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return metrics

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno
            end = max((child.lineno for child in ast.walk(node) if hasattr(child, "lineno")), default=start)
            length = end - start + 1
            params = len(node.args.args) + len(node.args.kwonlyargs)
            level_values = [getattr(child, "level", 0) for child in ast.walk(node) if hasattr(child, "level")]
            depth = max(level_values) if level_values else 1
            branches = sum(isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.BoolOp)) for child in ast.walk(node))
            if length > THRESHOLDS["long_function"]:
                metrics.append({"type": "long_function", "name": node.name, "value": length})
            if params > THRESHOLDS["too_many_params"]:
                metrics.append({"type": "too_many_parameters", "name": node.name, "value": params})
            if branches > THRESHOLDS["high_complexity"]:
                metrics.append({"type": "high_complexity", "name": node.name, "value": branches})
    return metrics


def compute_text_metrics(source, language):
    findings = []
    function_pattern = re.compile(r"\b(function|def|class|interface|struct|fn)\b")
    lines = source.splitlines()
    nesting = 0
    max_nesting = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("if ", "for ", "while ", "switch ", "case ", "else ", "try", "except", "catch")):
            nesting += 1
            max_nesting = max(max_nesting, nesting)
        elif stripped == "" and nesting > 0:
            nesting = max(nesting - 1, 0)
    if max_nesting > THRESHOLDS["deep_nesting"]:
        findings.append({"type": "deep_nesting", "value": max_nesting})
    if source.count("if ") + source.count("for ") + source.count("while ") > THRESHOLDS["high_complexity"]:
        findings.append({"type": "high_complexity", "value": source.count("if ") + source.count("for ") + source.count("while ")})
    return findings


def analyze_file(path, language):
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    findings = []
    line_count = len(text.splitlines())
    if line_count > THRESHOLDS["large_file"]:
        findings.append({"type": "large_file", "value": line_count})
    if language == "python":
        findings.extend(compute_python_metrics(text))
    else:
        findings.extend(compute_text_metrics(text, language))
    if path.name.count("class") > 0 and text.count("def ") > THRESHOLDS["god_class"]:
        findings.append({"type": "god_class", "value": text.count("def ")})
    return findings


def gather_files(root, language):
    extensions = LANGUAGE_EXTENSIONS.get(language, [])
    if not extensions:
        return []
    return [
        path
        for path in Path(root).rglob("*")
        if path.suffix in extensions
        and not any(part in EXCLUDED_DIRS for part in path.parts)
    ]


def build_report(target, language, results):
    issues = []
    for file_path, findings in results.items():
        for finding in findings:
            issues.append({"file": str(file_path), **finding})
    total_issues = len(issues)
    status = "pass" if total_issues == 0 else "warn"
    return {
        "target": str(target),
        "language": language,
        "total_files": len(results),
        "total_issues": total_issues,
        "status": status,
        "issues": issues,
    }


def render_text(report):
    lines = [
        f"Code Quality Checker Report for {report['target']}",
        f"Language: {report['language']}",
        f"Files analyzed: {report['total_files']}",
        f"Total issues: {report['total_issues']}",
        "",
    ]
    for issue in report["issues"]:
        lines.append(f"- {issue['file']}: {issue['type']} ({issue['value']})")
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description="Code quality checker for file-level complexity thresholds.")
    parser.add_argument("target", nargs="?", default=".", help="Path to analyze.")
    parser.add_argument("--language", default="python", help="Language to evaluate.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--output", type=Path, help="Write report to a file.")
    return parser.parse_args()


def main():
    args = parse_args()
    language = args.language.lower()
    files = gather_files(args.target, language)
    results = {}
    for file_path in files:
        findings = analyze_file(file_path, language)
        if findings:
            results[file_path] = findings
    report = build_report(args.target, language, results)
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
    if report["total_issues"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
