#!/usr/bin/env python3
"""
Comprehensive Obsidian Vault Knowledge Base Generator & Git Sync.

Generates a complete knowledge graph for the iacsecbench workspace inside Obsidian:
  1. Research Article Workspace & Methodological Proofs (`Research/`)
  2. Project Architecture Map & File Knowledge Base (`Project-Structure.md`)
  3. Cross-linked component notes in `Modules/` detailing dependencies, docstrings, & imports
  4. Chronological daily commit activity notes in `Daily/` with Mermaid charts & Dataview tags
  5. Master Dashboard index (`Changelog-Activity.md`)
"""

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DAILY_DIR = os.path.join(PROJECT_DIR, "obsidian_daily")
LOCAL_MODULES_DIR = os.path.join(PROJECT_DIR, "obsidian_modules")
LOCAL_RESEARCH_DIR = os.path.join(PROJECT_DIR, "obsidian_research")
LOCAL_INDEX_FILE = os.path.join(PROJECT_DIR, "OBSIDIAN_CHANGELOG_INDEX.md")
LOCAL_STRUCTURE_FILE = os.path.join(PROJECT_DIR, "OBSIDIAN_PROJECT_STRUCTURE.md")

VAULT_DIR = "/Users/manideepchittineni/Desktop/GitHub/Obsidian Vault/iacsecbench"
VAULT_DAILY_DIR = os.path.join(VAULT_DIR, "Daily")
VAULT_MODULES_DIR = os.path.join(VAULT_DIR, "Modules")
VAULT_RESEARCH_DIR = os.path.join(VAULT_DIR, "Research")
VAULT_INDEX_FILE = os.path.join(VAULT_DIR, "Changelog-Activity.md")
VAULT_STRUCTURE_FILE = os.path.join(VAULT_DIR, "Project-Structure.md")

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    ".DS_Store",
    "obsidian_daily",
    "obsidian_modules",
    "obsidian_research",
    ".coverage",
    "data",
}

EXCLUDE_PATH_PREFIXES = (
    "data/",
    "docs/api/",
)

EXCLUDE_FILES = {
    "OBSIDIAN_CHANGELOG_INDEX.md",
    "OBSIDIAN_CHANGELOG_SYNC.md",
    "OBSIDIAN_PROJECT_STRUCTURE.md",
}


# ==============================================================================
# SECTION 1: GIT HISTORY PARSING
# ==============================================================================


