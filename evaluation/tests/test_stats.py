"""Verification tests for :mod:`evaluation.stats`.

These tests pin the statistical core against values derived independently of the
implementation -- closed-form boundary results, textbook worked examples, and
values cross-checked against R's ``binom.test``/``mcnemar.test`` and
``scipy.stats``. They exist so that no number reaching the manuscript depends on
an unverified code path.
"""

from __future__ import annotations

import math

import pytest

from evaluation.stats import (
    ConfusionMatrix,
    betainc,
    betainc_inv,
    clopper_pearson,
    cohens_g,
    exact_mcnemar,
    holm_bonferroni,
    mcc,
    mcnemar_chi2_corrected,
    odds_ratio_haldane,
    paired_bootstrap_diff_ci,
    paired_proportion_diff_ci,
    wilson,
)

REL = 1e-9


# --------------------------------------------------------------------------- #
# Incomplete beta
# --------------------------------------------------------------------------- #


def test_betainc_boundaries():
    assert betainc(2.0, 3.0, 0.0) == 0.0
    assert betainc(2.0, 3.0, 1.0) == 1.0


def test_betainc_symmetry():
    """I_x(a, b) == 1 - I_{1-x}(b, a)."""
    for a, b, x in [(2.0, 5.0, 0.3), (0.5, 0.5, 0.7), (10.0, 1.0, 0.9)]:
        assert betainc(a, b, x) == pytest.approx(1.0 - betainc(b, a, 1.0 - x), rel=1e-12)


def test_betainc_closed_form_a1():
    """I_x(1, b) == 1 - (1 - x)^b."""
    x, b = 0.25, 4.0
    assert betainc(1.0, b, x) == pytest.approx(1.0 - (1.0 - x) ** b, rel=1e-12)


def test_betainc_inv_roundtrip():
    for a, b in [(3.0, 7.0), (0.5, 0.5), (12.0, 40.0)]:
        for p in (0.01, 0.25, 0.5, 0.975, 0.99):
            x = betainc_inv(a, b, p)
            assert betainc(a, b, x) == pytest.approx(p, abs=1e-10)


# --------------------------------------------------------------------------- #
# Clopper-Pearson
# --------------------------------------------------------------------------- #


def test_clopper_pearson_all_successes_closed_form():
    """At k = n the exact lower bound is (alpha/2)^(1/n) in closed form.

    This is the interval quoted in the manuscript abstract for 176/176 detections.
    """
    n = 176
    ci = clopper_pearson(n, n)
    expected_lower = 0.025 ** (1.0 / n)
    assert ci.lower == pytest.approx(expected_lower, rel=1e-10)
    assert ci.upper == 1.0
    # The published figure, to two decimal places.
    assert round(ci.lower * 100.0, 2) == 97.93


def test_clopper_pearson_zero_successes_closed_form():
    """At k = 0 the exact upper bound is 1 - (alpha/2)^(1/n)."""
    n = 169
    ci = clopper_pearson(0, n)
    assert ci.lower == 0.0
    assert ci.upper == pytest.approx(1.0 - 0.025 ** (1.0 / n), rel=1e-10)


def test_clopper_pearson_known_value():
    """Cross-check against R: binom.test(8, 20)$conf.int -> 0.1911, 0.6395."""
    ci = clopper_pearson(8, 20)
    assert ci.lower == pytest.approx(0.191190, abs=1e-6)
    assert ci.upper == pytest.approx(0.639457, abs=1e-6)


def test_clopper_pearson_satisfies_its_defining_equations():
    """The bounds are defined by P(X >= k | lower) = P(X <= k | upper) = alpha/2.

    Checking the definition directly validates the interval independently of the
    incomplete-beta inversion used to compute it.
    """

    def binom_ge(k: int, n: int, p: float) -> float:
        return sum(math.comb(n, i) * p**i * (1.0 - p) ** (n - i) for i in range(k, n + 1))

    def binom_le(k: int, n: int, p: float) -> float:
        return sum(math.comb(n, i) * p**i * (1.0 - p) ** (n - i) for i in range(0, k + 1))

    for k, n in [(8, 20), (158, 176), (45, 50), (1, 30)]:
        ci = clopper_pearson(k, n)
        assert binom_ge(k, n, ci.lower) == pytest.approx(0.025, abs=1e-9)
        assert binom_le(k, n, ci.upper) == pytest.approx(0.025, abs=1e-9)


def test_clopper_pearson_contains_point_and_is_conservative():
    ci = clopper_pearson(158, 176)
    assert ci.lower < ci.point < ci.upper
    w = wilson(158, 176)
    # Exact interval is never narrower than the Wilson score interval.
    assert (ci.upper - ci.lower) >= (w.upper - w.lower) - 1e-12


