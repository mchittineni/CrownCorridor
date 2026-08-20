"""Tests for the unlabelled external subset measurement.

Motivated by two real defects found while building it.

The first: the three scanners report a file path in three different dialects for
the same file. On ``main.tf`` at a repository root, Checkov says ``/main.tf``,
tfsec says the full absolute path, and Trivy says ``main.tf``. The module-reach
figure asks whether a finding sits below the root, and reading any of the first
two as a plain relative path answers yes -- so the first run reported that 100% of
Checkov's and tfsec's findings were inside modules, including findings in a
single-directory repository that has no modules at all.

The second: tfsec sometimes appends the offending attribute to the resource
identifier, reporting ``aws_db_instance.rdsdb2.deletion_protection`` where the
others report ``aws_db_instance.rdsdb2``. Compared verbatim, the two never match,
and cross-tool resource agreement is understated for every tfsec pair.

Both defects produce a plausible number rather than an error, which is why they
are pinned here.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from evaluation.external import (
    TOOLS,
    _aggregate,
    in_module,
    repo_relative,
    resource_key,
)

# Derived from the platform temp directory rather than written as a literal
# "/tmp/...", for two reasons. Bandit flags a hardcoded /tmp path (B108), and on
# macOS gettempdir() sits under /var, which is itself a symlink to /private/var --
# so ``resolve()`` diverges from the raw string here, which is precisely the
# condition repo_relative() has to survive. Nothing is created at this path; it is
# only ever compared against.
REPO = Path(tempfile.gettempdir()) / "iacsb-fixture" / "aws-samples_example"


class TestPathDialects:
    """One file, three scanners, three spellings -- all must normalise alike."""

    def test_checkov_leading_slash_is_not_a_module(self):
        assert repo_relative("/main.tf", REPO) == "main.tf"
        assert in_module("/main.tf", REPO) is False

    def test_tfsec_absolute_path_is_not_a_module(self):
        assert repo_relative(str(REPO / "main.tf"), REPO) == "main.tf"
        assert in_module(str(REPO / "main.tf"), REPO) is False

    def test_trivy_relative_path_is_not_a_module(self):
        assert repo_relative("main.tf", REPO) == "main.tf"
        assert in_module("main.tf", REPO) is False

    def test_all_three_dialects_agree(self):
        """The regression itself: the three spellings must not disagree."""
        spellings = ["/main.tf", str(REPO / "main.tf"), "main.tf"]
        assert len({repo_relative(s, REPO) for s in spellings}) == 1
        assert {in_module(s, REPO) for s in spellings} == {False}

    def test_nested_paths_are_modules_in_every_dialect(self):
        for spelling in (
            "modules/vpc/main.tf",
            "/modules/vpc/main.tf",
            str(REPO / "modules/vpc/main.tf"),
        ):
            assert in_module(spelling, REPO) is True, spelling

    def test_empty_path_is_not_a_module(self):
        assert repo_relative("", REPO) == ""
        assert in_module("", REPO) is False

    def test_symlinked_root_still_strips_the_prefix(self, tmp_path):
        """A real symlink, so the divergence is exercised on every platform.

        repo_relative() matches both the raw and the resolved spelling of the root.
        Whether those two differ for REPO depends on the platform -- they do on
        macOS, where the temp directory lives under the /var symlink, and do not on
        a Linux runner with a real /tmp. This builds the symlink itself so the case
        the both-prefixes loop exists for is covered wherever the suite runs.

        tfsec reports the path it walked, which is the symlinked spelling; matching
        only the resolved form would leave the prefix in place and read every root
        finding as nested.
        """
        real = tmp_path / "real-checkout"
        (real / "modules" / "vpc").mkdir(parents=True)
        link = tmp_path / "linked-checkout"
        link.symlink_to(real, target_is_directory=True)
        assert str(link) != str(link.resolve())

        # Root handed to the scanner in its symlinked spelling: findings come back in
        # either spelling, and both must strip.
        assert repo_relative(str(link / "main.tf"), link) == "main.tf"
        assert repo_relative(str(real / "main.tf"), link) == "main.tf"
        assert in_module(str(link / "main.tf"), link) is False
        assert in_module(str(real / "main.tf"), link) is False
        assert in_module(str(link / "modules" / "vpc" / "main.tf"), link) is True

        # The reverse -- root handed over in its real spelling, finding reported
        # through the symlink -- is deliberately NOT asserted. resolve() collapses a
        # symlink towards its target, so a root can be normalised to its real path,
        # but no amount of resolving discovers which symlinks point back at it. That
        # direction cannot occur in practice either: a scanner reports the path it
        # was told to walk, or that path resolved, never a third spelling.
        assert repo_relative(str(real / "main.tf"), real) == "main.tf"


class TestResourceKey:
    def test_tfsec_attribute_suffix_is_trimmed(self):
        assert resource_key("aws_db_instance.rdsdb2.deletion_protection") == (
            "aws_db_instance.rdsdb2"
        )

    def test_plain_identifier_is_unchanged(self):
        assert resource_key("aws_security_group.db2_sg") == "aws_security_group.db2_sg"

    def test_the_regression_two_tools_now_match(self):
        """tfsec's suffixed form and Checkov's plain form must compare equal."""
        assert resource_key("aws_db_instance.rdsdb2.deletion_protection") == resource_key(
            "aws_db_instance.rdsdb2"
        )

    def test_empty_resource_is_empty(self):
        assert resource_key("") == ""


def _repo(name: str, sloc: int, **tools) -> dict:
    return {"repo": name, "commit": "0" * 40, "sloc": sloc, "tools": tools}


def _tool(findings: int, mapped: int, in_mod: int, claims: list, resources: list) -> dict:
    return {
        "status": "ok",
        "findings": findings,
        "mapped": mapped,
        "unmapped": findings - mapped,
        "in_module": in_mod,
        "controls": sorted({c.split("|")[0] for c in claims}),
        "claims": claims,
        "resources": resources,
    }


class TestAggregate:
    def test_identical_tools_agree_perfectly(self):
        claims = ["STO_PUBLIC_BUCKET|aws_s3_bucket.a"]
        resources = ["aws_s3_bucket.a"]
        per_repo = [
            _repo(
                "x/y",
                1000,
                checkov=_tool(1, 1, 0, claims, resources),
                tfsec=_tool(1, 1, 0, claims, resources),
            )
        ]
        agg = _aggregate(per_repo, ("checkov", "tfsec"))
        assert agg["agreement"]["checkov|tfsec"]["jaccard"] == 1.0
        assert agg["agreement"]["checkov|tfsec"]["resource_jaccard"] == 1.0

    def test_same_resource_different_control_splits_the_two_measures(self):
        """The reason both granularities are reported.

        Two scanners flagging one resource under different controls agree about
        where the problem is and disagree about what it is. Control-level Jaccard
        alone would record that as total disagreement.
        """
        per_repo = [
            _repo(
                "x/y",
                1000,
                checkov=_tool(1, 1, 0, ["STO_PUBLIC_BUCKET|aws_s3_bucket.a"], ["aws_s3_bucket.a"]),
                tfsec=_tool(
                    1, 1, 0, ["STO_NO_ACCESS_LOGGING|aws_s3_bucket.a"], ["aws_s3_bucket.a"]
                ),
            )
        ]
        agg = _aggregate(per_repo, ("checkov", "tfsec"))["agreement"]["checkov|tfsec"]
        assert agg["jaccard"] == 0.0
        assert agg["resource_jaccard"] == 1.0

    def test_findings_per_kloc_uses_measured_sloc(self):
        per_repo = [_repo("x/y", 2000, checkov=_tool(10, 5, 2, [], []))]
        s = _aggregate(per_repo, ("checkov",))["per_tool"]["checkov"]
        assert s["findings_per_kloc"] == 5.0
        assert s["unmapped"] == 5
        assert s["unmapped_share"] == 0.5
        assert s["in_module_share"] == 0.2

    def test_failed_scan_is_excluded_not_counted_as_clean(self):
        """A scanner that errored must not contribute a zero-finding denominator."""
        per_repo = [
            _repo("x/y", 1000, checkov=_tool(4, 4, 0, [], [])),
            _repo("x/z", 9000, checkov={"status": "error", "exit_code": 2}),
        ]
        s = _aggregate(per_repo, ("checkov",))["per_tool"]["checkov"]
        assert s["repositories_scanned"] == 1
        assert s["findings"] == 4
        # 4 findings over the 1000 measured lines, not over all 10000.
        assert s["findings_per_kloc"] == 4.0

    def test_no_findings_yields_none_not_a_fabricated_zero(self):
        per_repo = [_repo("x/y", 1000, checkov=_tool(0, 0, 0, [], []))]
        s = _aggregate(per_repo, ("checkov",))["per_tool"]["checkov"]
        assert s["unmapped_share"] is None
        assert s["in_module_share"] is None


class TestRecordedResultsAreUnlabelled:
    """The invariant that keeps this subset out of the accuracy figures."""

    def test_manifest_declares_itself_unlabelled(self):
        doc = json.loads(
            (
                Path(__file__).resolve().parents[2]
                / "benchmark"
                / "external"
                / "aws_samples"
                / "manifest.json"
            ).read_text(encoding="utf-8")
        )
        assert doc["labelled"] is False
        assert doc["scoring"] == "excluded-from-accuracy"
        assert all(len(r["commit"]) == 40 for r in doc["repositories"])
        assert all(r["license"] in ("mit-0", "apache-2.0", "mit") for r in doc["repositories"])

    def test_output_carries_no_accuracy_metric(self):
        """No scored metric may appear as a field: there is no key to score against.

        Checks field names rather than raw text, so that prose explaining *why* the
        subset carries no recall figure does not itself trip the assertion.
        """
        path = Path(__file__).resolve().parents[2] / "results" / "external_subset.json"
        if not path.is_file():
            return  # not yet measured on this checkout
        banned = {"recall", "precision", "f1", "true_positives", "false_negatives", "accuracy"}
        seen: set[str] = set()

        def walk(node: object) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    seen.add(str(key).lower())
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(json.loads(path.read_text(encoding="utf-8")))
        assert not (seen & banned), f"scored metric fields present: {sorted(seen & banned)}"

    def test_opa_is_not_measured_here(self):
        assert "opa" not in TOOLS
