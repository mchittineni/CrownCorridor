#!/usr/bin/env python3
"""Generates the manuscript's diagram sources from the recorded results.

Why this exists
---------------
The figures shipped with an earlier revision of the manuscript hard-coded a corpus
size of 345 cases, named a scanner the paper excludes, omitted one it evaluates,
and carried four tool version strings that no longer matched
``results/run_manifest.json``. None of that was detectable from the figures
themselves, because they had no source in the repository: they were exported images
with numbers typed into them.

The manuscript already refuses to restate a version string in prose on the grounds
that a hand-copied one is the first thing to drift. This applies the same rule to
the figures. Every quantity below is read from the recorded results, so a figure
cannot disagree with a table unless the generator is wrong for both.

Usage
-----
    python -m experiments.generate_figures          # write paper/figures/*.mmd
    python -m experiments.generate_figures --check  # exit 1 if a figure's substance is stale
    python -m experiments.generate_figures --check --strict   # ... or its latency labels moved

``--check`` deliberately tolerates a change confined to the two measured latency
labels; see ``_without_latency`` for why.

Rendering requires the Mermaid CLI, which this repository does not vendor:

    npx -y @mermaid-js/mermaid-cli -i paper/figures/pipeline_architecture.mmd \\
        -o paper/figures/pipeline_architecture.pdf --pdfFit

``--pdfFit`` matters. Without it the page is sized to US Letter and a wide diagram
is paginated across several pages, of which ``\\includegraphics`` embeds only the
first. That is how the previous figures came to show a fragment of themselves.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGURES = ROOT / "paper" / "figures"
EVALUATION = ROOT / "results" / "evaluation.json"
MANIFEST = ROOT / "results" / "run_manifest.json"
CORPUS_REPORT = ROOT / "results" / "corpus_report.json"

# Order the scanners appear in, and the paradigm label each carries in the figure.
# iacsb_layer1 and opa are the pipeline's own layers and are drawn separately.
COMPARATORS = {
    "checkov": "AST static analysis",
    "tfsec": "HCL lexical scanning",
    "trivy": "HCL scanning, tfsec successor",
}


# The pipeline figure carries two measured latencies as edge labels. Everything else
# in both figures is deterministic given the recorded results -- counts, versions, which
# tools ran -- so a difference there means a figure now contradicts a table. Latency is
# not deterministic: it is a property of the host that measured it, and the measurement
# workflow says as much in its own summary ("latency in this run is not publishable. It
# was measured on a shared GitHub-hosted runner"). Comparing it byte-for-byte made the
# CI gate fail on every scheduled re-measurement, and the remedy it printed -- regenerate
# and commit -- would have replaced the published idle-machine figures with runner noise.
# So --check ignores these labels by default, and --strict restores the exact comparison
# for the machine that produces publishable latency.
_LATENCY_LABEL = re.compile(r'(pass, )[^"]*')


def _without_latency(text: str) -> str:
    """``text`` with the measured latency edge labels blanked out."""
    return _LATENCY_LABEL.sub(r"\1<latency>", text)


def _load() -> tuple[dict, dict, dict]:
    missing = [p.name for p in (EVALUATION, MANIFEST) if not p.is_file()]
    if missing:
        sys.exit(
            f"error: {', '.join(missing)} not found.\n"
            "       Run experiments/run_baselines.sh first; figures are generated "
            "from recorded results, never hand-authored."
        )
    evaluation = json.loads(EVALUATION.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report = (
        json.loads(CORPUS_REPORT.read_text(encoding="utf-8")) if CORPUS_REPORT.is_file() else {}
    )
    return evaluation, manifest, report


def _version(manifest: dict, tool: str) -> str:
    """Tool version as recorded, stripped of the noise each binary prefixes it with."""
    raw = (manifest.get("tools", {}).get(tool, {}) or {}).get("version", "")
    for prefix in ("Version:", "version", "Terraform"):
        raw = raw.replace(prefix, "")
    return raw.strip() or "unrecorded"


def _mean_ms(evaluation: dict, tool: str, level: str) -> float | None:
    entry = (evaluation.get("results", {}).get(tool) or {}).get(level) or {}
    return (entry.get("latency") or {}).get("mean_ms")


def _fmt_ms(value: float | None) -> str:
    if value is None:
        return "not measured"
    return f"{value:.1f} ms" if value >= 1 else f"{value:.2f} ms"


def pipeline_architecture(evaluation: dict, manifest: dict) -> str:
    """Vertical gating chain, kept deliberately short.

    An earlier layout gave each layer its own decision diamond, which made the
    drawing nine rows tall: 7.3in at the column measure, most of a page for a
    five-step pipeline. The decisions are now edge labels and the rejection path
    converges on one node, which halves the height without losing the gating
    semantics. The explanatory note that used to hang off Layer 2 belongs in the
    LaTeX caption, not in the drawing, and has moved there.
    """
    level = evaluation.get("matching_level", "control")
    l1 = _fmt_ms(_mean_ms(evaluation, "iacsb_layer1", level))
    l3 = _fmt_ms(_mean_ms(evaluation, "opa", level))
    tf = _version(manifest, "terraform")
    opa = _version(manifest, "opa")
    return f"""%% Generated by experiments/generate_figures.py -- do not edit by hand.
