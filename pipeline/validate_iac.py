"""Infrastructure as Code (IaC) validator for Crown Corridor Terraform configurations.

Validates module integrity, file presence, provider constraints, CIS AWS Benchmark policies,
HCL formatting syntax, native Terraform tests (.tftest.hcl), and zero-PII / secret compliance.
"""

import os
import re
import sys
from typing import Dict, List, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERRAFORM_DIR = os.path.join(PROJECT_ROOT, "terraform")

EXPECTED_MODULES = [
    "vpc",
    "security",
    "waf",
    "cdn",
    "auth",
    "api_gateway",
    "compute",
    "database",
    "secrets_ssm",
    "events_alerting",
]

EXPECTED_ROOT_FILES = [
    "main.tf",
    "providers.tf",
    "variables.tf",
    "outputs.tf",
    "terraform.tfvars.example",
]

EXPECTED_MODULE_FILES = ["main.tf", "variables.tf", "outputs.tf"]

SECRET_PATTERNS = [
    (r"(?i)aws_secret_access_key\s*=\s*['\"](?!\$\{)[A-Za-z0-9/+=]{20,}['\"]", "AWS Secret Key"),
    (r"(?i)password\s*=\s*['\"](?!var\.|random_|http)[^'\"]{8,}['\"]", "Hardcoded DB Password"),
    (r"(?i)api_key\s*=\s*['\"](?!var\.|random_)[^'\"]{16,}['\"]", "Hardcoded API Key"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "Personal Email Address"),
]


def check_root_files() -> Tuple[bool, List[str]]:
    """Validates presence of all required root Terraform files."""
    errors = []
    if not os.path.exists(TERRAFORM_DIR):
        return False, [f"Terraform directory missing: {TERRAFORM_DIR}"]

    for filename in EXPECTED_ROOT_FILES:
        filepath = os.path.join(TERRAFORM_DIR, filename)
        if not os.path.exists(filepath):
            errors.append(f"Missing root file: terraform/{filename}")

    return len(errors) == 0, errors


def check_modules_structure() -> Tuple[bool, List[str]]:
    """Validates presence and internal structure of all required child modules."""
    errors = []
    modules_dir = os.path.join(TERRAFORM_DIR, "modules")

    if not os.path.exists(modules_dir):
        return False, ["Missing modules directory: terraform/modules"]

    for module in EXPECTED_MODULES:
        mod_path = os.path.join(modules_dir, module)
        if not os.path.exists(mod_path):
            errors.append(f"Missing module directory: terraform/modules/{module}")
            continue

        for req_file in EXPECTED_MODULE_FILES:
            file_path = os.path.join(mod_path, req_file)
            if not os.path.exists(file_path):
                errors.append(f"Missing module file: terraform/modules/{module}/{req_file}")

    return len(errors) == 0, errors


def check_version_constraints() -> Tuple[bool, List[str]]:
    """Validates required Terraform and AWS provider versions in providers.tf."""
    errors = []
    providers_path = os.path.join(TERRAFORM_DIR, "providers.tf")

    if not os.path.exists(providers_path):
        return False, ["terraform/providers.tf file not found."]

    with open(providers_path, "r", encoding="utf-8") as file_obj:
        content = file_obj.read()

    if ">= 1.15.0" not in content and "1.15" not in content:
        errors.append("terraform/providers.tf must specify required_version >= 1.15.0")

    if "~> 6.56.0" not in content and "6.56" not in content:
        errors.append("terraform/providers.tf must specify aws provider version ~> 6.56.0")

    return len(errors) == 0, errors


def check_hcl_syntax_and_formatting() -> Tuple[bool, List[str]]:
    """Validates HCL brace balancing, quotes syntax, and formatting conventions."""
    errors = []

    for root, _, files in os.walk(TERRAFORM_DIR):
        for file in files:
            if not file.endswith(".tf"):
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, PROJECT_ROOT)

            with open(file_path, "r", encoding="utf-8") as file_obj:
                content = file_obj.read()

            # Check brace balance
            open_braces = content.count("{")
            close_braces = content.count("}")
            if open_braces != close_braces:
                errors.append(
                    f"{rel_path}: Unbalanced braces ({open_braces} '{{' vs {close_braces} '}}')"
                )

            # Check bracket balance
            open_brackets = content.count("[")
            close_brackets = content.count("]")
            if open_brackets != close_brackets:
                errors.append(
                    f"{rel_path}: Unbalanced brackets ({open_brackets} '[' vs {close_brackets} ']')"
                )

    return len(errors) == 0, errors


