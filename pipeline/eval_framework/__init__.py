"""IaC Security & Evaluation Benchmark Framework.

A reusable, modular framework for evaluating Infrastructure as Code (IaC) security,
CIS AWS Benchmark policy enforcement, zero-PII/secret detection, and comparative tool performance.
"""

from .engine import BenchmarkEngine
from .comparative_eval import ComparativeEvaluator, ToolBenchmarkResult

__all__ = ["BenchmarkEngine", "ComparativeEvaluator", "ToolBenchmarkResult"]
