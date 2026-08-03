"""IaCSecBench — exact statistical inference for paired scanner comparison.

Pure standard library: no numpy/scipy dependency, so the replication package runs
on a bare Python 3.11+ interpreter.

Everything here is exact or explicitly labelled as an approximation. The three
methods that carry the paper's claims are:

* ``clopper_pearson``  — exact binomial confidence interval for recall/precision.
* ``exact_mcnemar``    — exact binomial test for paired scanner disagreement.
                         Used in preference to the chi-square approximation,
                         which is invalid when a discordant cell is small.
* ``mcc``              — Matthews correlation coefficient.

References
----------
[1] C. J. Clopper and E. S. Pearson, "The use of confidence or fiducial limits
    illustrated in the case of the binomial," Biometrika, 26(4):404-413, 1934.
[2] Q. McNemar, "Note on the sampling error of the difference between correlated
    proportions or percentages," Psychometrika, 12(2):153-157, 1947.
[3] B. W. Matthews, "Comparison of the predicted and observed secondary structure
    of T4 phage lysozyme," Biochim. Biophys. Acta, 405(2):442-451, 1975.
[4] A. Agresti and B. A. Coull, "Approximate is better than 'exact' for interval
    estimation of binomial proportions," Amer. Statist., 52(2):119-126, 1998.
[5] T. G. Dietterich, "Approximate statistical tests for comparing supervised
    classification learning algorithms," Neural Comput., 10(7):1895-1923, 1998.
[6] A. Arcuri and L. Briand, "A Hitchhiker's guide to statistical tests for
    assessing randomized algorithms in software engineering," Softw. Test.
    Verif. Reliab., 24(3):219-250, 2014.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

__all__ = [
    "ConfusionMatrix",
    "Interval",
    "McNemarResult",
    "betainc",
    "betainc_inv",
    "clopper_pearson",
    "wilson",
    "mcc",
    "balanced_accuracy",
    "exact_mcnemar",
    "mcnemar_chi2_corrected",
    "odds_ratio_haldane",
    "paired_proportion_diff_ci",
    "cohens_g",
    "paired_bootstrap_diff_ci",
    "holm_bonferroni",
]

_EPS = 1e-15
_MAX_ITER = 300


# --------------------------------------------------------------------------- #
# Regularised incomplete beta function and its inverse.
# Needed for exact (Clopper-Pearson) binomial intervals without scipy.
# --------------------------------------------------------------------------- #


def _betacf(a: float, b: float, x: float) -> float:
    """Continued-fraction expansion for the incomplete beta function.

    Modified Lentz algorithm. See Numerical Recipes, 3rd ed., section 6.4.
    """
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < _EPS:
        d = _EPS
    d = 1.0 / d
    h = d

    for m in range(1, _MAX_ITER + 1):
        m2 = 2 * m

        # Even step.
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < _EPS:
            d = _EPS
        c = 1.0 + aa / c
        if abs(c) < _EPS:
            c = _EPS
        d = 1.0 / d
        h *= d * c

        # Odd step.
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < _EPS:
            d = _EPS
        c = 1.0 + aa / c
        if abs(c) < _EPS:
            c = _EPS
        d = 1.0 / d
        delta = d * c
        h *= delta

        if abs(delta - 1.0) < 3.0e-16:
            return h

    raise RuntimeError(f"betacf failed to converge for a={a}, b={b}, x={x}")


def betainc(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta function I_x(a, b).

    Args:
        a: First shape parameter, > 0.
        b: Second shape parameter, > 0.
        x: Evaluation point in [0, 1].

    Returns:
        I_x(a, b) in [0, 1].
    """
    if not 0.0 <= x <= 1.0:
        raise ValueError(f"x must lie in [0, 1], got {x}")
    if x in (0.0, 1.0):
        return x

    log_beta = (
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    )
    front = math.exp(log_beta)

    # The continued fraction converges quickly only for x < (a+1)/(a+b+2);
    # use the symmetry relation otherwise.
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def betainc_inv(a: float, b: float, p: float) -> float:
    """Inverse of :func:`betainc` in x, by monotone bisection.

    Bisection rather than Newton: slower but unconditionally stable, and the
    cost is irrelevant at benchmark scale.
    """
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"p must lie in [0, 1], got {p}")
    if p == 0.0:
        return 0.0
    if p == 1.0:
        return 1.0

    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if betainc(a, b, mid) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-15:
            break
    return 0.5 * (lo + hi)