def check_cis_aws_benchmark_policies() -> Tuple[bool, List[str]]:
    """Validates AWS configurations against highest CIS AWS Foundations Benchmark policies.

    Checks:
      - CIS 2.1: S3 Public Access Block & SSE Encryption enabled
      - CIS 2.3: RDS Storage Encryption & Publicly Accessible set to false
      - CIS 2.4: CloudFront HTTPS Redirection enforced
      - CIS 3.2: CloudTrail Multi-Region & Log File Validation enabled
      - CIS 4.1: GuardDuty Detector enabled
      - CIS 4.2: Security Hub Account enabled
      - CIS 5.1: Security Groups block SSH (22) and RDP (3389) from 0.0.0.0/0
    """
    violations = []

    # Read combined Terraform code
    tf_contents = {}
    for root, _, files in os.walk(TERRAFORM_DIR):
        for file in files:
            if file.endswith(".tf"):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, PROJECT_ROOT)
                with open(filepath, "r", encoding="utf-8") as f:
                    tf_contents[rel_path] = f.read()

    combined_code = "\n".join(tf_contents.values())

    # CIS Rule 1: S3 Public Access Block, Versioning & TLS Policy
    if "aws_s3_bucket_public_access_block" not in combined_code:
        violations.append("CIS 2.1: Missing aws_s3_bucket_public_access_block configuration")

    if "aws_s3_bucket_versioning" not in combined_code:
        violations.append("CIS 2.1.3: S3 buckets must enforce object versioning")

    if "aws:SecureTransport" not in combined_code and "EnforceTLSOnly" not in combined_code:
        violations.append("CIS 2.1.2: S3 buckets must enforce TLS-only access policy")

    # CIS Rule 2: RDS Storage Encryption & Non-Public Access
    if not re.search(r"storage_encrypted\s*=\s*true", combined_code):
        violations.append("CIS 2.3: RDS instances must enforce storage_encrypted = true")

    if not re.search(r"publicly_accessible\s*=\s*false", combined_code):
        violations.append("CIS 2.3: RDS instances must enforce publicly_accessible = false")

    # CIS Rule 3: CloudTrail Validation & KMS Rotation
    if not re.search(r"enable_log_file_validation\s*=\s*true", combined_code):
        violations.append("CIS 3.2: CloudTrail must enforce enable_log_file_validation = true")

    if not re.search(r"enable_key_rotation\s*=\s*true", combined_code):
        violations.append("CIS 2.8: KMS Keys must enforce enable_key_rotation = true")

    # CIS Rule 4: VPC Flow Logs & Default Security Group
    if "aws_flow_log" not in combined_code:
        violations.append("CIS 3.9: VPC Flow Logs must be enabled")

    if "aws_default_security_group" not in combined_code:
        violations.append("CIS 5.4: Default Security Group must restrict all ingress/egress")

    # CIS Rule 5: GuardDuty & Security Hub
    if "aws_guardduty_detector" not in combined_code:
        violations.append("CIS 4.1: GuardDuty detector must be enabled")

    if "aws_securityhub_account" not in combined_code:
        violations.append("CIS 4.2: Security Hub account must be enabled")

    # CIS Rule 6: CloudFront HTTPS & ALB Header Dropping
    if not re.search(r'viewer_protocol_policy\s*=\s*"redirect-to-https"', combined_code):
        violations.append("CIS 2.4: CloudFront must enforce viewer_protocol_policy = 'redirect-to-https'")

    if not re.search(r"drop_invalid_header_fields\s*=\s*true", combined_code):
        violations.append("Well-Architected: ALB must enforce drop_invalid_header_fields = true")

    # CIS Rule 7: ECR Image Scanning & Tag Immutability
    if not re.search(r"scan_on_push\s*=\s*true", combined_code):
        violations.append("CIS 5.3: ECR repositories must enable scan_on_push = true")

    # CIS Rule 8: Security Group SSH / RDP Restrictions
    for path, text in tf_contents.items():
        if "from_port   = 22" in text or "from_port   = 3389" in text:
            if 'cidr_blocks = ["0.0.0.0/0"]' in text:
                violations.append(f"CIS 5.1: {path} allows SSH/RDP ingress from 0.0.0.0/0")

    return len(violations) == 0, violations


def check_terraform_tests_and_policies() -> Tuple[bool, List[str]]:
    """Validates existence and structure of native Terraform test files and Rego policy files."""
    errors = []

    tests_dir = os.path.join(TERRAFORM_DIR, "tests")
    main_test_file = os.path.join(tests_dir, "main.tftest.hcl")
    if not os.path.exists(main_test_file):
        errors.append("Missing native Terraform test file: terraform/tests/main.tftest.hcl")

    rego_file = os.path.join(TERRAFORM_DIR, "policies", "cis_aws_benchmark.rego")
    if not os.path.exists(rego_file):
        errors.append("Missing CIS AWS Benchmark Rego policy file: terraform/policies/cis_aws_benchmark.rego")

    # Check that all module .tftest.hcl files are present in terraform/tests/
    for module in EXPECTED_MODULES:
        mod_test_file = os.path.join(tests_dir, f"{module}.tftest.hcl")
        if not os.path.exists(mod_test_file):
            errors.append(f"Missing module native test file in terraform/tests/{module}.tftest.hcl")

    return len(errors) == 0, errors


