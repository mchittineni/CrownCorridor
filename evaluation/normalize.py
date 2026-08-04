"""IaCSecBench — finding normalization engine.

Maps heterogeneous scanner output onto a canonical control taxonomy so that
tools with incompatible report schemas can be scored against one ground truth.

Canonical finding
-----------------
    F = <case_id, tool, control_id, resource, severity, rule_id, layer>

Three matching strictness levels are computed for every case, because they
answer different questions and disagree in practice:

``control``
    The tool emitted a finding whose native rule maps, via
    ``control_map.json``, to a control the case was authored to violate. This
    is the primary criterion.
``resource``
    The tool emitted any finding against the resource address named in the
    case's ground truth, regardless of which rule fired. Detects the
    "right resource, wrong reason" case.
``any``
    The tool emitted any finding at all within the case directory. This is the
    weakest criterion and inflates recall; it is reported only to quantify how
    much of a tool's apparent detection rate is attributable to unrelated
    findings.

Reporting all three is deliberate. A single loose criterion is the most common
way scanner benchmarks overstate detection.

Unmapped rule identifiers are counted and surfaced rather than discarded, since
treating an unmapped detection as a miss biases results toward whichever tool
the map was authored around.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTROL_MAP = Path(__file__).resolve().parent / "control_map.json"

MatchLevel = Literal["control", "resource", "any"]
MATCH_LEVELS: tuple[MatchLevel, ...] = ("control", "resource", "any")

__all__ = [
    "Finding",
    "ControlMap",
    "CaseOutcome",
    "normalize_tool_output",
    "score_case",
    "PARSERS",
]


# --------------------------------------------------------------------------- #
# Canonical finding
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Finding:
    """One canonicalised security finding."""

    case_id: str
    tool: str
    rule_id: str
    control_id: str | None
    resource: str
    severity: str
    message: str
    layer: str
    file: str = ""
    line: int = 0
    control_ids: tuple[str, ...] | list[str] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CaseOutcome:
    """Per-case detection outcome for one tool, at all three strictness levels."""

    case_id: str
    tool: str
    expected: Literal["VIOLATION", "COMPLIANT"]
    detected: dict[str, bool] = field(default_factory=dict)
    # Resource-level matching requires the case to declare the resource address
    # its violation lives at. When it does not, the criterion is inapplicable --
    # which is not the same as the tool having failed it.
    resource_matching_applicable: bool = True
    findings: list[Finding] = field(default_factory=list)
    unmapped_rules: list[str] = field(default_factory=list)
    tool_error: str | None = None

    def classification(self, level: MatchLevel = "control") -> str:
        """Returns TP, FP, TN or FN at the requested strictness level."""
        fired = self.detected.get(level, False)
        if self.expected == "VIOLATION":
            return "TP" if fired else "FN"
        return "FP" if fired else "TN"

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "tool": self.tool,
            "expected": self.expected,
            "detected": self.detected,
            "resource_matching_applicable": self.resource_matching_applicable,
            "classification": {lvl: self.classification(lvl) for lvl in MATCH_LEVELS},
            "n_findings": len(self.findings),
            "findings": [f.to_dict() for f in self.findings],
            "unmapped_rules": sorted(set(self.unmapped_rules)),
            "tool_error": self.tool_error,
        }


# --------------------------------------------------------------------------- #
# Control map
# --------------------------------------------------------------------------- #


class ControlMap:
    """Bidirectional index between native tool rules and canonical controls."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self.schema_version: str = payload.get("schema_version", "0")
        self.controls: dict[str, dict[str, Any]] = payload["controls"]

        # A native rule may legitimately cover more than one canonical control:
        # tfsec's aws-iam-no-policy-wildcards fires for both wildcard actions and
        # wildcard trust relationships. The mapping is therefore many-to-many,
        # and a finding is credited when any of its mapped controls is expected.
        self._rule_to_controls: dict[tuple[str, str], set[str]] = defaultdict(set)
        for control_id, spec in self.controls.items():
            for tool, rules in spec.get("tools", {}).items():
                for rule in rules:
                    self._rule_to_controls[(tool, rule.strip())].add(control_id)

    @classmethod
    def load(cls, path: Path | str = DEFAULT_CONTROL_MAP) -> ControlMap:
        with open(path, encoding="utf-8") as handle:
            return cls(json.load(handle))

    def controls_for(self, tool: str, rule_id: str) -> set[str]:
        """Returns every canonical control a native rule maps to (possibly empty)."""
        return self._rule_to_controls.get((tool, rule_id.strip()), set())

    def ambiguous_rules(self) -> dict[str, list[str]]:
        """Native rules covering more than one canonical control.

        Reported rather than rejected: coarse rules are a property of the tools,
        not an error in the map, but they must be visible because they weaken the
        precision of control-level attribution.
        """
        return {
            f"{tool}:{rule}": sorted(controls)
            for (tool, rule), controls in sorted(self._rule_to_controls.items())
            if len(controls) > 1
        }

    @property
    def unverified_controls(self) -> list[str]:
        """Controls whose rule mapping has not been confirmed against tool output."""
        return sorted(cid for cid, spec in self.controls.items() if not spec.get("verified"))

    def coverage(self, tool: str) -> list[str]:
        """Controls for which the given tool has at least one mapped rule."""
        return sorted(cid for cid, spec in self.controls.items() if spec.get("tools", {}).get(tool))