def get_git_history():
    """Retrieve full git commit history sorted chronologically."""
    git_cmd = [
        "git",
        "log",
        "--reverse",
        "--stat",
        "--format=COMMIT_START%n%H%n%h%n%an%n%ae%n%ad%n%aI%n%s%n%b%nSTAT_START",
    ]
    try:
        result = subprocess.run(
            git_cmd,
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error reading git history: {e}", file=sys.stderr)
        sys.exit(1)


def parse_commits(git_output):
    """Parse git log into structured commit objects grouped by date."""
    raw_commits = git_output.split("COMMIT_START\n")
    daily_commits = defaultdict(list)

    for raw in raw_commits:
        if not raw.strip():
            continue

        parts = raw.split("STAT_START\n")
        header_block = parts[0].strip().split("\n")

        if len(header_block) < 7:
            continue

        commit_hash = header_block[0]
        short_hash = header_block[1]
        author_name = header_block[2]
        author_email = header_block[3]
        author_date = header_block[4]
        iso_date_str = header_block[5]
        subject = header_block[6]
        body = "\n".join(header_block[7:]).strip() if len(header_block) > 7 else ""
        stat_block = parts[1].strip() if len(parts) > 1 else ""

        match_type = re.match(r"^([a-z]+)(\([^\)]+\))?:", subject)
        commit_type = match_type.group(1) if match_type else "other"
        day_key = iso_date_str.split("T")[0] if "T" in iso_date_str else iso_date_str[:10]

        daily_commits[day_key].append(
            {
                "hash": commit_hash,
                "short_hash": short_hash,
                "author_name": author_name,
                "author_email": author_email,
                "date": author_date,
                "subject": subject,
                "type": commit_type,
                "body": body,
                "stat": stat_block,
            }
        )

    return daily_commits


# ==============================================================================
# SECTION 2: WORKSPACE FILE SYSTEM & CODE DEPENDENCY PARSER
# ==============================================================================


def scan_project_files():
    """Scan markdown files and extract metadata."""
    file_map = {}

    for root, dirs, files in os.walk(PROJECT_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for f in files:
            if f in EXCLUDE_FILES or f.startswith("."):
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext != ".md":
                continue

            rel_path = os.path.relpath(os.path.join(root, f), PROJECT_DIR)
            if rel_path.startswith(EXCLUDE_PATH_PREFIXES):
                continue

            abs_path = os.path.join(root, f)
            size = os.path.getsize(abs_path)

            # A file that cannot be decoded as UTF-8 or read at all still belongs
            # in the map with its size and extension; only its body is missing.
            # The reason is recorded rather than swallowed, so an unexpectedly
            # unreadable file is visible in the sync log instead of silently
            # appearing empty.
            file_content = ""
            try:
                with open(abs_path, encoding="utf-8") as file_handle:
                    file_content = file_handle.read()
            except (OSError, UnicodeDecodeError) as exc:
                print(f"  ! skipped body of {rel_path}: {exc}")

            file_map[rel_path] = {
                "rel_path": rel_path,
                "size": size,
                "ext": ext,
                "content": file_content,
            }

    return file_map


# ==============================================================================
# SECTION 3: RESEARCH NOTES GENERATOR
# ==============================================================================

EVALUATION_JSON = os.path.join(PROJECT_DIR, "results", "evaluation.json")

_TOOL_LABELS = {
    "checkov": ("Checkov", "AST static analysis"),
    "tfsec": ("tfsec", "HCL lexical scanning"),
    "opa": ("OPA (plan-level)", "Rego over compiled plan"),
    "iacsecbench": ("IaCSecBench", "Composite pipeline"),
    "iacsb_layer1": ("IaCSecBench L1", "Repository-edge scanning"),
}

_NO_MEASUREMENT = """> [!WARNING] No measurement available
> `results/evaluation.json` is absent, so there are no results to show. This note
> deliberately shows nothing rather than illustrative numbers: a table synced into
> a vault outlives the caveat that accompanied it.
>
> Produce one with `experiments/run_baselines.sh`, then re-run the sync.
"""


def render_measured_metrics_table() -> str:
    """Renders the performance table from measured output, or says there is none.

    This table used to be a hardcoded literal reporting 345 cases and a perfect
    score for the reference implementation. Neither figure was measured: the
    corpus is a fraction of that size and the reference implementation ranks last
    on it. Because this function publishes into an Obsidian vault, a wrong number
    here escapes the repository entirely and acquires the authority of a note the
    author wrote themselves -- so it now reads the measured artefact or prints
    nothing at all.
    """
    try:
        with open(EVALUATION_JSON, encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return _NO_MEASUREMENT

    corpus = payload.get("corpus", {})
    level = payload.get("matching_level", "control")
    results = payload.get("results", {})
    if not results:
        return _NO_MEASUREMENT

    rows = []
    for tool, per_level in results.items():
        entry = per_level.get(level) or {}
        matrix = entry.get("confusion_matrix") or {}
        if not matrix:
            continue
        latency = entry.get("latency") or {}
        label, category = _TOOL_LABELS.get(tool, (tool, ""))
        ci = matrix.get("recall_ci") or {}

        def pct(key, source=matrix):
            value = source.get(key)
            return "n/e" if value is None else f"{value * 100:.2f}%"

        interval = (
            f"$[{ci['lower'] * 100:.2f}\\%, {ci['upper'] * 100:.2f}\\%]$"
            if ci.get("lower") is not None
            else "n/e"
        )
        mean = latency.get("mean_ms")
        sd = latency.get("sd_ms")
        latency_cell = "n/e" if mean is None else f"{mean:.1f} ± {sd:.1f} ms"
        rows.append(
            (
                matrix.get("recall") or 0.0,
                f"| {label} | {category} | {matrix.get('tp')} | {matrix.get('fp')} | "
                f"{matrix.get('fn')} | {matrix.get('tn')} | {pct('accuracy')} | "
                f"{pct('precision')} | {pct('recall')} | {interval} | {latency_cell} |",
            )
        )
    if not rows:
        return _NO_MEASUREMENT
    rows.sort(key=lambda r: r[0], reverse=True)

    caveats = payload.get("caveats") or []
    caveat_block = "\n".join(f"> - {c}" for c in caveats)
    return f"""- **Admissible cases:** `{corpus.get("n_cases")}` \
({corpus.get("n_vulnerable")} vulnerable, {corpus.get("n_compliant")} compliant)
- **Matching level:** `{level}`
- **Generated from:** `results/evaluation.json` — do not edit this note by hand.

| Tool / Engine | Category | TP | FP | FN | TN | Accuracy | Precision | Recall | 95% CI (Recall) | Latency |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
{chr(10).join(row for _, row in rows)}

> [!IMPORTANT] Caveats that travel with these numbers
{caveat_block or "> - (none recorded)"}
"""


def generate_research_notes():
    """Generate structured Research Article Notes.

    Markdown line breaks in these templates are expressed as list items, never as
    two trailing spaces. Trailing whitespace is content in Markdown and formatting
    slack everywhere else, and every tool in this repository treats it as the
    latter: pre-commit's trailing-whitespace hook and ruff's W291 both strip it.
    A previous revision relied on it here, and the hook duly deleted it, silently
    collapsing four separate metadata lines into one wrapped paragraph in the
    published vault. List markup survives every formatter, so the rendered output
    no longer depends on characters the toolchain is entitled to remove.
    """
    research_files = {}

    # 1. Article Workspace Note
    research_files["Article-Workspace.md"] = """---
type: research_article
title: "IaCSecBench: A Reproducible Benchmark Framework for Evaluating Infrastructure as Code Security Validation Pipelines"
author: "Manideep Chittineni"
target_journal: "IEEE Transactions on Software Engineering"
status: "Drafting"
tags: [research, ieee, paper, iac, devsecops, benchmark]
---

# 📝 IEEE Research Article: IaCSecBench Workspace

> - **Journal Target:** IEEE Transactions on Software Engineering
> - **Author:** Manideep Chittineni (`manideep.chittineni@hotmail.com`)
> - **Repository:** [[Project-Structure|iacsecbench Codebase]]
> - **Changelog & Activity:** [[Changelog-Activity|Master Activity Log]]

---

## 📌 Research Article Workspace Navigation

- [[Research/RQ1-Internal-Metrics|📊 RQ1: Internal Controlled Benchmark Performance]]
- [[Research/Threat-Model-STRIDE|🛡️ Threat Model & STRIDE Mitigation Matrix]]
- [[Research/RQ5-External-Generalizability|🌐 RQ5: External Generalizability Collection]]

---

## 📊 Quick Empirical Metrics Summary

""" + render_measured_metrics_table()

    # 2. RQ1 Metrics Note
    research_files["RQ1-Internal-Metrics.md"] = (
        """---
type: research_metrics
rq: "RQ1"
tags: [research, metrics, benchmark, rq1]
---

# 📊 RQ1: Internal Controlled Benchmark Performance

> **Research Question:** Can IaCSecBench identify deliberately introduced infrastructure and data security violations across a controlled benchmark dataset?

---

## 📈 Empirical Confusion Matrix Results

### Comprehensive Performance Comparison Table

"""
        + render_measured_metrics_table()
        + """
### Reading this table

The reference implementation does **not** lead it. Layer 1 is a repository-edge
secret and PII scanner and the corpus is cloud misconfigurations, so it detects
almost nothing here. That is a scope boundary, reported as measured.

The denominator is the *admissible* corpus — cases present on disk, labelled
unambiguously, and passing `terraform validate`. It is much smaller than the
designed taxonomy of 345 internal and 175 external cases, and the designed figure
is never used as a denominator.
"""
    )

    # 3. STRIDE Threat Model Note
    research_files["Threat-Model-STRIDE.md"] = """---
type: threat_model
tags: [research, security, stride, threat-model]
---

# 🛡️ Threat Model & STRIDE Mitigation Matrix

> **Reference Section:** Section IV (*Threat Model and Security Assumptions*)

---

## 📐 Pipeline Trust Boundaries & Threat Graph

```mermaid
graph TD
    Dev["Developer Workspace"] -->|Git Commit| Repo["GitHub Source Control"]
    Repo -->|Trigger Webhook| CI["Continuous Integration Pipeline"]

    subgraph Trust Boundary 1: Repository Edge
        L1["Layer 1: Data and PII Sanitizer"]
    end

    subgraph Trust Boundary 2: Module Validation
        L2["Layer 2: Native Terraform Tester"]
    end

    subgraph Trust Boundary 3: Compiled Plan Evaluation
        Plan["Terraform Plan JSON Exporter"]
        L3["Layer 3: OPA Rego Policy Engine"]
    end

    CI --> L1
    L1 --> L2
    L2 --> Plan
    Plan --> L3
    L3 -->|Pass Fail Gate| Deploy["Cloud Infrastructure Provisioning"]
```

---

## 📋 STRIDE Threat Matrix & Layered Mitigations

| STRIDE Category | Identified Security Threat Vector | IaCSecBench Mitigation Mechanism | Validation Layer |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Impersonation of cloud services or users via leaked API tokens or unauthenticated endpoints. | Mandatory Cognito JWT authorizers, TLS 1.3 enforcement, and zero-hardcoded credential rules. | Layer 1 (Data) & Layer 3 (OPA) |
| **Tampering** | Unauthorised modification of IaC modules, Rego policies, or imported data schemas. | Automated schema validation, Git pre-commit enforcement, and compiled plan JSON checking. | Layer 1 (Data) & Layer 2 (Native) |
| **Repudiation** | Absence of audit trails for infrastructure state changes or policy compliance decisions. | Structured CI telemetry logging, explicit `.tftest.hcl` execution reports, and CIS compliance tagging. | Layer 2 (Native) & Layer 3 (OPA) |
| **Information Disclosure** | Leakage of customer PII, AWS secret keys, or unencrypted storage volumes. | Regex-based Zero-PII scrubbing, mandatory KMS encryption, and S3 public access blocking. | Layer 1 (Data) & Layer 3 (OPA) |
| **Denial of Service** | Unrestricted API rate limits, open security groups, or missing Web Application Firewall (WAF) rules. | Automated validation of AWS WAF Web ACLs, ALB header dropping, and API Gateway throttling. | Layer 2 (Native) & Layer 3 (OPA) |
| **Elevation of Privilege** | Provisioning excessive IAM permissions (`*`), wildcard trust roles, or unauthenticated ingress. | OPA Rego policy evaluation denying wildcard IAM actions and unrestricted CIDR ingress (`0.0.0.0/0`). | Layer 3 (OPA Policy) |
"""

    return research_files


# ==============================================================================
# SECTION 4: OBSIDIAN KNOWLEDGE MAP GENERATOR
# ==============================================================================


def generate_project_structure_note(file_map):
    """Generate Project-Structure.md with full tree view and dependency graph."""
    lines = [
        "---",
        "type: project_architecture",
        "tags: [architecture, workspace, dependencies, knowledge-graph]",
        "---",
        "",
        "# 📐 iacsecbench — Workspace Architecture & File Knowledge Graph",
        "",
        f"> **Last Synced:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`  ",
        f"> **Total Tracked Markdown Files:** `{len(file_map)}`",
        "",
        "---",
        "",
        "## 🔗 High-Level Component Relationship Graph",
        "",
        "```mermaid",
        "graph TD",
        '    Root["iacsecbench Workspace Root"]',
        '    App["application (API and Portal UI)"]',
        '    Pipe["pipeline (Data Validation Engine)"]',
        '    Sec["security_framework (Scoring Policies)"]',
        '    Bench["benchmark (Datasets and Test Suites)"]',
        '    Exp["experiments (Reproducibility Drivers)"]',
        "",
        "    Root --> App",
        "    Root --> Pipe",
        "    Root --> Sec",
        "    Root --> Bench",
        "    Root --> Exp",
        "",
        "    Pipe --> Sec",
        "    App --> Pipe",
        "    Exp --> Pipe",
        "    Sec --> Bench",
        "```",
        "",
        "---",
        "",
        "## 📁 Workspace File Map & Module Links",
        "",
    ]

    grouped = defaultdict(list)
    for path, info in sorted(file_map.items()):
        top_dir = path.split(os.sep)[0] if os.sep in path else "Root Files"
        grouped[top_dir].append(info)

    for group_name, info_list in sorted(grouped.items()):
        lines.append(f"### 📂 `{group_name}`")
        lines.append("")
        for info in info_list:
            safe_module_name = info["rel_path"].replace("/", "_").replace(".", "_")
            lines.append(
                f"- **[[Modules/{safe_module_name}|`{info['rel_path']}`]]** ({info['size']} bytes)"
            )
        lines.append("")

    return "\n".join(lines)


def generate_module_notes(file_map):
    """Generate detailed individual module notes under Modules/ with cross-linking."""
    module_files = {}

    for rel_path, info in file_map.items():
        safe_name = rel_path.replace("/", "_").replace(".", "_") + ".md"
        lines = [
            "---",
            f"file_path: {rel_path}",
            f"size_bytes: {info['size']}",
            "type: code_module",
            "tags: [code, module, architecture]",
            "---",
            "",
            f"# 📄 Module Note: `{rel_path}`",
            "",
            f"> **Relative Path:** `{rel_path}`  ",
            f"> **File Size:** `{info['size']} bytes`  ",
            "> **Architecture Map:** [[Project-Structure]]  ",
            "> **Master Changelog:** [[Changelog-Activity]]",
            "",
            "---",
            "",
        ]

        parent_dir = os.path.dirname(rel_path)
        related = [
            p for p, i in file_map.items() if os.path.dirname(p) == parent_dir and p != rel_path
        ]
        if related:
            lines.append("## 🔗 Related Workspace Modules")
            lines.append("")
            for rpath in related[:10]:
                r_safe = rpath.replace("/", "_").replace(".", "_")
                lines.append(f"- [[Modules/{r_safe}|`{rpath}`]]")
            lines.append("")

        if info.get("content"):
            lines.append("## 📝 Document Content & Full Description")
            lines.append("")
            lines.append(info["content"])
            lines.append("")

        module_files[safe_name] = "\n".join(lines)

    return module_files


def generate_daily_notes(daily_commits):
    """Generate individual Obsidian daily note contents."""
    daily_files_data = {}

    for day_str, commits in sorted(daily_commits.items()):
        lines = [
            "---",
            f"date: {day_str}",
            f"total_commits: {len(commits)}",
            "type: daily_changelog",
            "tags: [changelog, activity, git-sync]",
            "---",
            "",
            f"# 📅 Activity Log — {day_str}",
            "",
            f"> **Date:** `{day_str}`  ",
            f"> **Total Commits:** `{len(commits)}`  ",
            "> **Main Index:** [[Changelog-Activity]]  ",
            "> **Architecture Map:** [[Project-Structure]]",
            "",
            "---",
            "",
            "## 📊 Daily Workflow Visualization",
            "",
            "```mermaid",
            "graph TD",
        ]

        for idx, c in enumerate(commits, 1):
            clean_sub = re.sub(r'["\'\(\)\[\]&<>]', " ", c["subject"])
            lines.append(f'    C{idx}["{c["short_hash"]}: {clean_sub}"]')
            if idx > 1:
                lines.append(f"    C{idx - 1} --> C{idx}")

        lines.extend(
            [
                "```",
                "",
                "---",
                "",
                "## 📝 Commit Details",
                "",
            ]
        )

        for idx, commit in enumerate(commits, 1):
            lines.append(f"### {idx}. {commit['subject']}")
            lines.append(f"- **Time/Date:** `{commit['date']}`")
            lines.append(f"- **Commit:** `{commit['short_hash']}` (`{commit['hash'][:12]}`)")
            lines.append(f"- **Author:** {commit['author_name']} (<{commit['author_email']}>)")
            lines.append(f"- **Type Tag:** #{commit['type']}")

            if commit["body"]:
                lines.append("")
                lines.append("```text")
                lines.append(commit["body"])
                lines.append("```")

            if commit["stat"]:
                lines.append("")
                lines.append("<details><summary><b>Changed Files & Statistics</b></summary>")
                lines.append("")
                lines.append("```text")
                lines.append(commit["stat"])
                lines.append("```")
                lines.append("</details>")

            lines.append("")
            lines.append("---")
            lines.append("")

        daily_files_data[f"{day_str}.md"] = "\n".join(lines)

    return daily_files_data


def generate_main_index(daily_commits):
    """Generate main Changelog-Activity.md dashboard."""
    total_commits = sum(len(commits) for commits in daily_commits.values())
    sorted_days = sorted(daily_commits.keys(), reverse=True)

    lines = [
        "---",
        "type: activity_dashboard",
        "tags: [dashboard, activity, obsidian-sync]",
        "---",
        "",
        "# 📜 iacsecbench — Master Activity Dashboard & Visualizations",
        "",
        f"> **Last Synced:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`  ",
        f"> **Total Synced Commits:** `{total_commits}` across `{len(sorted_days)}` days  ",
        "> **Research Article Workspace:** [[Research/Article-Workspace]]  ",
        "> **Workspace Knowledge Map:** [[Project-Structure]]",
        "",
        "---",
        "",
        "## 📅 Daily Activity Logs & Changes",
        "",
    ]

    for day in sorted_days:
        commits = daily_commits[day]
        lines.append(f"### [[Daily/{day}|📅 {day}]] (`{len(commits)} commits`)")
        for commit in commits:
            lines.append(f"- **`{commit['short_hash']}`** `{commit['type']}`: {commit['subject']}")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## 🔍 Quick Jump Navigation",
            "",
            "- [[Research/Article-Workspace|📝 View IEEE Research Article Workspace]]",
            "- [[Project-Structure|📐 View Project Architecture & Knowledge Graph]]",
        ]
    )
    for day in sorted_days:
        lines.append(f"- [[Daily/{day}|View activity for {day}]]")
    lines.append("")

    return "\n".join(lines)


def write_notes_dict(target_dir, notes_dict):
    """Safely write a dictionary of filenames -> content to target directory."""
    os.makedirs(target_dir, exist_ok=True)
    for fname, content in notes_dict.items():
        filepath = os.path.join(target_dir, fname)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)


