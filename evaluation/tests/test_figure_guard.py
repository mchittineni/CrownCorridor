"""Tests for the generated-figure staleness gate.

Motivated by a real defect: the measurement workflow re-ran the baselines on a
GitHub-hosted runner and then compared ``paper/figures/*.mmd`` byte-for-byte
against the committed sources. Two of those bytes are per-case latency means, so
the gate failed on every scheduled run -- and the remedy it printed ("regenerate
and commit") would have replaced the published idle-machine latency in the paper's
figures with shared-runner noise, which the same workflow's own summary declares
unpublishable.

The gate therefore distinguishes a figure whose substance drifted (a count, a
version, which tools ran -- anything a table could contradict) from one whose
latency labels merely followed the host.
"""

from __future__ import annotations

from experiments.generate_figures import _without_latency

FIGURE = """flowchart TD
    l1["<b>Layer 1</b>  repository edge"]
    l3["OPA 1.19.0 over plan JSON"]
    l1 -- "pass, 0.15 ms" --> l2
    l2 -- "pass" --> l3
    l3 -- "pass, 12.9 ms" --> ok
    l1 -. "leak or schema failure" .-> no
"""


def test_latency_only_drift_is_not_substantive():
    """The exact CI failure: a re-measurement moves both latency labels."""
    remeasured = FIGURE.replace("0.15 ms", "0.41 ms").replace("12.9 ms", "4711.3 ms")
    assert remeasured != FIGURE
    assert _without_latency(remeasured) == _without_latency(FIGURE)


def test_version_drift_is_substantive():
    """A version string is deterministic given the manifest, so it must still fail."""
    drifted = FIGURE.replace("OPA 1.19.0", "OPA 1.9.0")
    assert _without_latency(drifted) != _without_latency(FIGURE)


def test_unmeasured_latency_is_masked_like_any_other_value():
    """`_fmt_ms(None)` yields prose, not a number; it must mask the same way."""
    unmeasured = FIGURE.replace("12.9 ms", "not measured")
    assert _without_latency(unmeasured) == _without_latency(FIGURE)


def test_masking_leaves_unlabelled_edges_alone():
    """Only the `pass, <value>` labels are blanked -- not every edge label."""
    masked = _without_latency(FIGURE)
    assert '"pass"' in masked
    assert '"leak or schema failure"' in masked
    assert masked.count("<latency>") == 2
