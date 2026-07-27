"""Unit tests for IaC Security & Evaluation Benchmark Framework.

Verifies engine execution, comparative evaluator accuracy calculations, benchmark dataset schemas,
and experiment runner functionality.
"""

import json
import os
import pathlib
import sys
import pytest

ROOT = pathlib.Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security_framework.engine.engine import BenchmarkEngine, BenchmarkEngineRunner
from security_framework.engine.comparative_eval import ComparativeEvaluator, ToolBenchmarkResult
from pipeline.run_experiments import run_experiments


class TestBenchmarkEngine:
    """Tests for the core BenchmarkEngine."""

    def test_scan_secret_patterns_clean_dir(self, tmp_path):
        """Tests secret scanner on clean Terraform files."""
        tf_file = tmp_path / "main.tf"
        tf_file.write_text('resource "aws_s3_bucket" "b" {\n  bucket = "my-test-bucket"\n}\n')
        engine = BenchmarkEngine(str(tmp_path))
        violations = engine.scan_secret_patterns()
        assert len(violations) == 0

    def test_scan_secret_patterns_detects_secret(self, tmp_path):
        """Tests secret scanner detection on hardcoded credentials."""
        tf_file = tmp_path / "main.tf"
        tf_file.write_text('aws_secret_access_key = "AKIAIOSFODNN7EXAMPLE123"\n')
        engine = BenchmarkEngine(str(tmp_path))
        violations = engine.scan_secret_patterns()
        assert len(violations) == 1
        assert violations[0]["rule"] == "AWS Secret Key"

    def test_runner_full_evaluation(self, tmp_path):
        """Tests BenchmarkEngineRunner evaluation."""
        runner = BenchmarkEngineRunner(str(tmp_path))
        res = runner.run_full_evaluation()
        assert "execution_time_ms" in res
        assert res["status"] == "PASSED"


class TestComparativeEvaluator:
    """Tests for the ComparativeEvaluator module."""

    def test_default_benchmarks_load(self):
        """Verifies loading default benchmark cases."""
        evaluator = ComparativeEvaluator()
        assert len(evaluator.benchmarks) >= 10

    def test_run_comparative_suite(self):
        """Verifies comparative benchmarking calculation across tools."""
        evaluator = ComparativeEvaluator()
        results = evaluator.run_comparative_suite()
        assert len(results) == 5
        tool_names = [r.tool_name for r in results]
        assert "Checkov" in tool_names
        assert "tfsec" in tool_names
        assert "Sentinel / OPA" in tool_names
        assert "Terratest" in tool_names
        assert "IaCSecBench Engine" in tool_names

    def test_markdown_matrix_generation(self):
        """Verifies markdown table output."""
        evaluator = ComparativeEvaluator()
        matrix = evaluator.generate_comparison_matrix_markdown()
        assert "| Tool / Framework | Category |" in matrix
        assert "Checkov" in matrix


class TestBenchmarkDatasetSchema:
    """Tests integrity of public benchmarks.json dataset."""

    def test_benchmarks_json_validity(self):
        """Validates benchmarks.json format and test case keys."""
        path = ROOT / "benchmark" / "datasets" / "benchmarks.json"
        if not path.exists():
            path = ROOT / "data" / "benchmarks" / "benchmarks.json"
        assert path.exists()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "version" in data
        assert "test_cases" in data
        assert len(data["test_cases"]) >= 10
        for tc in data["test_cases"]:
            assert "id" in tc
            assert "module" in tc
            assert "category" in tc
            assert "has_violation" in tc


class TestRunExperiments:
    """Tests execution of the experiment runner."""

    def test_run_experiments_success(self):
        """Executes full experiment pipeline and verifies output structure."""
        out = run_experiments()
        assert "timestamp" in out
        assert "engine_scan" in out
        assert "comparative_benchmarks" in out
        assert len(out["comparative_benchmarks"]) == 5
