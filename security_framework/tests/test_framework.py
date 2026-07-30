import json
import os
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security_framework.engine.comparative_eval import ComparativeEvaluator
from security_framework.engine.engine import BenchmarkEngine, BenchmarkEngineRunner


class TestBenchmarkEngine:
    """Test suite for IaCSecBench BenchmarkEngine."""

    def test_scan_secret_patterns_clean_dir(self):
        """Verifies clean directory returns zero secret violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tf_file = os.path.join(tmpdir, "main.tf")
            with open(tf_file, "w", encoding="utf-8") as f:
                f.write('resource "aws_s3_bucket" "clean" { bucket = "my-bucket" }\n')

            engine = BenchmarkEngine(tmpdir)
            violations = engine.scan_secret_patterns()
            assert len(violations) == 0

    def test_scan_secret_patterns_detects_secret(self):
        """Verifies secret pattern scanning correctly flags hardcoded credentials."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tf_file = os.path.join(tmpdir, "secrets.tf")
            with open(tf_file, "w", encoding="utf-8") as f:
                f.write('aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"\n')

            engine = BenchmarkEngine(tmpdir)
            violations = engine.scan_secret_patterns()
            assert len(violations) == 1
            assert violations[0]["rule"] == "AWS Secret Key"

    def test_runner_full_evaluation(self):
        """Verifies full runner execution telemetry output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = BenchmarkEngineRunner(tmpdir)
            res = runner.run_full_evaluation()
            assert "execution_time_ms" in res
            assert "cis_violations_count" in res
            assert res["status"] == "PASSED"

    def test_evaluate_cis_policies(self):
        """Verifies CIS policy evaluation returns violations for missing required blocks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tf_file = os.path.join(tmpdir, "main.tf")
            with open(tf_file, "w", encoding="utf-8") as f:
                f.write(
                    'resource "aws_db_instance" "example" { storage_encrypted = false publicly_accessible = true }\n'
                )

            engine = BenchmarkEngine(tmpdir)
            violations = engine.evaluate_cis_policies()
            assert any(v["rule"] == "CIS 2.3" for v in violations)


class TestComparativeEvaluator:
    """Test suite for IaCSecBench ComparativeEvaluator."""

    def test_default_benchmarks_load(self):
        """Verifies default benchmark dataset loads properly."""
        evaluator = ComparativeEvaluator()
        assert len(evaluator.benchmarks) >= 10

    def test_run_comparative_suite(self):
        """Verifies evaluation execution across target tools."""
        evaluator = ComparativeEvaluator()
        results = evaluator.run_comparative_suite()
        assert len(results) == 5
        tools = [r.tool_name for r in results]
        assert "IaCSecBench Engine" in tools

    def test_markdown_matrix_generation(self):
        """Verifies markdown table generation output."""
        evaluator = ComparativeEvaluator()
        matrix = evaluator.generate_comparison_matrix_markdown()
        assert "| Tool / Framework | Category |" in matrix
        assert "IaCSecBench Engine" in matrix


class TestBenchmarkDatasetSchema:
    """Test suite for dataset schemas and integrity."""

    def test_benchmarks_json_validity(self):
        """Verifies benchmark dataset JSON file validity."""
        dataset_path = os.path.join(
            os.path.dirname(__file__), "../../benchmark/datasets/benchmarks.json"
        )
        if os.path.exists(dataset_path):
            with open(dataset_path, encoding="utf-8") as f:
                data = json.load(f)
            assert "test_cases" in data
            assert len(data["test_cases"]) > 0
