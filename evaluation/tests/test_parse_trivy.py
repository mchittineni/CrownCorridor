"""Regression tests for the Trivy output parser.

Trivy is the only parser whose rule identifier has moved between releases: the AVD
number has appeared under ``ID`` and under ``AVDID``, with and without an ``AVD-``
prefix. That matters more than it sounds. The control map is keyed on the bare form
(``AWS-0086``), so a version that changed the spelling would stop matching every
entry at once -- and a parser that silently yields unmatchable identifiers reports
zero detections rather than raising. Total detection failure and a genuinely clean
corpus are indistinguishable in the aggregate output, so the discrimination has to
be pinned by a test rather than left to inspection.

The recorded-output test reads real output from the measured run, so it fails if a
Trivy upgrade changes the schema in a way the parser does not handle.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evaluation.normalize import PARSERS

ROOT = Path(__file__).resolve().parent.parent.parent
TRIVY_RAW = ROOT / "results" / "raw" / "trivy"

parse_trivy = PARSERS["trivy"]


def test_trivy_is_registered_as_a_parser() -> None:
    assert "trivy" in PARSERS


@pytest.mark.skipif(not TRIVY_RAW.is_dir(), reason="no recorded Trivy output")
def test_recorded_output_yields_findings_with_bare_avd_identifiers() -> None:
    """Real recorded output must parse, and identifiers must carry no ``AVD-`` prefix."""
    total = 0
    for path in sorted(TRIVY_RAW.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        for rule_id, _resource, severity, _desc, _file, line in parse_trivy(
            record.get("payload", record)
        ):
            total += 1
            assert rule_id, f"{path.name}: empty rule identifier"
            assert not rule_id.startswith("AVD-"), (
                f"{path.name}: identifier {rule_id!r} kept its AVD- prefix; the control "
                "map is keyed on the bare form and would match nothing"
            )
            assert severity == severity.upper()
            assert isinstance(line, int)
    assert total > 0, "recorded Trivy output produced no findings at all"


def test_directory_level_group_without_misconfigurations_is_skipped() -> None:
    """Trivy's first result group summarises the directory and has no findings key.

    Indexing rather than iterating would raise on this shape, and defaulting it to an
    empty finding set would be equally wrong for the groups that do carry findings.
    """
    payload = {
        "Results": [
            {"Target": ".", "Class": "config", "MisconfSummary": {"Failures": 0}},
            {
                "Target": "main.tf",
                "Misconfigurations": [
                    {
                        "ID": "AWS-0086",
                        "Status": "FAIL",
                        "Severity": "high",
                        "Title": "t",
                        "CauseMetadata": {"Resource": "aws_s3_bucket.b", "StartLine": 4},
                    }
                ],
            },
        ]
    }
    assert list(parse_trivy(payload)) == [("AWS-0086", "aws_s3_bucket.b", "HIGH", "t", "main.tf", 4)]


def test_passing_checks_are_not_counted_as_findings() -> None:
    """A PASS carries the same rule identifier as a FAIL.

    Trivy can be asked to report passing checks. Emitting one would credit a tool for
    confirming that a control is *satisfied* -- scored identically to detecting its
    violation, which inverts the measurement on compliant cases.
    """
    payload = {
        "Results": [
            {
                "Target": "main.tf",
                "Misconfigurations": [
                    {"ID": "AWS-0086", "Status": "PASS", "CauseMetadata": {}},
                    {"ID": "AWS-0087", "Status": "FAIL", "CauseMetadata": {}},
                ],
            }
        ]
    }
    assert [f[0] for f in parse_trivy(payload)] == ["AWS-0087"]


@pytest.mark.parametrize(
    ("misconfig", "expected"),
    [
        ({"ID": "AWS-0086"}, "AWS-0086"),
        ({"ID": "AVD-AWS-0086"}, "AWS-0086"),
        ({"AVDID": "AVD-AWS-0086", "ID": "ignored"}, "AWS-0086"),
        ({"AVDID": "", "ID": "AWS-0086"}, "AWS-0086"),
    ],
)
def test_identifier_is_normalised_across_field_and_prefix_variants(
    misconfig: dict, expected: str
) -> None:
    """Both fields and both spellings must reduce to the bare AVD number."""
    payload = {
        "Results": [{"Target": "m.tf", "Misconfigurations": [{**misconfig, "CauseMetadata": {}}]}]
    }
    assert [f[0] for f in parse_trivy(payload)] == [expected]


@pytest.mark.parametrize("payload", [None, [], "", 0, {"Results": None}, {"Results": [None]}])
def test_malformed_payloads_yield_nothing_rather_than_raising(payload: object) -> None:
    assert list(parse_trivy(payload)) == []