def test_clopper_pearson_rejects_bad_input():
    with pytest.raises(ValueError, match="n must be positive"):
        clopper_pearson(5, 0)
    with pytest.raises(ValueError, match=r"k must lie in \[0, n\]"):
        clopper_pearson(11, 10)


# --------------------------------------------------------------------------- #
# MCC and confusion matrix
# --------------------------------------------------------------------------- #


def test_mcc_perfect_and_inverted():
    assert mcc(10, 0, 10, 0) == pytest.approx(1.0, rel=REL)
    assert mcc(0, 10, 0, 10) == pytest.approx(-1.0, rel=REL)


def test_mcc_degenerate_returns_zero():
    """A predictor that never fires has a vanishing denominator."""
    assert mcc(0, 0, 50, 50) == 0.0


def test_mcc_checkov_row_recomputed():
    """The published Checkov MCC of 0.820 does not follow from its own cells.

    With TP=158, FP=13, TN=156, FN=17 the coefficient is 0.826.
    """
    value = mcc(tp=158, fp=13, tn=156, fn=17)
    assert value == pytest.approx(0.8258, abs=5e-4)
    assert round(value, 3) != 0.820


def test_confusion_matrix_derived_metrics():
    cm = ConfusionMatrix(tp=154, fp=10, tn=159, fn=21)
    assert cm.total == 344
    assert cm.positives == 175
    assert cm.negatives == 169
    assert cm.recall == pytest.approx(154 / 175, rel=REL)
    assert cm.specificity == pytest.approx(159 / 169, rel=REL)
    assert cm.precision == pytest.approx(154 / 164, rel=REL)
    assert cm.balanced_accuracy == pytest.approx((154 / 175 + 159 / 169) / 2, rel=REL)


def test_confusion_matrix_total_guard_catches_off_by_one():
    """The guard that would have caught the published 344-vs-345 discrepancy."""
    cm = ConfusionMatrix(tp=158, fp=13, tn=156, fn=17)
    assert cm.total == 344
    with pytest.raises(ValueError, match="sums to 344 but corpus size is 345"):
        cm.assert_total(345)


def test_confusion_matrix_recall_denominator_is_internal():
    """Recall must use TP + FN, never an externally declared positive count.

    The published table divided 158 by 176 while its own cells implied 175.
    """
    cm = ConfusionMatrix(tp=158, fp=13, tn=156, fn=17)
    assert cm.recall == pytest.approx(158 / 175, rel=REL)
    assert cm.recall != pytest.approx(158 / 176, rel=1e-4)


def test_confusion_matrix_rejects_negative_cells():
    with pytest.raises(ValueError, match="tp must be non-negative"):
        ConfusionMatrix(tp=-1, fp=0, tn=0, fn=0)


# --------------------------------------------------------------------------- #
# McNemar
# --------------------------------------------------------------------------- #


def test_exact_mcnemar_zero_cell_is_a_power_of_two():
    """With c = 0 the two-sided exact p-value is 2 * 2^-b."""
    for b in (5, 10, 22, 30):
        res = exact_mcnemar(b, 0, n_total=345)
        assert res.p_exact == pytest.approx(2.0 * 0.5**b, rel=1e-12)


def test_exact_mcnemar_flags_chi2_as_invalid_at_zero_cell():
    """The chi-square approximation must be marked unusable when min(b, c) < 5."""
    res = exact_mcnemar(30, 0, n_total=345)
    assert res.chi2_valid is False
    res_ok = exact_mcnemar(20, 8, n_total=345)
    assert res_ok.chi2_valid is True


def test_yates_statistic_matches_published_arithmetic():
    """(|17 - 0| - 1)^2 / 17 = 15.06, reproducing the published value.

    The arithmetic is right; the input is not -- see the next test.
    """
    chi2, _ = mcnemar_chi2_corrected(17, 0)
    assert chi2 == pytest.approx(256 / 17, rel=1e-9)
    assert round(chi2, 2) == 15.06


def test_discordant_count_must_include_both_error_types():
    """b counts every disagreement, not false negatives alone.

    Checkov contributes 17 missed violations *and* 13 spurious findings against a
    reference with neither, so b = 30, not 17.
    """
    b_wrong = 17
    b_right = 17 + 13
    assert exact_mcnemar(b_right, 0).p_exact < exact_mcnemar(b_wrong, 0).p_exact


def test_exact_mcnemar_symmetric_case_is_not_significant():
    res = exact_mcnemar(12, 12, n_total=345)
    assert res.p_exact == pytest.approx(1.0, rel=1e-12)
    assert res.cohens_g == 0.0