def main():
    print(f"Syncing git history & workspace architecture from: {PROJECT_DIR}")

    # 1. Parse Git History & Project Files
    git_output = get_git_history()
    daily_commits = parse_commits(git_output)
    file_map = scan_project_files()

    # 2. Generate Content
    daily_files_data = generate_daily_notes(daily_commits)
    module_files_data = generate_module_notes(file_map)
    research_files_data = generate_research_notes()
    main_index_content = generate_main_index(daily_commits)
    structure_content = generate_project_structure_note(file_map)

    # 3. Write Local Workspace Copies
    write_notes_dict(LOCAL_DAILY_DIR, daily_files_data)
    write_notes_dict(LOCAL_MODULES_DIR, module_files_data)
    write_notes_dict(LOCAL_RESEARCH_DIR, research_files_data)

    with open(LOCAL_INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(main_index_content)

    with open(LOCAL_STRUCTURE_FILE, "w", encoding="utf-8") as f:
        f.write(structure_content)

    print(
        f"✅ Local workspace daily notes ({len(daily_files_data)}) generated in: {LOCAL_DAILY_DIR}"
    )
    print(
        f"✅ Local workspace module notes ({len(module_files_data)}) generated in: {LOCAL_MODULES_DIR}"
    )
    print(
        f"✅ Local workspace research notes ({len(research_files_data)}) generated in: {LOCAL_RESEARCH_DIR}"
    )

    # 4. Write Directly to External Vault (Dual Sync)
    try:
        write_notes_dict(VAULT_DAILY_DIR, daily_files_data)
        write_notes_dict(VAULT_MODULES_DIR, module_files_data)
        write_notes_dict(VAULT_RESEARCH_DIR, research_files_data)

        with open(VAULT_INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(main_index_content)

        with open(VAULT_STRUCTURE_FILE, "w", encoding="utf-8") as f:
            f.write(structure_content)

        print(f"✅ Vault daily notes updated at: {VAULT_DAILY_DIR}")
        print(f"✅ Vault module notes updated at: {VAULT_MODULES_DIR}")
        print(f"✅ Vault research notes updated at: {VAULT_RESEARCH_DIR}")
        print(f"✅ Vault main index updated at: {VAULT_INDEX_FILE}")
        print(f"✅ Vault project structure updated at: {VAULT_STRUCTURE_FILE}")
    except PermissionError:
        print("ℹ️ External Obsidian Vault direct write restricted. Local copy ready.")


if __name__ == "__main__":
    main()
