"""IaCSecBench — analysis and LaTeX table generation.

Consumes the raw tool output written by :mod:`evaluation.run_baselines`, applies
the finding-normalization engine, and produces:

* ``results/evaluation.json`` — the complete machine-readable result set;
* ``results/tables/*.tex``    — LaTeX tables ready for \\input into the manuscript;
* a console summary.

Reporting guarantees
--------------------
Metrics that are not estimable from the available corpus are reported as such
rather than as zero. Specificity requires ground-truth-compliant cases; MCC
requires both classes. A corpus consisting only of vulnerable cases supports a
recall estimate and nothing else, and the output says so explicitly instead of
printing a specificity of 0.00% that a reader would mistake for a measurement.

Tools that were not installed are listed as ``not_run`` and omitted from every
table. They are never assigned an assumed detection rate.

Every proportion is accompanied by an exact Clopper-Pearson interval, and every
pairwise comparison against the reference tool uses the exact binomial McNemar
test with Holm-Bonferroni correction across the tool family.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evaluation.corpus import Case, load_corpus
from evaluation.normalize import MATCH_LEVELS, ControlMap, MatchLevel, score_case
from evaluation.stats import (
    ConfusionMatrix,
    exact_mcnemar,
    holm_bonferroni,
)

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "results" / "raw"
MANIFEST = ROOT / "results" / "run_manifest.json"
OUT_JSON = ROOT / "results" / "evaluation.json"
TABLE_DIR = ROOT / "results" / "tables"
LEADERBOARD_CSV = ROOT / "leaderboard" / "results.csv"

REFERENCE_TOOL = "opa"

TOOL_LABELS = {
    "checkov": ("Checkov", "AST static analysis"),
    "tfsec": ("tfsec", "HCL lexical scanning"),
    "opa": ("OPA (plan-level)", "Rego over compiled plan"),
    "iacsecbench": ("IaCSecBench", "Composite pipeline"),
    "iacsb_layer1": ("IaCSecBench L1", "Repository-edge scanning"),
}

NOT_ESTIMABLE = "n/e"


@dataclass
class ToolResult:
    """Aggregated result for one tool at one strictness level."""

    tool: str
    level: MatchLevel
    matrix: ConfusionMatrix
    outcomes: dict[str, str]
    latencies_ms: list[float]
    n_errors: int
    n_unmapped: int
    n_unmapped_on_missed: int = 0
    n_resource_applicable: int = 0

    @property
    def specificity_estimable(self) -> bool:
        return self.matrix.negatives > 0

    @property
    def mcc_estimable(self) -> bool:
        return self.matrix.positives > 0 and self.matrix.negatives > 0

    def latency_summary(self) -> dict[str, float | None]:
        if not self.latencies_ms:
            return {"mean_ms": None, "sd_ms": None, "n": 0}
        return {
            "mean_ms": statistics.fmean(self.latencies_ms),
            "sd_ms": statistics.stdev(self.latencies_ms) if len(self.latencies_ms) > 1 else 0.0,
            "n": len(self.latencies_ms),
        }

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "tool": self.tool,
            "level": self.level,
            "confusion_matrix": self.matrix.to_dict(),
            "latency": self.latency_summary(),
            "n_execution_errors": self.n_errors,
            "n_unmapped_findings": self.n_unmapped,
            "n_unmapped_findings_on_missed_cases": self.n_unmapped_on_missed,
            "specificity_estimable": self.specificity_estimable,
            "mcc_estimable": self.mcc_estimable,
        }
        if not self.specificity_estimable:
            payload["confusion_matrix"]["specificity"] = None
            payload["confusion_matrix"]["balanced_accuracy"] = None
        if not self.mcc_estimable:
            payload["confusion_matrix"]["mcc"] = None
        return payload


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #


def _load_raw(tool: str, case_id: str) -> Any | None:
    path = RAW_DIR / tool / f"{case_id.replace('/', '__')}.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def aggregate(
    cases: list[Case], manifest: dict[str, Any], control_map: ControlMap
) -> tuple[dict[str, dict[MatchLevel, ToolResult]], dict[str, str]]:
    """Builds per-tool, per-level results plus a per-tool status map."""
    runs_by_key: dict[tuple[str, str], dict[str, Any]] = {
        (run["tool"], run["case_id"]): run for run in manifest.get("runs", [])
    }
    tools = sorted({run["tool"] for run in manifest.get("runs", [])})

    status: dict[str, str] = {}
    results: dict[str, dict[MatchLevel, ToolResult]] = {}

    for tool in tools:
        tool_runs = [runs_by_key[(tool, c.case_id)] for c in cases if (tool, c.case_id) in runs_by_key]
        if tool_runs and all(r["status"] == "not_installed" for r in tool_runs):
            status[tool] = "not_run"
            continue
        status[tool] = "run"

        latencies: list[float] = []
        n_errors = 0
        n_unmapped = 0
        # Unmapped findings only understate a tool where the tool *missed* the
        # case. On a case it already detected, or on a compliant case, an
        # unmapped rule changes nothing -- it is a detection of some other
        # control on incidental infrastructure. Counting the two situations
        # together turns a large, harmless number into an alarming one, so they
        # are counted apart.
        n_unmapped_on_missed = 0
        level_key = "all"
        resource_applicable: dict[str, int] = {"all": 0}
        per_level: dict[MatchLevel, dict[str, str]] = {lvl: {} for lvl in MATCH_LEVELS}
        counts: dict[MatchLevel, dict[str, int]] = {
            lvl: {"TP": 0, "FP": 0, "TN": 0, "FN": 0} for lvl in MATCH_LEVELS
        }

        for case in cases:
            run = runs_by_key.get((tool, case.case_id))
            if run is None:
                continue
            if run["status"] != "ok":
                n_errors += 1
                continue
            latencies.extend(run.get("latency_ms") or [])

            outcome = score_case(
                case_id=case.case_id,
                tool=tool,
                expected=case.expected,  # type: ignore[arg-type]
                expected_controls=case.canonical_controls,
                expected_resources=case.expected_resources or case.resource_types,
                payload=_load_raw(tool, case.case_id),
                control_map=control_map,
            )
            n_unmapped += len(outcome.unmapped_rules)
            if outcome.classification("control") == "FN" and outcome.unmapped_rules:
                n_unmapped_on_missed += len(outcome.unmapped_rules)
            if outcome.resource_matching_applicable:
                resource_applicable[level_key] += 1
            for level in MATCH_LEVELS:
                label = outcome.classification(level)
                counts[level][label] += 1
                per_level[level][case.case_id] = label

        results[tool] = {
            level: ToolResult(
                tool=tool,
                level=level,
                matrix=ConfusionMatrix(
                    tp=counts[level]["TP"],
                    fp=counts[level]["FP"],
                    tn=counts[level]["TN"],
                    fn=counts[level]["FN"],
                ),
                outcomes=per_level[level],
                latencies_ms=latencies,
                n_errors=n_errors,
                n_unmapped=n_unmapped,
                n_unmapped_on_missed=n_unmapped_on_missed,
                n_resource_applicable=resource_applicable["all"],
            )
            for level in MATCH_LEVELS
        }

    return results, status


def pairwise_comparisons(
    results: dict[str, dict[MatchLevel, ToolResult]],
    reference: str,
    level: MatchLevel,
    n_total: int,
) -> dict[str, Any]:
    """Exact McNemar comparisons of the reference tool against every other tool.

    Discordant counts include both error types: a case where the reference is
    correct and the comparator wrong contributes to ``b`` whether the
    comparator's error was a missed violation or a spurious finding.
    """
    if reference not in results:
        return {"error": f"reference tool {reference!r} produced no results"}

    ref_outcomes = results[reference][level].outcomes
    comparisons: dict[str, Any] = {}
    raw_p: dict[str, float] = {}

    for tool, levels in results.items():
        if tool == reference:
            continue
        other = levels[level].outcomes
        shared = sorted(set(ref_outcomes) & set(other))
        if not shared:
            continue

        b = c = 0
        for case_id in shared:
            ref_correct = ref_outcomes[case_id] in ("TP", "TN")
            other_correct = other[case_id] in ("TP", "TN")
            if ref_correct and not other_correct:
                b += 1
            elif other_correct and not ref_correct:
                c += 1

        result = exact_mcnemar(
            b, c, reference=reference, comparator=tool, n_total=len(shared)
        )
        comparisons[tool] = result.to_dict()
        comparisons[tool]["n_paired_cases"] = len(shared)
        raw_p[tool] = result.p_exact

    if raw_p:
        adjusted = holm_bonferroni(raw_p)
        for tool, entry in adjusted.items():
            comparisons[tool]["holm"] = entry

    return comparisons


# --------------------------------------------------------------------------- #
# LaTeX emission
# --------------------------------------------------------------------------- #


def _fmt_pct(value: float | None, estimable: bool = True) -> str:
    if not estimable or value is None:
        return NOT_ESTIMABLE
    return f"{value * 100:.2f}"


def _fmt_ci(matrix: ConfusionMatrix, which: str, estimable: bool = True) -> str:
    if not estimable:
        return NOT_ESTIMABLE
    interval = getattr(matrix, f"{which}_ci")().as_pct()
    return f"$[{interval.lower:.2f}, {interval.upper:.2f}]$"


def emit_performance_table(
    results: dict[str, dict[MatchLevel, ToolResult]],
    status: dict[str, str],
    level: MatchLevel,
    n_cases: int,
    n_positives: int,
    n_negatives: int,
) -> str:
    """Emits the main performance table with exact confidence intervals."""
    lines = [
        "% Generated by evaluation/analyze.py -- do not edit by hand.",
        "% Regenerate with: python -m evaluation.analyze",
        f"% Matching strictness level: {level}",
        "\\begin{table*}[!t]",
        "\\caption{Detection performance on the admissible corpus "
        f"($N = {n_cases}$: {n_positives} vulnerable, {n_negatives} compliant). "
        "Intervals are exact Clopper--Pearson at the 95\\% level. "
        f"Entries marked {NOT_ESTIMABLE} are not estimable from this corpus.}}",
        "\\label{tab:performance}",
        "\\centering",
        "\\small",
        "\\setlength{\\tabcolsep}{4pt}",
        "\\begin{tabular}{l c c c c c l c l c}",
        "\\toprule",
        "\\textbf{Tool} & \\textbf{TP} & \\textbf{FP} & \\textbf{TN} & \\textbf{FN} & "
        "\\textbf{Rec.\\ (\\%)} & \\textbf{Rec.\\ 95\\% CI} & "
        "\\textbf{Prec.\\ (\\%)} & \\textbf{Prec.\\ 95\\% CI} & \\textbf{MCC} \\\\",
        "\\midrule",
    ]

    for tool in sorted(results):
        if status.get(tool) != "run":
            continue
        result = results[tool][level]
        m = result.matrix
        label = TOOL_LABELS.get(tool, (tool, ""))[0]
        mcc = f"{m.mcc:.3f}" if result.mcc_estimable else NOT_ESTIMABLE
        lines.append(
            f"{label} & {m.tp} & {m.fp} & {m.tn} & {m.fn} & "
            f"{_fmt_pct(m.recall)} & {_fmt_ci(m, 'recall')} & "
            f"{_fmt_pct(m.precision)} & {_fmt_ci(m, 'precision')} & {mcc} \\\\"
        )

    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table*}", ""]

    not_run = sorted(t for t, s in status.items() if s == "not_run")
    if not_run:
        labels = ", ".join(TOOL_LABELS.get(t, (t, ""))[0] for t in not_run)
        lines.insert(
            -1,
            f"% Not installed in the measurement environment and therefore excluded: {labels}.",
        )
    return "\n".join(lines)


# Which tools constitute which validation layer of the composed pipeline.
# Layer 2 (native module testing) is absent by design: `terraform test` validates
# module behaviour -- variable constraints, outputs, conditional creation -- and
# is not a misconfiguration detector over single-resource security cases. Claiming
# a layer-2 detection count on this corpus would misrepresent what the layer does.
PIPELINE_LAYERS = {
    "L1 (repository edge)": "iacsb_layer1",
    "L3 (compiled plan)": "opa",
}
LAYER2_NOTE = (
    "Layer 2 (native module testing) is not scored: it validates module behaviour "
    "rather than detecting resource misconfiguration, so it has no detection "
    "count on this corpus."
)


def emit_layer_table(
    results: dict[str, dict[MatchLevel, ToolResult]],
    status: dict[str, str],
    level: MatchLevel,
    n_positives: int,
) -> str:
    """Emits layer attribution with explicit overlap between layers.

    Intersection sizes are reported alongside per-layer counts. A strictly
    additive attribution -- each layer detecting a disjoint case set -- is
    implausible on a real corpus, so the overlap is stated rather than left to be
    inferred from totals that happen to sum.
    """
    detected: dict[str, set[str]] = {}
    for label, tool in PIPELINE_LAYERS.items():
        if status.get(tool) != "run":
            continue
        outcomes = results[tool][level].outcomes
        detected[label] = {cid for cid, cls in outcomes.items() if cls == "TP"}

    lines = [
        "% Generated by evaluation/analyze.py -- do not edit by hand.",
        "\\begin{table}[!t]",
        "\\caption{Layer attribution over the vulnerable cases. Overlap is reported "
        "explicitly: layers are not assumed to detect disjoint sets. " + LAYER2_NOTE + "}",
        "\\label{tab:layers}",
        "\\centering",
        "\\small",
        "\\begin{tabular}{l r r}",
        "\\toprule",
        "\\textbf{Configuration} & \\textbf{Detected} & \\textbf{Recall (\\%)} \\\\",
        "\\midrule",
    ]

    def row(label: str, cases: set[str]) -> str:
        pct = (len(cases) / n_positives * 100.0) if n_positives else 0.0
        return f"{label} & {len(cases)} & {pct:.2f} \\\\"

    for label in sorted(detected):
        lines.append(row(label, detected[label]))

    if len(detected) >= 2:
        labels = sorted(detected)
        lines.append("\\midrule")
        for i, first in enumerate(labels):
            for second in labels[i + 1 :]:
                overlap = detected[first] & detected[second]
                lines.append(f"\\quad overlap: {first} $\\cap$ {second} & {len(overlap)} & "
                             f"{(len(overlap) / n_positives * 100.0) if n_positives else 0.0:.2f} \\\\")
        union: set[str] = set()
        for cases in detected.values():
            union |= cases
        lines.append("\\midrule")
        lines.append(f"\\textbf{{Union of scored layers}} & \\textbf{{{len(union)}}} & "
                     f"\\textbf{{{(len(union) / n_positives * 100.0) if n_positives else 0.0:.2f}}} \\\\")

    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(lines)


def emit_strictness_table(
    results: dict[str, dict[MatchLevel, ToolResult]], status: dict[str, str]
) -> str:
    """Emits recall under each matching strictness level.

    The gap between the ``control`` and ``any`` columns quantifies how much of a
    tool's apparent detection rate comes from findings unrelated to the
    vulnerability the case was authored to contain.
    """
    lines = [
        "% Generated by evaluation/analyze.py -- do not edit by hand.",
        "\\begin{table}[!t]",
        "\\caption{Recall under three finding-matching criteria. "
        "\\emph{Control} credits a detection only when the tool's rule maps to the "
        "control the case violates; \\emph{resource} credits any finding on the "
        "expected resource; \\emph{any} credits any finding whatsoever. The spread "
        "measures attribution precision.}",
        "\\label{tab:strictness}",
        "\\centering",
        "\\small",
        "\\begin{tabular}{l c c c}",
        "\\toprule",
        "\\textbf{Tool} & \\textbf{Control (\\%)} & \\textbf{Resource (\\%)} & "
        "\\textbf{Any (\\%)} \\\\",
        "\\midrule",
    ]
    for tool in sorted(results):
        if status.get(tool) != "run":
            continue
        label = TOOL_LABELS.get(tool, (tool, ""))[0]
        cells = " & ".join(
            _fmt_pct(
                results[tool][lvl].matrix.recall,
                estimable=(lvl != "resource" or results[tool][lvl].n_resource_applicable > 0),
            )
            for lvl in ("control", "resource", "any")
        )
        lines.append(f"{label} & {cells} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(lines)


def emit_latency_table(
    results: dict[str, dict[MatchLevel, ToolResult]], status: dict[str, str], repeats: int
) -> str:
    lines = [
        "% Generated by evaluation/analyze.py -- do not edit by hand.",
        "\\begin{table}[!t]",
        # The plan-level exclusion belongs in the caption, not only in the prose
        # that surrounds it. A table is extracted, pasted into slides and quoted in
        # reviews on its own, and read that way an 18 ms figure next to a 2.4 s one
        # invites a conclusion about relative cost that the measurement does not
        # support.
        f"\\caption{{Measured per-case execution latency over {repeats} repetitions. "
        "Values are mean $\\pm$ standard deviation on the environment recorded in "
        "\\texttt{results/run\\_manifest.json}. Each tool is measured at its own "
        "interface: the plan-level figure covers policy evaluation over an "
        "already-compiled plan document and excludes the \\texttt{terraform init} "
        "and \\texttt{terraform plan} invocations that produce it, which dominate "
        "that layer's wall-clock cost in continuous integration. It is therefore a "
        "lower bound, and is not comparable with the source-level figures, which "
        "have no equivalent preparation step.}",
        "\\label{tab:latency}",
        "\\centering",
        "\\small",
        "\\begin{tabular}{l l r}",
        "\\toprule",
        "\\textbf{Tool} & \\textbf{Evaluation layer} & \\textbf{Latency (ms)} \\\\",
        "\\midrule",
    ]
    for tool in sorted(results):
        if status.get(tool) != "run":
            continue
        label, category = TOOL_LABELS.get(tool, (tool, "-"))
        summary = results[tool]["control"].latency_summary()
        if summary["mean_ms"] is None:
            cell = NOT_ESTIMABLE
        else:
            cell = f"${summary['mean_ms']:.1f} \\pm {summary['sd_ms']:.1f}$"
        lines.append(f"{label} & {category} & {cell} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(lines)


def emit_mcnemar_table(comparisons: dict[str, Any], reference: str) -> str:
    lines = [
        "% Generated by evaluation/analyze.py -- do not edit by hand.",
        "\\begin{table}[!t]",
        "\\caption{Exact McNemar comparisons against "
        f"{TOOL_LABELS.get(reference, (reference, ''))[0]}. "
        "$b$ counts cases the reference classifies correctly and the comparator "
        "does not, counting both missed violations and spurious findings; $c$ is "
        "the converse. $p$ is the two-sided exact binomial value, "
        "$p_{\\text{adj}}$ its Holm--Bonferroni correction across the tool family. "
        "The odds ratio carries a Haldane--Anscombe correction so that a zero "
        "discordant cell yields a finite estimate.}",
        "\\label{tab:mcnemar}",
        "\\centering",
        "\\small",
        "\\setlength{\\tabcolsep}{4pt}",
        "\\begin{tabular}{l c c c c c c}",
        "\\toprule",
        "\\textbf{Comparator} & \\textbf{$b$} & \\textbf{$c$} & \\textbf{$p$} & "
        "\\textbf{$p_{\\text{adj}}$} & \\textbf{OR} & \\textbf{Cohen's $g$} \\\\",
        "\\midrule",
    ]
    if "error" in comparisons:
        lines.append(f"\\multicolumn{{7}}{{l}}{{{comparisons['error']}}} \\\\")
    for tool, entry in sorted(comparisons.items()):
        if tool == "error":
            continue
        label = TOOL_LABELS.get(tool, (tool, ""))[0]
        p_raw = entry["p_exact"]
        p_adj = entry.get("holm", {}).get("p_adjusted", p_raw)
        lines.append(
            f"{label} & {entry['b']} & {entry['c']} & "
            f"{_fmt_p(p_raw)} & {_fmt_p(p_adj)} & "
            f"{entry['odds_ratio']:.2f} & {entry['cohens_g']:.3f} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(lines)


def _fmt_p(value: float) -> str:
    if value < 0.001:
        return "$<0.001$"
    return f"${value:.3f}$"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="IaCSecBench analysis and table generation")
    parser.add_argument(
        "--level",
        choices=MATCH_LEVELS,
        default="control",
        help="matching strictness for the headline tables",
    )
    parser.add_argument(
        "--reference", default=REFERENCE_TOOL, help="tool to compare all others against"
    )
    parser.add_argument("--no-tables", action="store_true", help="skip LaTeX emission")
    args = parser.parse_args(argv)

    if not MANIFEST.is_file():
        print(f"No run manifest at {MANIFEST.relative_to(ROOT)}.")
        print("Run: python -m evaluation.run_baselines --all")
        return 2

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    control_map = ControlMap.load()
    scanned = set(manifest.get("scanned_case_ids") or [])

    all_cases = load_corpus(control_map)
    cases = [c for c in all_cases if c.case_id in scanned]
    if not cases:
        print("The manifest references no cases that are currently loadable.")
        return 2

    results, status = aggregate(cases, manifest, control_map)
    if not any(s == "run" for s in status.values()):
        print("No tool produced usable output; nothing to analyse.")
        return 2

    n_positives = sum(1 for c in cases if c.expected == "VIOLATION")
    n_negatives = len(cases) - n_positives
    comparisons = pairwise_comparisons(results, args.reference, args.level, len(cases))

    # ---- console summary -------------------------------------------------- #
    print("=" * 78)
    print(f"IaCSecBench evaluation  (matching level: {args.level})")
    print("=" * 78)
    env = manifest.get("environment", {})
    print(f"\nEnvironment : {env.get('platform')}  |  commit {str(env.get('git_commit'))[:12]}")
    print(f"Corpus      : {len(cases)} cases  ({n_positives} vulnerable, {n_negatives} compliant)")
    print(f"Repeats     : {manifest.get('repeats')} executions per tool-case")

    # Taken from the control map that scored these findings, not from the
    # manifest's snapshot. The manifest records the map as it stood when the
    # scanners ran, but scoring re-reads the file, so a map corrected after the
    # run would otherwise be reported with its pre-correction defect count --
    # overstating the caveat and understating the audit that removed it.
    unverified = sorted(control_map.unverified_controls)
    recorded = manifest.get("control_map_unverified") or []
    if unverified:
        print(f"\nWARNING: {len(unverified)} control-map entries are unverified.")
        print("         Results are provisional until they are confirmed.")
    if sorted(recorded) != unverified:
        print(
            f"\nNote: the control map was corrected after this run "
            f"({len(recorded)} unverified at scan time, {len(unverified)} now). "
            "Scoring used the corrected map; latency and tool versions still "
            "come from the recorded run."
        )

    if n_negatives == 0:
        print("\nWARNING: the corpus contains no compliant baseline cases.")
        print("         Specificity, balanced accuracy and MCC are not estimable.")
        print("         False-positive behaviour cannot be characterised at all.")

    print(f"\n{'tool':<18} {'TP':>4} {'FP':>4} {'TN':>4} {'FN':>4}  "
          f"{'recall':>8}  {'recall 95% CI':>20}  {'latency':>14}")
    print("-" * 78)
    for tool in sorted(results):
        if status.get(tool) != "run":
            continue
        r = results[tool][args.level]
        m = r.matrix
        ci = m.recall_ci().as_pct()
        lat = r.latency_summary()
        lat_cell = (
            f"{lat['mean_ms']:.1f}±{lat['sd_ms']:.1f}" if lat["mean_ms"] is not None else "-"
        )
        print(
            f"{TOOL_LABELS.get(tool, (tool, ''))[0]:<18} {m.tp:>4} {m.fp:>4} {m.tn:>4} {m.fn:>4}  "
            f"{m.recall * 100:>7.2f}%  [{ci.lower:>6.2f}, {ci.upper:>6.2f}]  {lat_cell:>14}"
        )

    for tool, state in sorted(status.items()):
        if state == "not_run":
            print(f"{TOOL_LABELS.get(tool, (tool, ''))[0]:<18} not installed -- excluded")

    print("\nRecall by matching strictness")
    print("-" * 78)
    print(f"{'tool':<18} {'control':>9} {'resource':>10} {'any':>8}")
    for tool in sorted(results):
        if status.get(tool) != "run":
            continue
        row = results[tool]
        applicable = row["resource"].n_resource_applicable > 0
        control = f"{row['control'].matrix.recall * 100:>8.2f}%"
        resource = f"{row['resource'].matrix.recall * 100:>9.2f}%" if applicable else f"{NOT_ESTIMABLE:>10}"
        any_level = f"{row['any'].matrix.recall * 100:>7.2f}%"
        print(f"{TOOL_LABELS.get(tool, (tool, ''))[0]:<18} {control} {resource} {any_level}")

    total_unmapped = sum(results[t][args.level].n_unmapped for t in results if status[t] == "run")
    total_unmapped_on_missed = sum(
        results[t][args.level].n_unmapped_on_missed for t in results if status[t] == "run"
    )
    if total_unmapped:
        print(f"\n{total_unmapped} findings carried rule identifiers absent from the control map.")
        if total_unmapped_on_missed:
            print(
                f"         {total_unmapped_on_missed} of them landed on cases the emitting "
                "tool missed, so those tools may be under-credited."
            )
        else:
            print(
                "         None landed on a case its tool missed, so no reported recall is "
                "under-credited by them."
            )
        print("Run `python -m evaluation.normalize --emit-unmapped` and extend it.")

    # ---- artefacts -------------------------------------------------------- #
    payload = {
        "environment": env,
        "corpus": {
            "n_cases": len(cases),
            "n_vulnerable": n_positives,
            "n_compliant": n_negatives,
            "case_ids": [c.case_id for c in cases],
        },
        "matching_level": args.level,
        "reference_tool": args.reference,
        "control_map_schema": manifest.get("control_map_schema"),
        "control_map_unverified": unverified,
        "tool_status": status,
        "results": {
            tool: {lvl: results[tool][lvl].to_dict() for lvl in MATCH_LEVELS}
            for tool in results
            if status[tool] == "run"
        },
        "pairwise_mcnemar": comparisons,
        "caveats": _caveats(
            n_negatives, unverified, total_unmapped, total_unmapped_on_missed
        ),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_JSON.relative_to(ROOT)}")

    if not args.no_tables:
        TABLE_DIR.mkdir(parents=True, exist_ok=True)
        tables = {
            "performance.tex": emit_performance_table(
                results, status, args.level, len(cases), n_positives, n_negatives
            ),
            "strictness.tex": emit_strictness_table(results, status),
            "latency.tex": emit_latency_table(results, status, manifest.get("repeats", 1)),
            "mcnemar.tex": emit_mcnemar_table(comparisons, args.reference),
            "layers.tex": emit_layer_table(results, status, args.level, n_positives),
        }
        malformed = {n: p for n, c in tables.items() if (p := _latex_defects(c))}
        if malformed:
            print("\nerror: generated tables are malformed and were not written.", file=sys.stderr)
            for name, problems in malformed.items():
                for problem in problems:
                    print(f"  {name}: {problem}", file=sys.stderr)
            print(
                "\nA malformed table breaks the manuscript build at a point far from "
                "its cause.\nFix the emitter in evaluation/analyze.py.",
                file=sys.stderr,
            )
            return 1
        for name, content in tables.items():
            (TABLE_DIR / name).write_text(content + "\n", encoding="utf-8")
        print(f"Wrote {len(tables)} LaTeX tables to {TABLE_DIR.relative_to(ROOT)}/")

        LEADERBOARD_CSV.parent.mkdir(parents=True, exist_ok=True)
        LEADERBOARD_CSV.write_text(
            emit_leaderboard_csv(results, status, args.level) + "\n", encoding="utf-8"
        )
        print(f"Wrote {LEADERBOARD_CSV.relative_to(ROOT)}")

    print("\nCaveats that must accompany these numbers:")
    for caveat in payload["caveats"]:
        print(f"  - {caveat}")
    return 0


def emit_leaderboard_csv(
    results: dict[str, dict[str, ToolResult]],
    status: dict[str, str],
    level: MatchLevel,
) -> str:
    """Renders the public leaderboard from measured confusion matrices.

    ``leaderboard/results.csv`` was previously written by evaluation/score.py,
    which multiplies corpus counts by hardcoded per-tool rates and pins the
    reference implementation to a perfect score. Emitting the same path from the
    measured matrices is what stops the fabricated version from being the only
    one that exists -- a file no measuring stage writes will keep being
    regenerated by the stage that fabricates it.

    Only tools that actually executed appear. A tool that was absent or errored
    on every case is omitted rather than written with zeros, because a zero row
    and a missing row mean different things and a CSV cannot caveat itself.
    """
    header = (
        "tool_name,category,total_cases,tp,fp,tn,fn,"
        "accuracy_pct,precision_pct,recall_pct,f1_score_pct,fpr_pct,fnr_pct,"
        "recall_ci_low_pct,recall_ci_high_pct,latency_mean_ms,latency_sd_ms,"
        "latency_samples,matching_level"
    )
    lines = [header]
    ranked = sorted(
        (t for t in results if status[t] == "run"),
        key=lambda t: results[t][level].matrix.recall,
        reverse=True,
    )
    for tool in ranked:
        result = results[tool][level]
        m = result.matrix
        label, category = TOOL_LABELS.get(tool, (tool, ""))
        ci = m.recall_ci()
        latency = result.latency_summary()

        def num(value: float | None, digits: int = 2) -> str:
            return "" if value is None else f"{value:.{digits}f}"

        lines.append(
            ",".join(
                [
                    label,
                    category,
                    str(m.total),
                    str(m.tp),
                    str(m.fp),
                    str(m.tn),
                    str(m.fn),
                    num(m.accuracy * 100),
                    num(m.precision * 100),
                    num(m.recall * 100),
                    num(m.f1 * 100),
                    num((1 - m.specificity) * 100) if result.specificity_estimable else "",
                    num((1 - m.recall) * 100),
                    num(ci.as_pct().lower) if ci else "",
                    num(ci.as_pct().upper) if ci else "",
                    num(latency["mean_ms"], 1),
                    num(latency["sd_ms"], 1),
                    str(latency["n"]),
                    level,
                ]
            )
        )
    return "\n".join(lines)


def _latex_defects(content: str) -> list[str]:
    """Reports structural defects in a generated LaTeX table.

    A stray brace in an emitter's caption string surfaces during typesetting as
    ``Extra }, or forgotten \\endgroup`` attributed to the generated file, which
    gives no indication of which emitter produced it. Catching it at generation
    time names the emitter instead. Escaped braces are discounted, since
    ``\\{`` is a literal character rather than a group delimiter.
    """
    defects: list[str] = []
    unescaped = re.sub(r"\\[{}]", "", content)
    delta = unescaped.count("{") - unescaped.count("}")
    if delta:
        direction = "unclosed {" if delta > 0 else "extra }"
        defects.append(f"brace imbalance ({direction} x{abs(delta)})")

    for index, line in enumerate(content.splitlines(), start=1):
        bare = re.sub(r"\\[{}]", "", line)
        if line.lstrip().startswith("\\caption") and bare.count("{") != bare.count("}"):
            defects.append(f"line {index}: caption braces do not balance on one line")

    for environment in ("table", "tabular"):
        opens = content.count(f"\\begin{{{environment}}}")
        closes = content.count(f"\\end{{{environment}}}")
        if opens != closes:
            defects.append(f"{environment}: {opens} begin vs {closes} end")

    if "\\caption" in content and "\\label" not in content:
        defects.append("caption without label; \\ref to this table would print '??'")

    return defects


def _caveats(
    n_negatives: int,
    unverified: list[str],
    n_unmapped: int,
    n_unmapped_on_missed: int,
) -> list[str]:
    caveats = []
    if n_negatives == 0:
        caveats.append(
            "The corpus has no compliant baselines, so no false-positive rate, "
            "specificity, balanced accuracy or MCC can be reported."
        )
    if unverified:
        caveats.append(
            f"{len(unverified)} control-map entries are unverified against tool output; "
            "detection may be under-credited for affected controls."
        )
    if n_unmapped:
        # Whether unmapped findings understate anything is measurable, not
        # assumable. An unmapped rule matters only on a case the tool missed at
        # control level; anywhere else it is a detection of a different control on
        # incidental infrastructure, and excluding it is correct rather than
        # unfair. Asserting understatement without checking would overstate the
        # uncertainty as surely as ignoring it would understate it.
        if n_unmapped_on_missed:
            caveats.append(
                f"{n_unmapped} findings were unmappable and are excluded from "
                f"control-level scoring. {n_unmapped_on_missed} of them occurred on "
                "cases the emitting tool missed, so recall for those tools may be "
                "under-credited; extend the control map to resolve them."
            )
        else:
            caveats.append(
                f"{n_unmapped} findings were unmappable and are excluded from "
                "control-level scoring. None occurred on a case its tool missed, so "
                "no reported recall is under-credited by them: they are detections "
                "of controls other than the one under test, on infrastructure the "
                "case declares incidentally."
            )
    caveats.append(
        "Comparator tools ran with default rulesets; the plan-level policy set was "
        "authored with knowledge of the corpus. This asymmetry favours the reference."
    )
    return caveats


if __name__ == "__main__":
    raise SystemExit(main())
