"""Unit tests for the Infrastructure as Code (IaC) validator script."""

from pipeline.validate_iac import (
    check_root_files,
    check_modules_structure,
    check_version_constraints,
    check_hcl_syntax_and_formatting,
    check_cis_aws_benchmark_policies,
    check_terraform_tests_and_policies,
    scan_iac_secrets_and_pii,
    validate_all_iac,
)


def test_check_root_files():
    """Tests that root terraform files are present."""
    ok, errors = check_root_files()
    assert ok, f"Root files check failed with errors: {errors}"
    assert len(errors) == 0


def test_check_modules_structure():
    """Tests that all 10 child modules exist with main, variables, outputs files."""
    ok, errors = check_modules_structure()
    assert ok, f"Modules structure check failed with errors: {errors}"
    assert len(errors) == 0


def test_check_version_constraints():
    """Tests that Terraform >= 1.15.0 and AWS ~> 6.56.0 constraints are present."""
    ok, errors = check_version_constraints()
    assert ok, f"Version constraints check failed: {errors}"
    assert len(errors) == 0


def test_check_hcl_syntax_and_formatting():
    """Tests HCL brace and bracket balance across all .tf files."""
    ok, errors = check_hcl_syntax_and_formatting()
    assert ok, f"HCL syntax check failed: {errors}"
    assert len(errors) == 0


def test_check_cis_aws_benchmark_policies():
    """Tests compliance with highest CIS AWS Foundations Benchmark policies."""
    ok, violations = check_cis_aws_benchmark_policies()
    assert ok, f"CIS AWS Benchmark check failed with violations: {violations}"
    assert len(violations) == 0


def test_check_terraform_tests_and_policies():
    """Tests that native .tftest.hcl test file and Rego policy files exist."""
    ok, errors = check_terraform_tests_and_policies()
    assert ok, f"Terraform tests/policies check failed: {errors}"
    assert len(errors) == 0


def test_scan_iac_secrets_and_pii():
    """Tests that no hardcoded secrets or PII exist in terraform files."""
    ok, violations = scan_iac_secrets_and_pii()
    assert ok, f"Secret scan found violations: {violations}"
    assert len(violations) == 0


def test_validate_all_iac_runner():
    """Tests full IaC validation runner execution."""
    success = validate_all_iac()
    assert success is True
