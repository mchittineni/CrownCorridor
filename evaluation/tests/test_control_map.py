"""Invariants the control map must satisfy for results to mean anything.

The control map mediates between the native rule identifiers a tool emits and the
canonical controls a benchmark case is authored against. Every defect in it moves
a measurement without looking like it moved anything: a mistyped identifier turns
a detection into a false negative, and an identifier no tool can emit turns an
uncovered control into an apparently covered one.

These tests check the properties that can be checked without running a scanner.
They are deliberately mechanical -- an assertion here is cheaper than re-reading
1,700 lines of JSON after every edit.
"""

# A test function's parameter deliberately shares the name of the fixture that
# supplies it -- that is how pytest resolves fixtures, so pylint's shadowing
# warning is inapplicable to every occurrence in this file.
# pylint: disable=redefined-outer-name

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from evaluation.normalize import PARSERS, ControlMap

ROOT = Path(__file__).resolve().parent.parent.parent
CONTROL_MAP = ROOT / "evaluation" / "control_map.json"
POLICY_DIR = ROOT / "security_framework" / "policies"


@pytest.fixture(scope="module")
def control_map() -> ControlMap:
    return ControlMap.load(CONTROL_MAP)


def implemented_opa_rule_ids() -> set[str]:
    """The ``rule_id`` literals the Rego policy set can actually emit."""
    source = "".join(path.read_text(encoding="utf-8") for path in POLICY_DIR.glob("*.rego"))
    return set(re.findall(r'"rule_id":\s*"([a-z0-9_]+)"', source))


def test_opa_identifiers_are_all_implemented(control_map: ControlMap) -> None:
    """No control may claim an OPA rule the policy set does not define.

    This is the direction of error that flatters the reference implementation:
    a phantom identifier cannot cause a false detection, because nothing emits
    it, but it inflates the count of controls the plan-level layer appears to
    cover. Seven such identifiers were removed from this file once; the test
    exists so they cannot drift back in unnoticed.
    """
    implemented = implemented_opa_rule_ids()
    assert implemented, "no rule_id literals found -- the policy set or this regex changed"

    phantom = {
        control_id: sorted(set(spec.get("tools", {}).get("opa") or []) - implemented)
        for control_id, spec in control_map.controls.items()
    }
    phantom = {cid: rules for cid, rules in phantom.items() if rules}
    assert not phantom, (
        "control map names OPA rules absent from security_framework/policies/*.rego: "
        f"{phantom}. Either implement the rule or drop the mapping -- do not leave a "
        "control looking covered when it is not."
    )


def test_every_tool_key_is_a_known_parser(control_map: ControlMap) -> None:
    """A tool key with no parser silently maps nothing.

    Findings are keyed by tool name, so an entry under a misspelled or removed
    tool is unreachable: the rules never match, and the affected controls score
    as undetected for a tool that was in fact never consulted.
    """
    known = set(PARSERS)
    unknown: dict[str, list[str]] = {}
    for control_id, spec in control_map.controls.items():
        extra = sorted(set(spec.get("tools", {})) - known)
        if extra:
            unknown[control_id] = extra
    assert not unknown, (
        f"control map references tools with no parser in evaluation/normalize.py: {unknown}. "
        f"Known tools: {sorted(known)}"
    )


def test_no_control_is_undetectable_by_every_tool(control_map: ControlMap) -> None:
    """A control no tool can report is not a control, it is a gap in the taxonomy.

    Such an entry scores every case citing it as a false negative for every tool
    at once, which reads as unanimous tool failure rather than as missing
    coverage. If a control genuinely has no detector yet, that belongs in the
    taxonomy documentation, not in the scoring map.
    """
    undetectable = sorted(
        control_id
        for control_id, spec in control_map.controls.items()
        if not any(spec.get("tools", {}).values())
    )
    assert not undetectable, (
        f"controls with no rule identifier for any tool: {undetectable}. "
        "Every case citing one scores as a miss for all tools simultaneously."
    )


def test_rule_identifiers_are_unique_within_a_tool(control_map: ControlMap) -> None:
    """The same identifier listed twice for one tool signals a copy-paste error."""
    duplicated: dict[str, dict[str, list[str]]] = {}
    for control_id, spec in control_map.controls.items():
        for tool, rules in spec.get("tools", {}).items():
            seen = {x for x in rules if rules.count(x) > 1}
            if seen:
                duplicated.setdefault(control_id, {})[tool] = sorted(seen)
    assert not duplicated, f"duplicate rule identifiers: {duplicated}"


def test_identifiers_carry_no_surrounding_whitespace() -> None:
    """Whitespace in an identifier makes it match nothing.

    ``controls_for`` strips before lookup, so a padded identifier still resolves
    at runtime and the defect stays invisible. It is caught here instead, where
    the fix is to correct the file rather than to rely on the reader.
    """
    payload = json.loads(CONTROL_MAP.read_text(encoding="utf-8"))
    padded: dict[str, list[str]] = {}
    for control_id, spec in payload["controls"].items():
        for tool, rules in spec.get("tools", {}).items():
            bad = [r for r in rules if r != r.strip() or not r]
            if bad:
                padded[f"{control_id}/{tool}"] = bad
    assert not padded, f"rule identifiers with stray whitespace or empty entries: {padded}"


def test_cis_citation_agrees_with_the_corpus_generator() -> None:
    """The map and the generator must cite the same control for the same ID.

    Ground truth is derived from the generator's per-control specification, while
    scoring and every human-readable label come from this map. If the two cite
    different CIS controls for one identifier, the corpus is testing one
    requirement and the results are described as another, and nothing in the
    pipeline would notice.

    This is the check that would have caught STO_UNENCRYPTED_BUCKET sooner. Its
    map text stated the CIS 2.1.1 requirement, which SSE-S3 satisfies, while its
    corpus labelled an AES256 bucket as violating -- a stricter,
    customer-managed-key requirement. Titles are deliberately not compared: the
    two files phrase controls neutrally and negatively by convention
    ("Key management rotation" against "Key management key lacks automatic
    rotation"), and 21 of 22 such differences are stylistic.
    """
    generator = (ROOT / "benchmark" / "generate_corpus.py").read_text(encoding="utf-8")
    cited = dict(
        re.findall(
            r'control_id="([A-Z0-9_]+)",\s*\n\s*domain="[^"]*",\s*\n\s*cis_control="([^"]*)"',
            generator,
        )
    )
    assert cited, "no ControlSpec entries parsed -- the generator's shape changed"

    control_map = ControlMap.load(CONTROL_MAP)
    conflicts = {}
    for control_id, generator_cis in cited.items():
        spec = control_map.controls.get(control_id)
        if spec is None:
            continue  # covered by the corpus loader, which rejects unknown controls
        map_cis = str(spec.get("cis_aws", ""))
        if map_cis != str(generator_cis):
            conflicts[control_id] = {"generator": generator_cis, "control_map": map_cis}
    assert not conflicts, (
        "generator and control map cite different CIS controls for the same "
        f"identifier: {conflicts}"
    )


def test_unverified_controls_are_reported_not_hidden(control_map: ControlMap) -> None:
    """The unverified set must stay introspectable.

    Results are qualified by how many entries remain unconfirmed against real
    tool output, so this list feeds a caveat printed alongside every run. A
    refactor that broke it would quietly drop the caveat, not the uncertainty.
    """
    unverified = control_map.unverified_controls
    assert isinstance(unverified, list)
    assert all(cid in control_map.controls for cid in unverified)
    for control_id in unverified:
        assert control_map.controls[control_id].get("verified") is not True