%% Latency figures are per-case means from results/evaluation.json.
%% Layer 3's figure covers policy evaluation over an already-compiled plan and
%% excludes terraform init/plan, which dominate the layer's wall-clock cost.
flowchart TD
    commit(["Commit or pull request"])
    l1["<b>Layer 1</b>  repository edge<br/>schema validation, sensitive-field<br/>and personal-data detection"]
    l2["<b>Layer 2</b>  native module testing<br/>Terraform {tf} test framework<br/>not scored per case"]
    l3["<b>Layer 3</b>  compiled-plan policy<br/>OPA {opa} over plan JSON<br/>CIS AWS Foundations controls"]
    ok(["Eligible to apply"])
    no["Rejected<br/>finding reported"]

    commit --> l1
    l1 -- "pass, {l1}" --> l2
    l2 -- "pass" --> l3
    l3 -- "pass, {l3}" --> ok
    l1 -. "leak or schema failure" .-> no
    l2 -. "assertion failure" .-> no
    l3 -. "policy violation" .-> no

    classDef layer fill:#e8eaf6,stroke:#3949ab
    classDef term fill:#e8f5e9,stroke:#2e7d32
    classDef bad fill:#ffebee,stroke:#c62828
    class l1,l2,l3 layer
    class ok,commit term
    class no bad
"""


def normalization_workflow(evaluation: dict, manifest: dict, report: dict) -> str:
    corpus = evaluation.get("corpus", {})
    n, vuln, comp = corpus.get("n_cases"), corpus.get("n_vulnerable"), corpus.get("n_compliant")
    # The declared count is drawn deliberately, and labelled as declared. An earlier
    # hand-drawn version of this figure showed internal_declared (345) as though it
    # were the corpus size, which contradicted every table in the paper. The number
    # is worth showing -- the gap between declared and admissible is a finding -- but
    # only with both halves present.
    gap = report.get("catalogue_gap") or {}
    declared = (gap.get("internal_declared") or 0) + (gap.get("external_declared") or 0)
    on_disk = (gap.get("internal_on_disk") or 0) + (gap.get("external_on_disk") or 0)
    level = evaluation.get("matching_level", "control")
    ran = [t for t, s in (evaluation.get("tool_status") or {}).items() if s == "run"]

    comparators = "\n".join(
        f'        {t}["{t if t not in ("tfsec",) else t}  {_version(manifest, t)}<br/>{para}"]'
        for t, para in COMPARATORS.items()
        if t in ran
    )
    edges_in = "\n".join(f"    corpus --> {t}" for t in COMPARATORS if t in ran)
    edges_out = "\n".join(f"    {t} --> norm" for t in COMPARATORS if t in ran)

    declared_line = (
        f"<br/><i>from {declared} catalogue entries declared,<br/>{on_disk} present on disk</i>"
        if declared
        else ""
    )
    return f"""%% Generated by experiments/generate_figures.py -- do not edit by hand.