# --------------------------------------------------------------------------- #
# Per-tool parsers
#
# Each parser takes the tool's raw output (already JSON-decoded) plus the case
# identifier, and yields (rule_id, resource, severity, message, file, line)
# tuples. Parsers are intentionally tolerant of schema drift between tool
# versions: an unrecognised payload raises so it is visible, rather than
# returning zero findings and being scored as a clean miss.
# --------------------------------------------------------------------------- #


def _parse_checkov(payload: Any) -> Iterable[tuple[str, str, str, str, str, int]]:
    """Parses ``checkov -o json`` output.

    Checkov emits either a single object or a list of objects (one per detected
    framework) depending on what it finds in the target directory.

    Args:
        payload: Decoded JSON from ``checkov -o json``.

    Yields:
        One ``(rule_id, resource, severity, description, file, line)`` tuple per
        failed check.
    """
    blocks = payload if isinstance(payload, list) else [payload]
    for block in blocks:
        if not isinstance(block, dict):
            continue
        results = block.get("results") or {}
        for check in results.get("failed_checks") or []:
            location = check.get("file_line_range") or [0, 0]
            yield (
                check.get("check_id", ""),
                check.get("resource", ""),
                (check.get("severity") or "UNKNOWN") if check.get("severity") else "UNKNOWN",
                check.get("check_name", ""),
                check.get("file_path", ""),
                int(location[0]) if location else 0,
            )


def _parse_tfsec(payload: Any) -> Iterable[tuple[str, str, str, str, str, int]]:
    """Parses ``tfsec --format json`` output.

    The long identifier is preferred over ``rule_id``: tfsec reports the short
    ``AVD-AWS-NNNN`` form in ``rule_id``, and the control map is keyed on the
    stable long name.

    Args:
        payload: Decoded JSON from ``tfsec --format json``.

    Yields:
        One ``(rule_id, resource, severity, description, file, line)`` tuple per
        result.
    """
    if not isinstance(payload, dict):
        return
    for result in payload.get("results") or []:
        location = result.get("location") or {}
        yield (
            result.get("long_id") or result.get("rule_id", ""),
            result.get("resource", ""),
            (result.get("severity") or "UNKNOWN").upper(),
            result.get("description", ""),
            location.get("filename", ""),
            int(location.get("start_line") or 0),
        )


def _parse_trivy(payload: Any) -> Iterable[tuple[str, str, str, str, str, int]]:
    """Parses ``trivy config --format json`` output.

    Trivy groups misconfigurations by target file, and the first group is a
    directory-level entry that carries a summary but no ``Misconfigurations``
    key, so groups are iterated rather than indexed.

    Only entries whose ``Status`` is ``FAIL`` are emitted. Trivy can be asked to
    report passing checks as well, and a passing check carries the same rule
    identifier as a failing one; counting it as a finding would credit a tool for
    confirming that a control is *satisfied*.

    Rule identifiers are emitted as Trivy reports them (``AWS-0086``). Trivy 0.73
    supplies no ``AVDID`` field, and earlier and later releases have moved this
    identifier between ``ID`` and ``AVDID`` and have prefixed it with ``AVD-``, so
    both fields are consulted and a leading ``AVD-`` is stripped. Without that the
    control map would silently stop matching on a Trivy upgrade, which presents as
    a total detection failure rather than as a parse error.

    Args:
        payload: Decoded JSON from ``trivy config --format json``.

    Yields:
        One ``(rule_id, resource, severity, description, file, line)`` tuple per
        failing misconfiguration.
    """
    if not isinstance(payload, dict):
        return
    for group in payload.get("Results") or []:
        if not isinstance(group, dict):
            continue
        target = group.get("Target", "")
        for misconfig in group.get("Misconfigurations") or []:
            if not isinstance(misconfig, dict):
                continue
            if (misconfig.get("Status") or "FAIL").upper() != "FAIL":
                continue
            rule_id = str(misconfig.get("AVDID") or misconfig.get("ID") or "")
            if rule_id.startswith("AVD-"):
                rule_id = rule_id[len("AVD-") :]
            cause = misconfig.get("CauseMetadata") or {}
            yield (
                rule_id,
                cause.get("Resource", ""),
                (misconfig.get("Severity") or "UNKNOWN").upper(),
                misconfig.get("Title", ""),
                target,
                int(cause.get("StartLine") or 0),
            )


