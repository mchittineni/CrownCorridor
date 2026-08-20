#!/usr/bin/env python3
"""Measures the source-level scanners over the unlabelled external subset.

What this measures, and what it deliberately does not
----------------------------------------------------
The 25 repositories in ``benchmark/external/aws_samples/manifest.json`` carry no
ground-truth label. Nothing here computes accuracy, precision, recall, or a
confusion matrix, and nothing here may be combined with the labelled corpus's
numbers. Any such figure would be fabricated: there is no key to score against.

What an unlabelled subset does support is everything that needs no key:

* **Alert volume.** Findings per thousand lines, per tool, on production-shaped
  code. A practitioner's adoption cost is the count they must triage.
* **Cross-tool agreement.** Where two scanners examine the same resource and
  reach the same canonical control, they corroborate. Where one is silent, at
  most one of them is right. Disagreement is measurable without a key, and it
  bounds how much of the labelled corpus's apparent parity is real.
* **Module-boundary reach.** Every case in the labelled corpus is a single flat
  directory with no module indirection, so the labelled results cannot say
  whether a scanner resolves a value across a ``module`` call at all. Here the
  findings are attributed to root or to a module subtree, which answers it.

Why it does not reuse ``run_tool_on_case``
------------------------------------------
That function copies ``case_dir.glob("*.tf")`` -- flat, non-recursive -- into a
temporary directory. On a real repository that silently discards every module
subtree, which is precisely the structure under test: the scan would appear to
succeed while measuring a fraction of the configuration. The scanners are
therefore invoked on the work tree in place. The commands themselves come from
``run_baselines.TOOL_SPECS``, so the flags remain the ones the manifest records.

Usage
-----
    python -m evaluation.external                 # measure and write results
    python -m evaluation.external --tool checkov  # one scanner only
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from evaluation.normalize import ControlMap
from evaluation.run_baselines import TOOL_SPECS

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "benchmark" / "external" / "aws_samples" / "manifest.json"
CORPUS_DIR = ROOT / ".external-corpus"
OUT_JSON = ROOT / "results" / "external_subset.json"
TABLE_DIR = ROOT / "results" / "tables"
RAW_DIR = ROOT / "results" / "raw" / "external"

# Only the source-level scanners. OPA is a plan-level layer: it would need real
# credentials and a live `terraform plan` per repository, and the reference policy
# was authored against the labelled corpus, so including it here would compare a
# corpus-aware policy against corpus-blind scanners on unfamiliar code.
TOOLS = ("checkov", "tfsec", "trivy")


def _load_manifest() -> dict:
    if not MANIFEST.is_file():
        sys.exit(f"error: {MANIFEST.relative_to(ROOT)} not found.")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _sloc(repo_dir: Path) -> int:
    total = 0
    for tf in repo_dir.rglob("*.tf"):
        if ".git" in tf.parts:
            continue
        try:
            text = tf.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        total += sum(1 for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#"))
    return total


def repo_relative(path: str, repo_dir: Path) -> str:
    """Normalises a reported file path to one relative to the repository root.

    The three scanners disagree about what a path is, and the disagreement is
    silent. On the same file Checkov reports ``/main.tf``, tfsec reports the full
    absolute path, and Trivy reports ``main.tf``. Reading any of them as a plain
    relative path makes a root-level finding look nested -- ``Path('/main.tf')``
    has two parts -- which would have inflated the module-reach figure below to
    100% for two tools out of three.
    """
    text = str(path).strip()
    if not text:
        return ""
    # Both spellings of the root are tried. A scanner reports whichever path it was
    # handed, while ``resolve()`` follows symlinks -- on macOS ``/tmp`` becomes
    # ``/private/tmp`` -- so matching only the resolved form silently fails to strip
    # the prefix whenever any component of the path is a symlink, and every root
    # finding then reads as nested.
    for prefix in {str(repo_dir), str(repo_dir.resolve())}:
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break
    return text.lstrip("/")


def in_module(path: str, repo_dir: Path) -> bool:
    """True when a finding's file sits below the repository root.

    A finding reported here proves the scanner walked past the top-level
    directory: either it followed a ``module`` call or it recursed on its own.
    """
    parts = Path(repo_relative(path, repo_dir)).parts
    return len(parts) > 1


def resource_key(resource: str) -> str:
    """Canonicalises a resource identifier for cross-tool comparison.

    All three scanners name a resource ``type.name``, which makes them directly
    comparable -- but tfsec sometimes appends the offending attribute, reporting
    ``aws_db_instance.rdsdb2.deletion_protection`` where the others report
    ``aws_db_instance.rdsdb2``. Truncating to the first two segments compares the
    resource the tools actually examined rather than which field each objected to.
    """
    return ".".join(str(resource).split(".")[:2])


def scan(tool: str, repo_dir: Path, repo: str) -> dict[str, Any]:
    """Runs one scanner over one work tree, in place, and returns its raw outcome."""
    spec = TOOL_SPECS[tool]
    if spec.resolve() is None:
        return {"status": "not_installed"}

    command = spec.build_command(repo_dir)
    try:
        proc = subprocess.run(
            command, capture_output=True, text=True, timeout=1800, check=False, cwd=repo_dir
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}

    if proc.returncode not in spec.ok_exit_codes:
        return {
            "status": "error",
            "exit_code": proc.returncode,
            "stderr": (proc.stderr or "").strip()[:400],
        }

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{tool}__{repo.replace('/', '_')}.json"
    raw_path.write_text(proc.stdout, encoding="utf-8")
    # Scan duration is deliberately neither timed nor recorded. Latency is a
    # property of the measuring host, not of the subset, and this subset makes no
    # latency claim -- the labelled corpus reports timing, on a quiet machine.
    # Leaving it out is what makes this artefact byte-reproducible: every other
    # field is deterministic, so two runs on different hardware produce the same
    # file, and no one can quote a shared-runner number that was never publishable.
    return {
        "status": "ok",
        "exit_code": proc.returncode,
        "raw_path": str(raw_path.relative_to(ROOT)),
    }


def _findings(tool: str, raw_path: Path, control_map: ControlMap) -> list[dict[str, Any]]:
    """Parses one raw scanner output into normalized finding records.

    Uses the same per-tool parsers as the labelled pipeline, so a native rule
    identifier resolves to the same canonical control in both. ``normalize.Finding``
    is not reused: it carries a ``case_id`` and a ground-truth-oriented shape that
    would be meaningless here, and filling those fields with placeholders is how an
    unlabelled record later gets mistaken for a scored one.
    """
    from evaluation.normalize import _parse_checkov, _parse_tfsec, _parse_trivy

    parsers = {"checkov": _parse_checkov, "tfsec": _parse_tfsec, "trivy": _parse_trivy}
    try:
        payload = json.loads(raw_path.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError:
        return []

    out: list[dict[str, Any]] = []
    # Parsers yield (rule_id, resource, severity, description, file, line).
    for rule_id, resource, severity, _description, path, line in parsers[tool](payload):
        out.append(
            {
                "rule_id": rule_id,
                "controls": sorted(control_map.controls_for(tool, rule_id)),
                "resource": resource,
                "severity": severity,
                "file": path,
                "line": line,
            }
        )
    return out


def measure(tools: tuple[str, ...]) -> dict[str, Any]:
    doc = _load_manifest()
    control_map = ControlMap.load()
    repos = doc["repositories"]

    missing = [r["repo"] for r in repos if not (CORPUS_DIR / r["repo"].replace("/", "_")).is_dir()]
    if missing:
        sys.exit(
            f"error: {len(missing)} of {len(repos)} repositories are not materialised.\n"
            "       Run: python -m experiments.fetch_external"
        )

    per_repo: list[dict[str, Any]] = []
    for entry in repos:
        repo = entry["repo"]
        repo_dir = CORPUS_DIR / repo.replace("/", "_")
        sloc = _sloc(repo_dir)
        record: dict[str, Any] = {
            "repo": repo,
            "commit": entry["commit"],
            "sloc": sloc,
            "tools": {},
        }

        for tool in tools:
            outcome = scan(tool, repo_dir, repo)
            if outcome.get("status") != "ok":
                record["tools"][tool] = outcome
                continue
            found = _findings(tool, ROOT / outcome["raw_path"], control_map)
            mapped = [f for f in found if f["controls"]]
            in_mod = [f for f in found if in_module(f["file"], repo_dir)]
            record["tools"][tool] = {
                **outcome,
                "findings": len(found),
                "mapped": len(mapped),
                "unmapped": len(found) - len(mapped),
                "in_module": len(in_mod),
                "controls": sorted({c for f in mapped for c in f["controls"]}),
                # Two agreement keys, because they answer different questions.
                # A control claim needs the control map, so it only covers the
                # mapped subset. A resource is named identically by all three
                # scanners, so it needs no map: it asks whether they flagged the
                # same thing at all, regardless of which rule each one fired.
                "claims": sorted(
                    {f"{c}|{resource_key(f['resource'])}" for f in mapped for c in f["controls"]}
                ),
                "resources": sorted({resource_key(f["resource"]) for f in found if f["resource"]}),
            }
        per_repo.append(record)

    return {
        "subset": doc["dataset"],
        "labelled": False,
        "scoring": "excluded-from-accuracy",
        "$comment": (
            "Unlabelled. Contains no accuracy, precision or recall figure and must "
            "not be merged with results/evaluation.json."
        ),
        "control_map_schema_version": control_map.schema_version,
        "repositories": per_repo,
        "aggregate": _aggregate(per_repo, tools),
    }


def _aggregate(per_repo: list[dict], tools: tuple[str, ...]) -> dict[str, Any]:
    agg: dict[str, Any] = {"per_tool": {}, "agreement": {}}
    for tool in tools:
        ok = [r for r in per_repo if r["tools"].get(tool, {}).get("status") == "ok"]
        f = sum(r["tools"][tool]["findings"] for r in ok)
        m = sum(r["tools"][tool]["mapped"] for r in ok)
        im = sum(r["tools"][tool]["in_module"] for r in ok)
        sloc = sum(r["sloc"] for r in ok) or 1
        agg["per_tool"][tool] = {
            "repositories_scanned": len(ok),
            "findings": f,
            "mapped": m,
            "unmapped": f - m,
            "unmapped_share": round((f - m) / f, 4) if f else None,
            "in_module": im,
            "in_module_share": round(im / f, 4) if f else None,
            "findings_per_kloc": round(f / sloc * 1000, 2),
            "controls": sorted({c for r in ok for c in r["tools"][tool]["controls"]}),
        }

    # Pairwise agreement, Jaccard, over the repositories both tools scanned
    # successfully. Neither measure needs ground truth: they report how far the
    # scanners corroborate one another, not which of them is right.
    #
    # Reported at both granularities on purpose. Control-level agreement covers
    # only findings the control map recognises, so on unfamiliar code it can be
    # near-empty and would read as total disagreement. Resource-level agreement
    # asks the map-free question -- did they flag the same resource at all -- and
    # the gap between the two is itself informative: the same resource reached by
    # different rules is corroboration the control map cannot currently express.
    for i, a in enumerate(tools):
        for b in tools[i + 1 :]:
            counts = {"claims": [0, 0], "resources": [0, 0]}
            for r in per_repo:
                ra, rb = r["tools"].get(a, {}), r["tools"].get(b, {})
                if ra.get("status") != "ok" or rb.get("status") != "ok":
                    continue
                for key in counts:
                    sa, sb = set(ra[key]), set(rb[key])
                    counts[key][0] += len(sa & sb)
                    counts[key][1] += len(sa | sb)
            ci, cu = counts["claims"]
            ri, ru = counts["resources"]
            agg["agreement"][f"{a}|{b}"] = {
                "shared_claims": ci,
                "union_claims": cu,
                "jaccard": round(ci / cu, 4) if cu else None,
                "shared_resources": ri,
                "union_resources": ru,
                "resource_jaccard": round(ri / ru, 4) if ru else None,
            }
    return agg


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", maxsplit=1)[0])
    ap.add_argument("--tool", action="append", choices=TOOLS, help="restrict to one scanner")
    args = ap.parse_args(argv)
    tools = tuple(args.tool) if args.tool else TOOLS

    result = measure(tools)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    # Tables are only written for a full run. A --tool subset would emit a table
    # that looks like the comparison but silently omits a scanner.
    wrote_tables = False
    if tuple(tools) == TOOLS:
        from evaluation.tables import latex_defects

        for name, content in (
            ("external.tex", emit_external_table(result)),
            ("external_agreement.tex", emit_agreement_table(result)),
        ):
            defects = latex_defects(content)
            if defects:
                print(f"error: {name} is malformed: {'; '.join(defects)}", file=sys.stderr)
                return 1
            path = TABLE_DIR / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        wrote_tables = True

    print(f"wrote {OUT_JSON.relative_to(ROOT)}")
    if wrote_tables:
        print(f"wrote {(TABLE_DIR / 'external.tex').relative_to(ROOT)}")
        print(f"wrote {(TABLE_DIR / 'external_agreement.tex').relative_to(ROOT)}")
    else:
        print("tables not written: --tool restricts the run to a subset of scanners")
    print()
    print(f"{'tool':10s} {'repos':>5s} {'find':>6s} {'unmap':>6s} {'/kLOC':>7s} {'in-mod':>7s}")
    for tool, s in result["aggregate"]["per_tool"].items():
        share = f"{s['in_module_share']:.0%}" if s["in_module_share"] is not None else "n/a"
        print(
            f"{tool:10s} {s['repositories_scanned']:5d} {s['findings']:6d} "
            f"{s['unmapped']:6d} {s['findings_per_kloc']:7.1f} {share:>7s}"
        )
    print("\npairwise agreement (Jaccard) -- no ground truth involved:")
    print(f"  {'pair':22s} {'by control':>22s} {'by resource':>22s}")
    for pair, s in result["aggregate"]["agreement"].items():
        j = f"{s['jaccard']:.3f}" if s["jaccard"] is not None else "n/a"
        rj = f"{s['resource_jaccard']:.3f}" if s["resource_jaccard"] is not None else "n/a"
        print(
            f"  {pair:22s} {j:>7s} ({s['shared_claims']:>4d}/{s['union_claims']:<5d})"
            f" {rj:>9s} ({s['shared_resources']:>4d}/{s['union_resources']:<5d})"
        )
    return 0


# --------------------------------------------------------------------------- #
# LaTeX emission
# --------------------------------------------------------------------------- #


def emit_external_table(result: dict[str, Any]) -> str:
    """Emits the unlabelled-subset table.

    The caption states the subset is unlabelled and names what the columns are
    not. A reader who meets this table after the confusion-matrix tables will
    otherwise read "findings" as "true positives", which is the one inference the
    subset cannot support.
    """
    per_tool = result["aggregate"]["per_tool"]
    repos = result["repositories"]
    n_repos = len(repos)
    sloc = sum(r["sloc"] for r in repos)

    lines = [
        "% Generated by evaluation/external.py -- do not edit by hand.",
        "% Regenerate with: python -m evaluation.external",
        "% UNLABELLED SUBSET. No column here is a detection rate. There is no",
        "% ground truth for these repositories, so nothing in this table may be",
        "% combined with Table~\\ref{tab:performance} or Table~\\ref{tab:rates}.",
        "\\begin{table}[!t]",
        "\\caption{Scanner behaviour on the unlabelled external subset: "
        f"{n_repos} third-party AWS-published Terraform repositories "
        f"({sloc:,} lines), each pinned to an exact commit. "
        "These configurations carry no ground-truth label, so the columns count "
        "\\emph{alerts}, not detections: no value here is a true-positive or a "
        "recall figure. `Unmapped' is the share of a tool's alerts whose native "
        "rule has no entry in the canonical control map, and `In module' the "
        "share reported below the repository root.}",
        "\\label{tab:external}",
        "\\centering",
        "\\small",
        "\\setlength{\\tabcolsep}{5pt}",
        "\\begin{tabular}{@{}l r r r r@{}}",
        "\\toprule",
        "\\textbf{Tool} & \\textbf{Alerts} & \\textbf{Per kLOC} & "
        "\\textbf{Unmapped} & \\textbf{In module} \\\\",
        "\\midrule",
    ]

    def percent(value: float | None) -> str:
        """A share as a LaTeX-safe percentage. Bare ``%`` starts a comment."""
        return "--" if value is None else format(value, ".0%").replace("%", "\\%")

    for tool in sorted(per_tool):
        s = per_tool[tool]
        lines.append(
            f"{tool} & {s['findings']} & {s['findings_per_kloc']:.1f} & "
            f"{percent(s['unmapped_share'])} & {percent(s['in_module_share'])} \\\\"
        )

    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
    ]
    return "\n".join(lines)


def emit_agreement_table(result: dict[str, Any]) -> str:
    """Emits pairwise agreement, which needs no ground truth to interpret."""
    agreement = result["aggregate"]["agreement"]
    lines = [
        "% Generated by evaluation/external.py -- do not edit by hand.",
        "% Regenerate with: python -m evaluation.external",
        "\\begin{table}[!t]",
        "\\caption{Pairwise agreement between the source-level scanners on the "
        "unlabelled external subset, as Jaccard indices over the repositories both "
        "tools scanned. `By control' compares canonical controls and so covers only "
        "mapped alerts; `by resource' compares the Terraform resource each tool "
        "flagged and needs no control map. Agreement is not correctness: two tools "
        "may corroborate one another and both be wrong. Note that Trivy is tfsec's "
        "successor and inherits its rule set, so that pair is not an independent "
        "comparison.}",
        "\\label{tab:external-agreement}",
        "\\centering",
        "\\small",
        "\\begin{tabular}{@{}l r r@{}}",
        "\\toprule",
        "\\textbf{Pair} & \\textbf{By control} & \\textbf{By resource} \\\\",
        "\\midrule",
    ]
    for pair in sorted(agreement):
        s = agreement[pair]
        a, b = pair.split("|")
        control = f"{s['jaccard']:.3f}" if s["jaccard"] is not None else "--"
        resource = f"{s['resource_jaccard']:.3f}" if s["resource_jaccard"] is not None else "--"
        lines.append(f"{a} vs.\\ {b} & {control} & {resource} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