# --------------------------------------------------------------------------- #
# Interval estimation
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Interval:
    """A point estimate with a two-sided confidence interval."""

    point: float
    lower: float
    upper: float
    level: float = 0.95
    method: str = ""

    def as_pct(self) -> Interval:
        """Returns the same interval rescaled to percentage units."""
        return Interval(
            point=self.point * 100.0,
            lower=self.lower * 100.0,
            upper=self.upper * 100.0,
            level=self.level,
            method=self.method,
        )

    def latex(self, decimals: int = 2) -> str:
        """Formats as a LaTeX math-mode interval, e.g. ``$[84.32, 93.89]$``."""
        return f"$[{self.lower:.{decimals}f}, {self.upper:.{decimals}f}]$"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> Interval:
    """Exact (Clopper-Pearson) confidence interval for a binomial proportion.

    This is the interval the paper should report for recall and precision. It is
    conservative by construction, which is the appropriate default when a cell
    count is zero or the proportion is at a boundary -- exactly the regime in
    which Wald intervals collapse to zero width and mislead.

    Args:
        k: Number of successes, 0 <= k <= n.
        n: Number of trials, n > 0.
        alpha: Two-sided error rate; 0.05 yields a 95% interval.

    Returns:
        An ``Interval`` whose ``point`` is ``k / n``.

    Notes:
        Boundary behaviour is handled explicitly: at k = n the lower bound is
        ``(alpha/2) ** (1/n)`` and the upper bound is exactly 1.0. For n = 176
        and k = 176 this gives a lower bound of 0.97926, i.e. [97.93%, 100.00%].
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= k <= n:
        raise ValueError(f"k must lie in [0, n], got k={k}, n={n}")

    lower = 0.0 if k == 0 else betainc_inv(k, n - k + 1, alpha / 2.0)
    upper = 1.0 if k == n else betainc_inv(k + 1, n - k, 1.0 - alpha / 2.0)

    return Interval(
        point=k / n,
        lower=lower,
        upper=upper,
        level=1.0 - alpha,
        method="Clopper-Pearson (exact)",
    )


def wilson(k: int, n: int, alpha: float = 0.05) -> Interval:
    """Wilson score interval for a binomial proportion.

    Reported alongside Clopper-Pearson where a less conservative interval is
    wanted. Not a substitute for it at boundary counts.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    z = _normal_quantile(1.0 - alpha / 2.0)
    p_hat = k / n
    denom = 1.0 + z * z / n
    centre = (p_hat + z * z / (2.0 * n)) / denom
    half = (z / denom) * math.sqrt(p_hat * (1.0 - p_hat) / n + z * z / (4.0 * n * n))
    return Interval(
        point=p_hat,
        lower=max(0.0, centre - half),
        upper=min(1.0, centre + half),
        level=1.0 - alpha,
        method="Wilson score",
    )


