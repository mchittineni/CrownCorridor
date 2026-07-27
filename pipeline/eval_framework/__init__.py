"""IaC Security & Evaluation Benchmark Framework.

A reusable, modular framework for evaluating Infrastructure as Code (IaC) security,
CIS AWS Benchmark policy enforcement, zero-PII/secret detection, and comparative tool performance.
"""

from .comparative_eval import ComparativeEvaluator, ToolBenchmarkResult
from .engine import BenchmarkEngine

__all__ = ["BenchmarkEngine", "ComparativeEvaluator", "ToolBenchmarkResult"]