def _parse_opa(payload: Any) -> Iterable[tuple[str, str, str, str, str, int]]:
    """Parses ``opa eval --format json`` output over a Terraform plan.

    Two shapes are accepted: the raw ``{"result": [{"expressions": [...]}]}``
    envelope, and a pre-extracted list of deny messages. Deny messages are
    expected to carry a leading ``[rule_id]`` marker so that findings can be
    mapped to canonical controls; messages without one are reported as
    ``unmapped`` rather than dropped.

    Args:
        payload: Decoded JSON from ``opa eval --format json``, or a pre-extracted
            list of deny messages.

    Yields:
        One ``(rule_id, resource, severity, description, file, line)`` tuple per
        deny message.
    """
    denies: list[Any] = []

    if isinstance(payload, dict) and "result" in payload:
        for result in payload.get("result") or []:
            for expression in result.get("expressions") or []:
                value = expression.get("value")
                if isinstance(value, list):
                    denies.extend(value)
                elif isinstance(value, dict):
                    denies.extend(value.get("deny") or [])
    elif isinstance(payload, list):
        denies = payload

    for entry in denies:
        if isinstance(entry, dict):
            yield (
                entry.get("rule_id", ""),
                entry.get("resource", ""),
                (entry.get("severity") or "UNKNOWN").upper(),
                entry.get("msg", ""),
                entry.get("file", ""),
                int(entry.get("line") or 0),
            )
        else:
            text = str(entry)
            rule_id = ""
            if text.startswith("[") and "]" in text:
                rule_id = text[1 : text.index("]")]
            yield (rule_id, "", "UNKNOWN", text, "", 0)


PARSERS = {
    "checkov": _parse_checkov,
    "tfsec": _parse_tfsec,
    "trivy": _parse_trivy,
    "opa": _parse_opa,
    "iacsecbench": _parse_opa,
    "iacsb_layer1": _parse_opa,
}

TOOL_LAYERS = {
    "checkov": "source",
    "tfsec": "source",
    "trivy": "source",
    "opa": "plan",
    "iacsecbench": "composite",
    "iacsb_layer1": "repository",
}


# --------------------------------------------------------------------------- #
# Normalization and scoring
# --------------------------------------------------------------------------- #


def normalize_tool_output(
    case_id: str,
    tool: str,
    payload: Any,
    control_map: ControlMap,
) -> tuple[list[Finding], list[str]]:
    """Converts raw tool output into canonical findings.

    Returns:
        A ``(findings, unmapped_rule_ids)`` pair. ``unmapped_rule_ids`` lists
        native rules absent from the control map; these still appear in
        ``findings`` with ``control_id = None`` so they remain auditable.
    """
    parser = PARSERS.get(tool)
    if parser is None:
        raise KeyError(f"no parser registered for tool {tool!r}")

    findings: list[Finding] = []
    unmapped: list[str] = []

    for rule_id, resource, severity, message, file_path, line in parser(payload):
        mapped = control_map.controls_for(tool, rule_id) if rule_id else set()
        if not mapped and rule_id:
            unmapped.append(rule_id)
        findings.append(
            Finding(
                case_id=case_id,
                tool=tool,
                rule_id=rule_id,
                control_id=sorted(mapped)[0] if mapped else None,
                control_ids=sorted(mapped),
                resource=resource,
                severity=severity,
                message=message,
                layer=TOOL_LAYERS.get(tool, "unknown"),
                file=file_path,
                line=line,
            )
        )

    return findings, unmapped


def _resource_matches(finding_resource: str, expected_resources: set[str]) -> bool:
    """Loose resource-address comparison.

    Tools disagree on address formatting: Checkov emits ``aws_s3_bucket.data``,
    tfsec emits a file-scoped path, and plan-level output emits fully qualified
    addresses that may include module prefixes and index keys.
    Comparison is therefore performed on the trailing two dot-separated
    components, case-insensitively.
    """
    if not finding_resource:
        return False

    def tail(address: str) -> str:
        parts = [p for p in address.replace('["', ".").replace('"]', "").split(".") if p]
        return ".".join(parts[-2:]).lower() if parts else ""

    finding_tail = tail(finding_resource)
    return any(finding_tail == tail(expected) for expected in expected_resources if expected)