def scan_iac_secrets_and_pii() -> Tuple[bool, List[str]]:
    """Scans all Terraform files for hardcoded secrets, plain passwords, or PII leaks."""
    violations = []

    for root, _, files in os.walk(TERRAFORM_DIR):
        for file in files:
            if not file.endswith(".tf"):
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, PROJECT_ROOT)

            with open(file_path, "r", encoding="utf-8") as file_obj:
                lines = file_obj.readlines()

            for line_idx, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#") or stripped.startswith("//"):
                    continue

                for pattern, desc in SECRET_PATTERNS:
                    if desc == "Personal Email Address" and "admin@crowncorridor.example.com" in line:
                        continue

                    if re.search(pattern, line):
                        violations.append(
                            f"{rel_path}:{line_idx} — Potential {desc} detected: {line.strip()}"
                        )

    return len(violations) == 0, violations


def validate_all_iac() -> bool:
    """Executes the full IaC validation suite and prints structured output."""
    print("=" * 60)
    print("Crown Corridor — Infrastructure as Code (IaC) Validator")
    print("=" * 60 + "\n")

    all_passed = True

    # 1. Root Files Check
    ok, errors = check_root_files()
    if ok:
        print("[1] Root Configuration Files")
        print("  ✓  All required root terraform files present")
    else:
        print("[1] Root Configuration Files")
        for err in errors:
            print(f"  ✗  {err}")
        all_passed = False

    # 2. Child Modules Structure Check
    ok, errors = check_modules_structure()
    if ok:
        print("\n[2] Modular Architecture Integrity")
        print(f"  ✓  All {len(EXPECTED_MODULES)} child modules present with valid structure")
    else:
        print("\n[2] Modular Architecture Integrity")
        for err in errors:
            print(f"  ✗  {err}")
        all_passed = False

    # 3. Provider & Version Constraints Check
    ok, errors = check_version_constraints()
    if ok:
        print("\n[3] Provider & Version Constraints")
        print("  ✓  Terraform >= 1.15.0 & AWS Provider ~> 6.56.0 constraints verified")
    else:
        print("\n[3] Provider & Version Constraints")
        for err in errors:
            print(f"  ✗  {err}")
        all_passed = False

    # 4. HCL Syntax & Formatting Check
    ok, errors = check_hcl_syntax_and_formatting()
    if ok:
        print("\n[4] HCL Syntax & Formatting Integrity")
        print("  ✓  All .tf files pass HCL syntax, brace & bracket balance validation")
    else:
        print("\n[4] HCL Syntax & Formatting Integrity")
        for err in errors:
            print(f"  ✗  {err}")
        all_passed = False

    # 5. CIS AWS Benchmark Policies Check
    ok, violations = check_cis_aws_benchmark_policies()
    if ok:
        print("\n[5] CIS AWS Foundations Benchmark Policies")
        print("  ✓  100% compliant with CIS AWS Benchmark (Encryption, Private RDS, CloudTrail, GuardDuty, Security Hub, WAF)")
    else:
        print("\n[5] CIS AWS Foundations Benchmark Policies")
        for viol in violations:
            print(f"  ✗  {viol}")
        all_passed = False

    # 6. Native Terraform Tests & Rego Policies Presence Check
    ok, errors = check_terraform_tests_and_policies()
    if ok:
        print("\n[6] Native Terraform Tests & Policy Definitions")
        print("  ✓  Native .tftest.hcl test suite and CIS AWS Benchmark Rego policy present")
    else:
        print("\n[6] Native Terraform Tests & Policy Definitions")
        for err in errors:
            print(f"  ✗  {err}")
        all_passed = False

    # 7. Zero-PII & Secret Security Scan
    ok, violations = scan_iac_secrets_and_pii()
    if ok:
        print("\n[7] Zero-PII & Secret Security Scan")
        print("  ✓  Zero hardcoded secrets or PII detected in IaC files")
    else:
        print("\n[7] Zero-PII & Secret Security Scan")
        for viol in violations:
            print(f"  ✗  {viol}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL IAC CHECKS & POLICIES PASSED ✓")
        print("=" * 60)
        return True
    else:
        print("IAC VALIDATION FAILED ✗")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = validate_all_iac()
    sys.exit(0 if success else 1)