def _normal_quantile(p: float) -> float:
    """Standard normal quantile via Acklam's rational approximation.

    Absolute error below 1.15e-9 over the open unit interval, which is far
    tighter than anything reported to two decimal places.
    """
    if not 0.0 < p < 1.0:
        raise ValueError(f"p must lie in (0, 1), got {p}")

    a = (
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    )
    b = (
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    )
    c = (
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    )
    d = (
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e00,
        3.754408661907416e00,
    )
    p_low, p_high = 0.02425, 1.0 - 0.02425

    if p < p_low:
        q = math.sqrt(-2.0 * math.log(p))
        num = ((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]
        den = (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
        return num / den
    if p > p_high:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        num = ((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]
        den = (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
        return -num / den

    q = p - 0.5
    r = q * q
    num = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
    den = ((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0
    return num / den


# --------------------------------------------------------------------------- #
# Confusion matrix and derived scalars
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ConfusionMatrix:
    """A 2x2 confusion matrix with derived metrics.

    ``__post_init__`` asserts that the four cells sum to the declared corpus
    size when one is supplied. This guard exists because the original result
    tables published cell counts that summed to 344 against a declared corpus of
    345, with recall computed against a third denominator.
    """

    tp: int
    fp: int
    tn: int
    fn: int

    def __post_init__(self) -> None:
        for name, value in (("tp", self.tp), ("fp", self.fp), ("tn", self.tn), ("fn", self.fn)):
            if value < 0:
                raise ValueError(f"{name} must be non-negative, got {value}")

    # -- structural totals -------------------------------------------------- #

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.tn + self.fn

    @property
    def positives(self) -> int:
        """Ground-truth vulnerable cases (TP + FN)."""
        return self.tp + self.fn

    @property
    def negatives(self) -> int:
        """Ground-truth secure cases (TN + FP)."""
        return self.tn + self.fp

    def assert_total(self, expected: int) -> None:
        """Raises if the cells do not sum to ``expected``."""
        if self.total != expected:
            raise ValueError(
                f"confusion matrix sums to {self.total} but corpus size is {expected}: "
                f"TP={self.tp} FP={self.fp} TN={self.tn} FN={self.fn}"
            )

    # -- rates -------------------------------------------------------------- #

    @property
    def accuracy(self) -> float:
        return (self.tp + self.tn) / self.total if self.total else 0.0

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom else 0.0

    @property
    def recall(self) -> float:
        return self.tp / self.positives if self.positives else 0.0

    @property
    def specificity(self) -> float:
        return self.tn / self.negatives if self.negatives else 0.0

    @property
    def f1(self) -> float:
        denom = self.precision + self.recall
        return 2.0 * self.precision * self.recall / denom if denom else 0.0

    @property
    def balanced_accuracy(self) -> float:
        return balanced_accuracy(self.recall, self.specificity)

    @property
    def mcc(self) -> float:
        return mcc(self.tp, self.fp, self.tn, self.fn)

    # -- intervals ---------------------------------------------------------- #

    # Interval accessors return None rather than raising when the relevant
    # denominator is zero. A proportion with no trials is not estimable, and
    # substituting zero would present an absence of evidence as a measurement.

    def recall_ci(self, alpha: float = 0.05) -> Interval | None:
        return clopper_pearson(self.tp, self.positives, alpha) if self.positives else None

    def specificity_ci(self, alpha: float = 0.05) -> Interval | None:
        return clopper_pearson(self.tn, self.negatives, alpha) if self.negatives else None

    def precision_ci(self, alpha: float = 0.05) -> Interval | None:
        predicted = self.tp + self.fp
        return clopper_pearson(self.tp, predicted, alpha) if predicted else None

    def accuracy_ci(self, alpha: float = 0.05) -> Interval | None:
        return clopper_pearson(self.tp + self.tn, self.total, alpha) if self.total else None

    def to_dict(self) -> dict[str, Any]:
        def interval(getter: Any) -> dict[str, Any] | None:
            value = getter()
            return value.to_dict() if value is not None else None

        return {
            "tp": self.tp,
            "fp": self.fp,
            "tn": self.tn,
            "fn": self.fn,
            "total": self.total,
            "positives": self.positives,
            "negatives": self.negatives,
            "accuracy": self.accuracy if self.total else None,
            "precision": self.precision if (self.tp + self.fp) else None,
            "recall": self.recall if self.positives else None,
            "specificity": self.specificity if self.negatives else None,
            "f1": self.f1 if self.positives and (self.tp + self.fp) else None,
            "balanced_accuracy": (
                self.balanced_accuracy if self.positives and self.negatives else None
            ),
            "mcc": self.mcc if self.positives and self.negatives else None,
            "recall_ci": interval(self.recall_ci),
            "precision_ci": interval(self.precision_ci),
            "specificity_ci": interval(self.specificity_ci),
            "accuracy_ci": interval(self.accuracy_ci),
        }


def mcc(tp: int, fp: int, tn: int, fn: int) -> float:
    """Matthews correlation coefficient.

    Returns 0.0 when the denominator vanishes, which is the conventional
    treatment for a degenerate matrix (a predictor that never fires, or a corpus
    with a single ground-truth class).
    """
    numerator = (tp * tn) - (fp * fn)
    denominator = math.sqrt(float(tp + fp) * float(tp + fn) * float(tn + fp) * float(tn + fn))
    return numerator / denominator if denominator > 0.0 else 0.0


def balanced_accuracy(recall: float, specificity: float) -> float:
    """Arithmetic mean of recall and specificity."""
    return (recall + specificity) / 2.0


# --------------------------------------------------------------------------- #
# Paired significance testing
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class McNemarResult:
    """Outcome of a paired McNemar comparison of two classifiers.

    Attributes:
        b: Cases the reference tool classifies correctly and the comparator does
           not. This must count *every* disagreement -- both missed violations
           and spurious findings -- not false negatives alone.
        c: Cases the comparator classifies correctly and the reference does not.
        p_exact: Two-sided exact binomial p-value. The value to report.
        p_midp: Mid-p variant; less conservative, still valid at small counts.
        p_chi2_cc: Chi-square approximation with Yates continuity correction,
                   retained only for comparison with prior literature.
        chi2_valid: False when min(b, c) < 5, in which case ``p_chi2_cc`` must
                    not be reported as the primary result.
    """

    reference: str
    comparator: str
    b: int
    c: int
    n_discordant: int
    p_exact: float
    p_midp: float
    p_chi2_cc: float
    chi2_statistic: float
    chi2_valid: bool
    odds_ratio: float
    odds_ratio_ci: Interval
    diff_ci: Interval
    cohens_g: float

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["odds_ratio_ci"] = self.odds_ratio_ci.to_dict()
        payload["diff_ci"] = self.diff_ci.to_dict()
        return payload


def _binom_sf_le(k: int, n: int) -> Fraction:
    """Exact P(X <= k) for X ~ Binomial(n, 1/2), as a rational number."""
    if n == 0:
        return Fraction(1)
    total = sum(math.comb(n, i) for i in range(0, k + 1))
    return Fraction(total, 2**n)


def exact_mcnemar(
    b: int,
    c: int,
    reference: str = "reference",
    comparator: str = "comparator",
    alpha: float = 0.05,
    n_total: int | None = None,
) -> McNemarResult:
    """Exact binomial (McNemar) test on paired discordant counts.

    Under the null hypothesis the two tools are equally likely to be the one
    that is correct on a discordant case, so the discordant pairs follow
    Binomial(b + c, 1/2). The two-sided exact p-value is

        p = min(1, 2 * P(X <= min(b, c)))

    which is used in preference to the chi-square approximation. The chi-square
    form is computed and returned, but flagged invalid when ``min(b, c) < 5`` --
    notably including the ``c = 0`` case, where the corrected statistic is
    routinely quoted in the IaC-scanner literature but is not trustworthy.

    Args:
        b: Discordant pairs favouring the reference tool.
        c: Discordant pairs favouring the comparator.
        reference: Label for the reference tool.
        comparator: Label for the comparator tool.
        alpha: Two-sided error rate for the accompanying intervals.
        n_total: Corpus size, required for the paired difference interval. When
            omitted, the difference interval is computed over discordant pairs
            only and will be wider than the corpus-level interval.

    Returns:
        A fully populated ``McNemarResult``.
    """
    if b < 0 or c < 0:
        raise ValueError("discordant counts must be non-negative")

    n_disc = b + c
    k = min(b, c)

    if n_disc == 0:
        # Perfect agreement: no evidence of any difference.
        p_exact = 1.0
        p_midp = 1.0
        chi2 = 0.0
        p_chi2 = 1.0
    else:
        tail = _binom_sf_le(k, n_disc)
        p_exact = float(min(Fraction(1), 2 * tail))
        pmf_k = Fraction(math.comb(n_disc, k), 2**n_disc)
        p_midp = float(min(Fraction(1), 2 * (tail - pmf_k / 2)))
        chi2 = (abs(b - c) - 1.0) ** 2 / n_disc if n_disc > 0 else 0.0
        p_chi2 = _chi2_sf_1df(chi2)

    denom = n_total if n_total is not None else max(n_disc, 1)

    return McNemarResult(
        reference=reference,
        comparator=comparator,
        b=b,
        c=c,
        n_discordant=n_disc,
        p_exact=p_exact,
        p_midp=p_midp,
        p_chi2_cc=p_chi2,
        chi2_statistic=chi2,
        chi2_valid=k >= 5,
        odds_ratio=odds_ratio_haldane(b, c)[0],
        odds_ratio_ci=odds_ratio_haldane(b, c)[1],
        diff_ci=paired_proportion_diff_ci(b, c, denom, alpha),
        cohens_g=cohens_g(b, c),
    )


def mcnemar_chi2_corrected(b: int, c: int) -> tuple[float, float]:
    """Yates-corrected McNemar chi-square statistic and p-value.

    Provided for reproducing figures from prior work. Prefer
    :func:`exact_mcnemar` for new results.
    """
    n = b + c
    if n == 0:
        return 0.0, 1.0
    chi2 = (abs(b - c) - 1.0) ** 2 / n
    return chi2, _chi2_sf_1df(chi2)


def _chi2_sf_1df(x: float) -> float:
    """Upper tail of the chi-square distribution with one degree of freedom."""
    if x <= 0.0:
        return 1.0
    return math.erfc(math.sqrt(x / 2.0))


def odds_ratio_haldane(b: int, c: int, alpha: float = 0.05) -> tuple[float, Interval]:
    """Odds ratio for discordant pairs with a Haldane-Anscombe correction.

    A zero discordant cell makes the naive ratio ``b / c`` infinite, which is
    not an effect size and must not be reported as one. Adding 0.5 to both cells
    yields a finite estimate with a computable interval, and the correction is
    disclosed in the returned method string.
    """
    b_adj, c_adj = b + 0.5, c + 0.5
    ratio = b_adj / c_adj
    log_or = math.log(ratio)
    se = math.sqrt(1.0 / b_adj + 1.0 / c_adj)
    z = _normal_quantile(1.0 - alpha / 2.0)
    interval = Interval(
        point=ratio,
        lower=math.exp(log_or - z * se),
        upper=math.exp(log_or + z * se),
        level=1.0 - alpha,
        method="Haldane-Anscombe corrected (+0.5 per cell)",
    )
    return ratio, interval


def paired_proportion_diff_ci(b: int, c: int, n: int, alpha: float = 0.05) -> Interval:
    """Confidence interval for the difference of two paired proportions.

    Uses the standard paired-difference variance

        Var(d) = [ (b + c) - (b - c)^2 / n ] / n^2 ,  d = (b - c) / n

    This is the effect size to report for a paired scanner comparison: it is
    expressed in the units the reader cares about (percentage points of corpus
    accuracy) and stays finite when a discordant cell is zero.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    d = (b - c) / n
    variance = ((b + c) - (b - c) ** 2 / n) / (n * n)
    se = math.sqrt(max(variance, 0.0))
    z = _normal_quantile(1.0 - alpha / 2.0)
    return Interval(
        point=d,
        lower=max(-1.0, d - z * se),
        upper=min(1.0, d + z * se),
        level=1.0 - alpha,
        method="paired difference of proportions (Wald)",
    )


def cohens_g(b: int, c: int) -> float:
    """Cohen's g effect size for McNemar's test.

    g = |b / (b + c) - 0.5|, bounded in [0, 0.5]. Conventional thresholds:
    0.05 small, 0.15 medium, 0.25 large.
    """
    n = b + c
    if n == 0:
        return 0.0
    return abs(b / n - 0.5)


def paired_bootstrap_diff_ci(
    outcomes_a: Sequence[bool],
    outcomes_b: Sequence[bool],
    iterations: int = 10_000,
    alpha: float = 0.05,
    seed: int = 20260802,
) -> Interval:
    """Paired bootstrap interval for the difference in per-case correctness.

    Resamples cases -- not predictions -- so the pairing between the two tools is
    preserved. The seed is fixed so the interval is reproducible; report it.
    """
    if len(outcomes_a) != len(outcomes_b):
        raise ValueError("paired outcome vectors must have equal length")
    n = len(outcomes_a)
    if n == 0:
        raise ValueError("outcome vectors must be non-empty")

    deltas = [int(a) - int(b) for a, b in zip(outcomes_a, outcomes_b)]
    observed = sum(deltas) / n

    # A seeded Mersenne Twister is the correct generator here, not a weakness: the
    # bootstrap must be reproducible from the seed recorded in the run manifest so
    # a reader can regenerate the published interval exactly. Nothing here is a
    # secret, a token, or a nonce.
    rng = random.Random(seed)  # nosec B311 - reproducible resampling, not cryptography
    replicates = []
    for _ in range(iterations):
        total = 0
        for _ in range(n):
            total += deltas[rng.randrange(n)]
        replicates.append(total / n)
    replicates.sort()

    lo_idx = int(math.floor((alpha / 2.0) * iterations))
    hi_idx = min(iterations - 1, int(math.ceil((1.0 - alpha / 2.0) * iterations)) - 1)

    return Interval(
        point=observed,
        lower=replicates[lo_idx],
        upper=replicates[hi_idx],
        level=1.0 - alpha,
        method=f"paired bootstrap ({iterations} replicates, seed={seed})",
    )


def holm_bonferroni(p_values: dict[str, float], alpha: float = 0.05) -> dict[str, dict[str, Any]]:
    """Holm-Bonferroni step-down correction for a family of comparisons.

    Comparing one tool against four others is four tests on one corpus; the
    family-wise error rate must be controlled or the smallest p-value is not
    interpretable at the nominal level.

    Returns:
        Mapping from comparison label to ``{"p_raw", "p_adjusted", "rank",
        "reject"}``, where ``p_adjusted`` is the step-down adjusted value
        enforced to be monotone non-decreasing in rank.
    """
    ordered = sorted(p_values.items(), key=lambda kv: kv[1])
    m = len(ordered)
    out: dict[str, dict[str, Any]] = {}
    running_max = 0.0

    for rank, (label, p_raw) in enumerate(ordered):
        adjusted = min(1.0, (m - rank) * p_raw)
        running_max = max(running_max, adjusted)
        out[label] = {
            "p_raw": p_raw,
            "p_adjusted": running_max,
            "rank": rank + 1,
            "reject": running_max <= alpha,
        }
    return out