def score_case(
    case_id: str,
    tool: str,
    expected: Literal["VIOLATION", "COMPLIANT"],
    expected_controls: Iterable[str],
    expected_resources: Iterable[str],
    payload: Any,
    control_map: ControlMap,
    tool_error: str | None = None,
) -> CaseOutcome:
    """Scores one benchmark case for one tool at all three strictness levels.

    A tool that crashed on a case is recorded with ``tool_error`` set and is
    scored as not detecting. Execution failures are reported separately in the
    aggregate output so they are never silently folded into the false-negative
    count.
    """
    outcome = CaseOutcome(case_id=case_id, tool=tool, expected=expected, tool_error=tool_error)

    if tool_error is not None:
        outcome.detected = dict.fromkeys(MATCH_LEVELS, False)
        return outcome

    findings, unmapped = normalize_tool_output(case_id, tool, payload, control_map)
    outcome.findings = findings
    outcome.unmapped_rules = unmapped

    wanted_controls = {c for c in expected_controls if c}
    # Only fully qualified addresses ("type.name") can be compared; a bare
    # resource *type* is not an address and must not be treated as one.
    wanted_resources = {r for r in expected_resources if r and "." in r}
    outcome.resource_matching_applicable = bool(wanted_resources)

    outcome.detected = {
        "control": any(set(f.control_ids) & wanted_controls for f in findings),
        "resource": any(_resource_matches(f.resource, wanted_resources) for f in findings),
        "any": bool(findings),
    }
    return outcome


# --------------------------------------------------------------------------- #
# CLI: audit the control map against observed tool output
# --------------------------------------------------------------------------- #


def _emit_unmapped(raw_dir: Path, control_map: ControlMap) -> int:
    """Reports every native rule observed in raw output but absent from the map."""
    observed: dict[str, Counter] = defaultdict(Counter)

    for tool_dir in sorted(p for p in raw_dir.iterdir() if p.is_dir()):
        tool = tool_dir.name
        if tool not in PARSERS:
            continue
        for case_file in sorted(tool_dir.glob("*.json")):
            try:
                payload = json.loads(case_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            _, unmapped = normalize_tool_output(case_file.stem, tool, payload, control_map)
            observed[tool].update(unmapped)

    if not observed:
        print(f"No raw tool output found under {raw_dir}.", file=sys.stderr)
        print("Run experiments/run_baselines.sh first.", file=sys.stderr)
        return 1

    total = 0
    print("Unmapped native rule identifiers observed in raw tool output")
    print("=" * 72)
    for tool, counter in sorted(observed.items()):
        if not counter:
            print(f"\n{tool}: all observed rules are mapped.")
            continue
        print(f"\n{tool}: {len(counter)} distinct unmapped rules")
        for rule, count in counter.most_common():
            print(f"  {count:5d}  {rule}")
            total += count

    print("\n" + "=" * 72)
    print(f"{total} unmapped findings in total.")
    print(
        "Each unmapped finding is a detection the harness cannot credit. Extend\n"
        "evaluation/control_map.json before reporting results, or the comparison\n"
        "understates every tool whose rule identifiers are missing."
    )
    unverified = control_map.unverified_controls
    if unverified:
        print(f"\n{len(unverified)} controls are still flagged verified=false:")
        for control_id in unverified:
            print(f"  {control_id}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="IaCSecBench finding normalization engine")
    parser.add_argument(
        "--control-map",
        type=Path,
        default=DEFAULT_CONTROL_MAP,
        help="path to the canonical control map",
    )
    parser.add_argument(
        "--emit-unmapped",
        action="store_true",
        help="report native rule identifiers absent from the control map",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=ROOT / "results" / "raw",
        help="directory containing per-tool raw output",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="report per-tool control coverage of the map",
    )
    args = parser.parse_args(argv)

    control_map = ControlMap.load(args.control_map)

    if args.coverage:
        print(
            f"Control map schema {control_map.schema_version}: "
            f"{len(control_map.controls)} canonical controls"
        )
        for tool in sorted(PARSERS):
            covered = control_map.coverage(tool)
            print(f"  {tool:<14} {len(covered):>3}/{len(control_map.controls)} controls mapped")

        ambiguous = control_map.ambiguous_rules()
        if ambiguous:
            print(f"\n{len(ambiguous)} native rules span multiple canonical controls.")
            print("These weaken control-level attribution and must be disclosed:")
            for rule, controls in ambiguous.items():
                print(f"  {rule:<44} -> {', '.join(controls)}")

        unverified = control_map.unverified_controls
        if unverified:
            print(
                f"\n{len(unverified)}/{len(control_map.controls)} controls are flagged "
                "verified=false; no result may be reported until these are confirmed "
                "against actual tool output."
            )
        return 0

    if args.emit_unmapped:
        return _emit_unmapped(args.raw_dir, control_map)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