def test_exact_mcnemar_no_discordance():
    res = exact_mcnemar(0, 0, n_total=345)
    assert res.p_exact == 1.0
    assert res.n_discordant == 0


def test_exact_mcnemar_known_textbook_value():
    """b=12, c=5 -> exact two-sided p = 2 * 9402 / 2^17 = 0.1434631."""
    res = exact_mcnemar(12, 5, n_total=100)
    expected = 2.0 * sum(math.comb(17, i) for i in range(6)) / 2**17
    assert res.p_exact == pytest.approx(expected, rel=1e-12)
    assert res.p_exact == pytest.approx(0.1434631, abs=1e-7)


def test_midp_is_between_exact_and_chi2_direction():
    res = exact_mcnemar(12, 5, n_total=100)
    assert res.p_midp < res.p_exact


def test_odds_ratio_is_finite_at_zero_cell():
    """An infinite odds ratio is not an effect size; the correction bounds it."""
    ratio, interval = odds_ratio_haldane(30, 0)
    assert math.isfinite(ratio)
    assert ratio == pytest.approx(30.5 / 0.5, rel=REL)
    assert math.isfinite(interval.lower) and math.isfinite(interval.upper)
    assert interval.lower > 1.0


def test_cohens_g_bounds():
    assert cohens_g(30, 0) == pytest.approx(0.5, rel=REL)
    assert cohens_g(10, 10) == 0.0
    assert 0.0 <= cohens_g(18, 7) <= 0.5


def test_paired_proportion_diff_ci_finite_and_signed():
    ci = paired_proportion_diff_ci(30, 0, 345)
    assert ci.point == pytest.approx(30 / 345, rel=REL)
    assert ci.lower > 0.0
    assert ci.upper < 1.0


# --------------------------------------------------------------------------- #
# Bootstrap and multiplicity
# --------------------------------------------------------------------------- #


def test_paired_bootstrap_is_deterministic_under_seed():
    a = [True] * 90 + [False] * 10
    b = [True] * 70 + [False] * 30
    first = paired_bootstrap_diff_ci(a, b, iterations=2000)
    second = paired_bootstrap_diff_ci(a, b, iterations=2000)
    assert first.lower == second.lower and first.upper == second.upper


def test_paired_bootstrap_brackets_observed_difference():
    a = [True] * 90 + [False] * 10
    b = [True] * 70 + [False] * 30
    ci = paired_bootstrap_diff_ci(a, b, iterations=4000)
    assert ci.lower <= ci.point <= ci.upper
    assert ci.point == pytest.approx(0.20, abs=1e-12)


def test_paired_bootstrap_rejects_unequal_lengths():
    with pytest.raises(ValueError, match="must have equal length"):
        paired_bootstrap_diff_ci([True, False], [True])


def test_holm_bonferroni_is_monotone_and_conservative():
    raw = {
        "checkov": 0.0001,
        "tfsec": 0.004,
        "iacsb_layer1": 0.02,
        "iacsecbench": 0.030,
    }
    adj = holm_bonferroni(raw)
    ordered = sorted(adj.items(), key=lambda kv: kv[1]["rank"])
    values = [entry["p_adjusted"] for _, entry in ordered]
    assert values == sorted(values), "adjusted p-values must be non-decreasing"
    for label, entry in adj.items():
        assert entry["p_adjusted"] >= entry["p_raw"] - 1e-15, label

    # iacsb_layer1: (4-2) * 0.02 = 0.04, still significant.
    assert adj["iacsb_layer1"]["p_adjusted"] == pytest.approx(0.04, rel=1e-12)
    assert adj["iacsb_layer1"]["reject"] is True
    # iacsecbench: raw 0.030 survives its own step but is dragged to 0.04 by
    # monotonicity.
    assert adj["iacsecbench"]["p_adjusted"] == pytest.approx(0.04, rel=1e-12)


def test_holm_bonferroni_rejects_marginal_comparison():
    """A comparison that is nominally significant can fail after correction."""
    adj = holm_bonferroni({"a": 0.0001, "b": 0.004, "c": 0.02, "d": 0.045})
    assert adj["d"]["p_raw"] < 0.05
    assert adj["d"]["p_adjusted"] == pytest.approx(0.045, rel=1e-12)
    adj_five = holm_bonferroni({"a": 0.04, "b": 0.5, "c": 0.6, "d": 0.7, "e": 0.8})
    assert adj_five["a"]["p_adjusted"] == pytest.approx(0.20, rel=1e-12)
    assert adj_five["a"]["reject"] is False


def test_holm_bonferroni_single_test_is_identity():
    adj = holm_bonferroni({"only": 0.03})
    assert adj["only"]["p_adjusted"] == pytest.approx(0.03, rel=REL)
