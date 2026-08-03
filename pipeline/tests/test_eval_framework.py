"""Unit tests for IaC Security & Evaluation Benchmark Framework.

Verifies engine execution, comparative evaluator accuracy calculations, benchmark dataset schemas,
and experiment runner functionality.
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

import pipeline.run_experiments as run_experiments_module
from evaluation.synthetic_guard import GUARD_ENV
from pipeline.run_experiments import run_experiments
from security_framework.engine.comparative_eval import ComparativeEvaluator
from security_framework.engine.engine import BenchmarkEngine, BenchmarkEngineRunner


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
        with open(path, encoding="utf-8") as f:
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

    def test_run_experiments_refuses_without_explicit_opt_in(self, monkeypatch):
        """The synthetic stage must not run just because something imported it.

        ``run_experiments`` derives its comparative numbers from hardcoded per-tool
        profile rates and writes them to ``results/benchmark_results.json`` -- a
        path a reader has every reason to take for measured output. The guard is
        the only thing standing between an editor-triggered ``run_all.sh`` and a
        set of fabricated results overwriting real ones, so its refusal is part of
        the contract and is asserted here rather than merely worked around below.
        """
        monkeypatch.delenv(GUARD_ENV, raising=False)
        with pytest.raises(SystemExit):
            run_experiments()

    def test_run_experiments_success(self, monkeypatch, tmp_path):
        """Executes full experiment pipeline and verifies output structure.

        Opts into synthetic output explicitly, because that is what this stage
        produces. The opt-in belongs in the test rather than in the module.

        Writes are redirected into ``tmp_path``. Without that, running the test
        suite silently replaces ``results/benchmark_results.json`` and
        ``benchmark/reports/experiment_results.json`` with fabricated numbers --
        the exact substitution the synthetic guard exists to prevent, performed by
        the guard's own test.
        """
        monkeypatch.setenv(GUARD_ENV, "1")
        monkeypatch.setattr(
            run_experiments_module, "EXPERIMENT_RESULTS_PATH", str(tmp_path / "experiment.json")
        )
        monkeypatch.setattr(
            run_experiments_module, "BENCHMARK_RESULTS_PATH", str(tmp_path / "benchmark.json")
        )
        out = run_experiments()
        assert "timestamp" in out
        assert "engine_scan" in out
        assert "comparative_benchmarks" in out
        assert len(out["comparative_benchmarks"]) == 5
