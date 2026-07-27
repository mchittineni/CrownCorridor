"""IaCSecBench — Evaluation Metrics Calculation Engine.

Calculates Accuracy, Precision, Recall, F1 Score, False Positive Rate (FPR),
False Negative Rate (FNR), and Execution Latency metrics across tools.
"""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class EvaluationMetrics:  # pylint: disable=too-many-instance-attributes
    """Holds comprehensive evaluation metrics for a benchmark run."""

    tool_name: str
    category: str
    total_cases: int
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    accuracy_pct: float
    precision_pct: float
    recall_pct: float
    f1_score_pct: float
    fpr_pct: float
    fnr_pct: float
    execution_time_ms: float

    def to_dict(self) -> dict[str, Any]:
        """Converts metrics to dictionary representation."""
        return asdict(self)


def calculate_metrics(
    tool_name: str,
    category: str,
    total_cases: int,
    true_positives: int,
    false_positives: int,
    true_negatives: int,
    false_negatives: int,
    execution_time_ms: float,
) -> EvaluationMetrics:
    """Calculates standard classification and security metrics.

    Args:
        tool_name: Name of the security analysis tool.
        category: Analysis mechanism category (e.g. AST, Rego, Rule Engine).
        total_cases: Total benchmark test cases evaluated.
        true_positives: Correctly identified security violations.
        false_positives: Incorrectly reported violations on secure cases.
        true_negatives: Correctly identified compliant cases.
        false_negatives: Missed security violations.
        execution_time_ms: Total execution time in milliseconds.

    Returns:
        EvaluationMetrics dataclass instance.
    """
    total = max(1, total_cases)

    # Accuracy = (TP + TN) / Total
    accuracy = ((true_positives + true_negatives) / total) * 100.0

    # Precision = TP / (TP + FP)
    denom_prec = true_positives + false_positives
    precision = (true_positives / denom_prec * 100.0) if denom_prec > 0 else 0.0

    # Recall = TP / (TP + FN)
    denom_rec = true_positives + false_negatives
    recall = (true_positives / denom_rec * 100.0) if denom_rec > 0 else 0.0

    # F1 = 2 * (P * R) / (P + R)
    denom_f1 = precision + recall
    f1_score = (2.0 * precision * recall / denom_f1) if denom_f1 > 0 else 0.0

    # FPR = FP / (FP + TN)
    denom_fpr = false_positives + true_negatives
    fpr = (false_positives / denom_fpr * 100.0) if denom_fpr > 0 else 0.0

    # FNR = FN / (TP + FN)
    fnr = (false_negatives / denom_rec * 100.0) if denom_rec > 0 else 0.0

    return EvaluationMetrics(
        tool_name=tool_name,
        category=category,
        total_cases=total,
        true_positives=true_positives,
        false_positives=false_positives,
        true_negatives=true_negatives,
        false_negatives=false_negatives,
        accuracy_pct=round(accuracy, 2),
        precision_pct=round(precision, 2),
        recall_pct=round(recall, 2),
        f1_score_pct=round(f1_score, 2),
        fpr_pct=round(fpr, 2),
        fnr_pct=round(fnr, 2),
        execution_time_ms=round(execution_time_ms, 2),
    )