%% Counts come from results/evaluation.json and results/corpus_report.json.
%% Tool versions come from results/run_manifest.json. Nothing here is typed.
flowchart TD
    subgraph input["Admissible corpus"]
        corpus["<b>{n} admissible cases</b><br/>{vuln} vulnerable / {comp} compliant{declared_line}"]
    end

    subgraph tools["Third-party scanners (source level)"]
{comparators}
    end

    subgraph own["Pipeline layers"]
        l1["IaCSecBench L1<br/>repository-edge scanning"]
        opa["OPA {_version(manifest, "opa")}<br/>Rego over compiled plan"]
    end

    subgraph engine["Finding normalization"]
        norm["Canonical mapper<br/>native rule id to control set"]
        rec["F = (case, tool, controls, resource, severity)"]
        unmapped["Unmapped rule ids<br/>counted and reported,<br/>never discarded"]
    end

    subgraph scoring["Scoring"]
        match["Matching criterion<br/>control / resource / any<br/>(primary: {level})"]
        cm["Confusion matrix per tool"]
        stat["Clopper-Pearson intervals<br/>exact McNemar, Holm-Bonferroni"]
    end

{edges_in}
    corpus --> l1
    corpus --> opa
{edges_out}
    l1 --> norm
    opa --> norm
    norm --> rec
    norm --> unmapped
    rec --> match --> cm --> stat

    classDef box fill:#e8eaf6,stroke:#3949ab
    classDef eng fill:#f3e5f5,stroke:#6a1b9a
    classDef sc fill:#e0f2f1,stroke:#00695c
    classDef warn fill:#fff8e1,stroke:#f9a825
    class corpus,l1,opa box
    class norm,rec eng
    class unmapped warn
    class match,cm,stat sc
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", maxsplit=1)[0])
    ap.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if regeneration would change a figure's substance",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help=(
            "with --check, also fail when only the measured latency labels differ "
            "(for the idle machine that produces publishable latency)"
        ),
    )
    args = ap.parse_args()

    evaluation, manifest, report = _load()
    wanted = {
        "pipeline_architecture.mmd": pipeline_architecture(evaluation, manifest),
        "normalization_workflow.mmd": normalization_workflow(evaluation, manifest, report),
    }

    FIGURES.mkdir(parents=True, exist_ok=True)
    stale = []  # differs in something a table could contradict
    latency_only = []  # differs only in the host-dependent latency labels
    for name, content in wanted.items():
        path = FIGURES / name
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current == content:
            continue
        if current is not None and _without_latency(current) == _without_latency(content):
            latency_only.append(name)
        else:
            stale.append(name)
        if not args.check:
            path.write_text(content, encoding="utf-8")

    if args.check:
        if stale:
            print("figure sources are stale: " + ", ".join(stale), file=sys.stderr)
            print("run: python -m experiments.generate_figures", file=sys.stderr)
            return 1
        if latency_only and args.strict:
            print(
                "figure latency labels no longer match this run: " + ", ".join(latency_only),
                file=sys.stderr,
            )
            print("run: python -m experiments.generate_figures", file=sys.stderr)
            return 1
        if latency_only:
            print(
                "figure sources match the recorded results; only the measured latency "
                "labels differ (" + ", ".join(latency_only) + "), which track the host "
                "that measured them. Pass --strict to treat that as stale."
            )
            return 0
        print("figure sources match the recorded results.")
        return 0

    print(f"wrote {len(stale) + len(latency_only)} of {len(wanted)} figure sources to {FIGURES}")
    for name in wanted:
        rendered = (FIGURES / name).with_suffix(".pdf")
        if not rendered.is_file():
            print(f"  {name}: no rendered PDF yet")
    print(
        "\nRender with (requires network for the first npx fetch):\n"
        "  npx -y @mermaid-js/mermaid-cli -i paper/figures/NAME.mmd \\\n"
        "      -o paper/figures/NAME.pdf --pdfFit"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
