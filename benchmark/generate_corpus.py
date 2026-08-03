"""IaCSecBench — controlled corpus generator.

Emits one vulnerable and one compliant case for each canonical control, as real
Terraform that ``terraform validate`` accepts and ``terraform plan`` can resolve.

Why a generator rather than hand-authored files
-----------------------------------------------
Each case must satisfy four properties simultaneously: valid HCL2 against the
real provider schema, an unambiguous ground-truth label, an explicit canonical
control annotation, and a vulnerable/compliant pair that differs *only* in the
security-relevant attribute. Hand-authoring drifts on all four. Generating them
from one specification per control keeps the pair minimal and the annotation
consistent, and makes the corpus auditable: the specification is the ground
truth, and the emitted HCL is derived from it.

The generated cases are not synthetic *results*. They are real configurations
that real scanners analyse; nothing here predicts or asserts what any tool will
find.

Design rules enforced for every pair
------------------------------------
1. The compliant variant differs from the vulnerable variant only in the
   attributes named by the control. Everything else -- resource types, names,
   supporting resources -- is identical, so a detection difference cannot be
   attributed to incidental structure.
2. The compliant variant must be genuinely compliant with respect to *its own*
   control only. It may still violate unrelated controls; that is expected and is
   why detection is scored per control rather than per case.
3. Both variants declare ``canonical_controls`` explicitly. No case relies on
   inference from a CIS section number.
4. Resource addresses are recorded in ``expected.json`` so that resource-level
   matching is applicable.

Usage::

    python benchmark/generate_corpus.py --dry-run
    python benchmark/generate_corpus.py --write
    python benchmark/generate_corpus.py --write --clean
"""

# Most of this module's length is the corpus itself: one ControlSpec per canonical
# control, each embedding the literal HCL for its vulnerable and compliant case.
# Splitting it across files would separate a specification from the ground truth
# it defines, which is the one thing this design exists to keep together.
# pylint: disable=too-many-lines

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "benchmark" / "internal" / "cases"

TERRAFORM_HEADER = """\
terraform {
  required_version = ">= 1.9.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
"""

VARIABLES_TF = """\
variable "name_prefix" {
  type        = string
  default     = "iacsecbench"
  description = "Prefix applied to generated resource names."

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.name_prefix))
    error_message = "name_prefix must contain only lowercase letters, digits and hyphens."
  }
}

variable "environment" {
  type        = string
  default     = "benchmark"
  description = "Deployment environment label."
}
"""


@dataclass
class ControlSpec:
    """Specification for one canonical control's case pair."""

    control_id: str
    domain: str
    cis_control: str
    severity: str
    title: str
    # The security-relevant difference, stated in prose for the metadata.
    vulnerable_summary: str
    compliant_summary: str
    # HCL bodies. Both must be valid and differ only in the control's attributes.
    vulnerable_hcl: str
    compliant_hcl: str
    # Resource addresses the violation lives at.
    resources: list[str] = field(default_factory=list)
    # Terraform language features exercised, for the complexity table.
    features: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Control specifications
#
# Ordered by domain. Each pair is minimal: read the two HCL bodies side by side
# and the only difference should be the attribute the control governs.
# --------------------------------------------------------------------------- #

SPECS: list[ControlSpec] = [
    # ---------------------------- storage --------------------------------- #
    ControlSpec(
        control_id="STO_PUBLIC_BUCKET",
        domain="STO",
        cis_control="2.1.5",
        severity="CRITICAL",
        title="Object storage public access block",
        vulnerable_summary="All four public access block flags are disabled.",
        compliant_summary="All four public access block flags are enabled.",
        resources=["aws_s3_bucket_public_access_block.target"],
        features=["locals", "interpolation"],
        vulnerable_hcl="""
locals {
  bucket_name = "${var.name_prefix}-sto-public-${var.environment}"
}

resource "aws_s3_bucket" "target" {
  bucket = local.bucket_name
}

resource "aws_s3_bucket_public_access_block" "target" {
  bucket                  = aws_s3_bucket.target.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
""",
        compliant_hcl="""
locals {
  bucket_name = "${var.name_prefix}-sto-public-${var.environment}"
}

resource "aws_s3_bucket" "target" {
  bucket = local.bucket_name
}

resource "aws_s3_bucket_public_access_block" "target" {
  bucket                  = aws_s3_bucket.target.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
""",
    ),
    ControlSpec(
        control_id="STO_UNENCRYPTED_BUCKET",
        domain="ENC",
        cis_control="2.1.1",
        severity="HIGH",
        title="Object storage encryption at rest",
        vulnerable_summary="Bucket encryption uses AES256 rather than a customer-managed key.",
        compliant_summary="Bucket encryption uses a customer-managed KMS key.",
        resources=["aws_s3_bucket_server_side_encryption_configuration.target"],
        features=["locals", "resource references"],
        vulnerable_hcl="""
resource "aws_s3_bucket" "target" {
  bucket = "${var.name_prefix}-sto-enc-${var.environment}"
}

resource "aws_kms_key" "target" {
  description             = "Benchmark key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_s3_bucket_server_side_encryption_configuration" "target" {
  bucket = aws_s3_bucket.target.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
""",
        compliant_hcl="""
resource "aws_s3_bucket" "target" {
  bucket = "${var.name_prefix}-sto-enc-${var.environment}"
}

resource "aws_kms_key" "target" {
  description             = "Benchmark key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_s3_bucket_server_side_encryption_configuration" "target" {
  bucket = aws_s3_bucket.target.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.target.arn
      sse_algorithm     = "aws:kms"
    }
  }
}
""",
    ),
    ControlSpec(
        control_id="STO_NO_ACCESS_LOGGING",
        domain="MON",
        cis_control="2.1.3",
        severity="MEDIUM",
        title="Object storage access logging",
        vulnerable_summary="No access logging configuration is declared for the bucket.",
        compliant_summary="Access logging is directed to a dedicated log bucket.",
        resources=["aws_s3_bucket.target"],
        features=["multiple resources"],
        vulnerable_hcl="""
resource "aws_s3_bucket" "logs" {
  bucket = "${var.name_prefix}-sto-logs-${var.environment}"
}

resource "aws_s3_bucket" "target" {
  bucket = "${var.name_prefix}-sto-log-${var.environment}"
}
""",
        compliant_hcl="""
resource "aws_s3_bucket" "logs" {
  bucket = "${var.name_prefix}-sto-logs-${var.environment}"
}

resource "aws_s3_bucket" "target" {
  bucket = "${var.name_prefix}-sto-log-${var.environment}"
}

resource "aws_s3_bucket_logging" "target" {
  bucket        = aws_s3_bucket.target.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "access/"
}
""",
    ),
    # ---------------------------- network --------------------------------- #
    ControlSpec(
        control_id="NET_UNRESTRICTED_INGRESS",
        domain="NET",
        cis_control="5.2",
        severity="CRITICAL",
        title="Unrestricted network ingress",
        vulnerable_summary="Security group permits SSH ingress from 0.0.0.0/0.",
        compliant_summary="Security group permits SSH ingress only from the VPC CIDR.",
        resources=["aws_security_group.target"],
        features=["locals", "dynamic block", "resource references"],
        vulnerable_hcl="""
locals {
  ingress_cidrs = ["0.0.0.0/0"]
}

resource "aws_vpc" "target" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_security_group" "target" {
  name        = "${var.name_prefix}-net-ingress"
  description = "Benchmark ingress group"
  vpc_id      = aws_vpc.target.id

  dynamic "ingress" {
    for_each = local.ingress_cidrs
    content {
      description = "SSH"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
""",
        compliant_hcl="""
locals {
  ingress_cidrs = ["10.0.0.0/16"]
}

resource "aws_vpc" "target" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_security_group" "target" {
  name        = "${var.name_prefix}-net-ingress"
  description = "Benchmark ingress group"
  vpc_id      = aws_vpc.target.id

  dynamic "ingress" {
    for_each = local.ingress_cidrs
    content {
      description = "SSH"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
""",
    ),
    ControlSpec(
        control_id="NET_NO_FLOW_LOGS",
        domain="MON",
        cis_control="3.9",
        severity="MEDIUM",
        title="Virtual network flow logging",
        vulnerable_summary="No flow log is declared for the VPC.",
        compliant_summary="A flow log delivers VPC traffic records to CloudWatch Logs.",
        resources=["aws_vpc.target"],
        features=["iam policy document", "resource references"],
        vulnerable_hcl="""
resource "aws_vpc" "target" {
  cidr_block           = "10.1.0.0/16"
  enable_dns_hostnames = true
}
""",
        compliant_hcl="""
resource "aws_vpc" "target" {
  cidr_block           = "10.1.0.0/16"
  enable_dns_hostnames = true
}

resource "aws_cloudwatch_log_group" "flow" {
  name              = "/${var.name_prefix}/vpc/flow"
  retention_in_days = 365
}

resource "aws_iam_role" "flow" {
  name = "${var.name_prefix}-flow-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "vpc-flow-logs.amazonaws.com" }
    }]
  })
}

resource "aws_flow_log" "target" {
  iam_role_arn    = aws_iam_role.flow.arn
  log_destination = aws_cloudwatch_log_group.flow.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.target.id
}
""",
    ),
    ControlSpec(
        control_id="NET_PUBLIC_INSTANCE",
        domain="NET",
        cis_control="5.6",
        severity="HIGH",
        title="Compute instance public addressing",
        vulnerable_summary="Instance is launched with a public IP association.",
        compliant_summary="Instance is launched without a public IP association.",
        resources=["aws_instance.target"],
        features=["data source", "resource references"],
        vulnerable_hcl="""
resource "aws_vpc" "target" {
  cidr_block = "10.2.0.0/16"
}

resource "aws_subnet" "target" {
  vpc_id     = aws_vpc.target.id
  cidr_block = "10.2.1.0/24"
}

resource "aws_instance" "target" {
  ami                         = "ami-0abcdef1234567890"
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.target.id
  associate_public_ip_address  = true

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    encrypted = true
  }
}
""",
        compliant_hcl="""
resource "aws_vpc" "target" {
  cidr_block = "10.2.0.0/16"
}

resource "aws_subnet" "target" {
  vpc_id     = aws_vpc.target.id
  cidr_block = "10.2.1.0/24"
}

resource "aws_instance" "target" {
  ami                         = "ami-0abcdef1234567890"
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.target.id
  associate_public_ip_address  = false

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    encrypted = true
  }
}
""",
    ),
    ControlSpec(
        control_id="NET_NO_HTTPS_REDIRECT",
        domain="NET",
        cis_control="n/a",
        severity="MEDIUM",
        title="Content delivery HTTPS enforcement",
        vulnerable_summary="Cache behaviour allows plaintext HTTP viewer requests.",
        compliant_summary="Cache behaviour redirects viewer requests to HTTPS.",
        resources=["aws_cloudfront_distribution.target"],
        features=["nested blocks"],
        vulnerable_hcl="""
resource "aws_cloudfront_distribution" "target" {
  enabled = true

  origin {
    domain_name = "origin.example.com"
    origin_id   = "primary"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "primary"
    viewer_protocol_policy = "allow-all"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
""",
        compliant_hcl="""
resource "aws_cloudfront_distribution" "target" {
  enabled = true

  origin {
    domain_name = "origin.example.com"
    origin_id   = "primary"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "primary"
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
""",
    ),
    ControlSpec(
        control_id="NET_ALB_INVALID_HEADERS",
        domain="NET",
        cis_control="n/a",
        severity="MEDIUM",
        title="Load balancer header sanitisation",
        vulnerable_summary="Load balancer forwards invalid HTTP header fields.",
        compliant_summary="Load balancer drops invalid HTTP header fields.",
        resources=["aws_lb.target"],
        features=["count", "resource references"],
        vulnerable_hcl="""
resource "aws_vpc" "target" {
  cidr_block = "10.3.0.0/16"
}

resource "aws_subnet" "target" {
  count             = 2
  vpc_id            = aws_vpc.target.id
  cidr_block        = cidrsubnet(aws_vpc.target.cidr_block, 8, count.index)
  availability_zone = count.index == 0 ? "eu-west-2a" : "eu-west-2b"
}

resource "aws_lb" "target" {
  name                       = "${var.name_prefix}-alb"
  internal                   = true
  load_balancer_type         = "application"
  subnets                    = aws_subnet.target[*].id
  drop_invalid_header_fields = false
}
""",
        compliant_hcl="""
resource "aws_vpc" "target" {
  cidr_block = "10.3.0.0/16"
}

resource "aws_subnet" "target" {
  count             = 2
  vpc_id            = aws_vpc.target.id
  cidr_block        = cidrsubnet(aws_vpc.target.cidr_block, 8, count.index)
  availability_zone = count.index == 0 ? "eu-west-2a" : "eu-west-2b"
}

resource "aws_lb" "target" {
  name                       = "${var.name_prefix}-alb"
  internal                   = true
  load_balancer_type         = "application"
  subnets                    = aws_subnet.target[*].id
  drop_invalid_header_fields = true
}
""",
    ),
    # ------------------------------ IAM ----------------------------------- #
    ControlSpec(
        control_id="IAM_WILDCARD_ACTION",
        domain="IAM",
        cis_control="1.16",
        severity="CRITICAL",
        title="Identity policy action scope",
        vulnerable_summary="Policy grants Action '*' on Resource '*'.",
        compliant_summary="Policy grants a single read action on a specific bucket ARN.",
        resources=["aws_iam_policy.target"],
        features=["jsonencode", "resource references"],
        vulnerable_hcl="""
resource "aws_s3_bucket" "target" {
  bucket = "${var.name_prefix}-iam-scope-${var.environment}"
}

resource "aws_iam_policy" "target" {
  name = "${var.name_prefix}-iam-wildcard"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "*"
      Resource = "*"
    }]
  })
}
""",
        compliant_hcl="""
resource "aws_s3_bucket" "target" {
  bucket = "${var.name_prefix}-iam-scope-${var.environment}"
}

resource "aws_iam_policy" "target" {
  name = "${var.name_prefix}-iam-wildcard"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "s3:GetObject"
      Resource = "${aws_s3_bucket.target.arn}/*"
    }]
  })
}
""",
    ),
    ControlSpec(
        control_id="IAM_WILDCARD_TRUST",
        domain="IAM",
        cis_control="1.16",
        severity="CRITICAL",
        title="Role trust policy principal scope",
        vulnerable_summary="Trust policy allows sts:AssumeRole from principal '*'.",
        compliant_summary="Trust policy allows sts:AssumeRole from a named service principal.",
        resources=["aws_iam_role.target"],
        features=["jsonencode"],
        vulnerable_hcl="""
resource "aws_iam_role" "target" {
  name = "${var.name_prefix}-iam-trust"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = "*"
    }]
  })
}
""",
        compliant_hcl="""
resource "aws_iam_role" "target" {
  name = "${var.name_prefix}-iam-trust"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}
""",
    ),
    # --------------------------- encryption -------------------------------- #
    ControlSpec(
        control_id="ENC_UNENCRYPTED_VOLUME",
        domain="ENC",
        cis_control="2.2.1",
        severity="HIGH",
        title="Block storage encryption at rest",
        vulnerable_summary="EBS volume is created unencrypted.",
        compliant_summary="EBS volume is encrypted with a customer-managed key.",
        resources=["aws_ebs_volume.target"],
        features=["resource references"],
        vulnerable_hcl="""
resource "aws_kms_key" "target" {
  description             = "Benchmark volume key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_ebs_volume" "target" {
  availability_zone = "eu-west-2a"
  size              = 8
  encrypted         = false
}
""",
        compliant_hcl="""
resource "aws_kms_key" "target" {
  description             = "Benchmark volume key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_ebs_volume" "target" {
  availability_zone = "eu-west-2a"
  size              = 8
  encrypted         = true
  kms_key_id        = aws_kms_key.target.arn
}
""",
    ),
    ControlSpec(
        control_id="ENC_UNENCRYPTED_DATABASE",
        domain="ENC",
        cis_control="2.3.1",
        severity="HIGH",
        title="Managed database encryption at rest",
        vulnerable_summary="Database instance storage is unencrypted.",
        compliant_summary="Database instance storage is encrypted with a KMS key.",
        resources=["aws_db_instance.target"],
        features=["resource references"],
        vulnerable_hcl="""
resource "aws_kms_key" "target" {
  description             = "Benchmark database key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_db_instance" "target" {
  identifier              = "${var.name_prefix}-enc-db"
  allocated_storage       = 20
  engine                  = "postgres"
  instance_class          = "db.t3.micro"
  username                = "benchmark"
  manage_master_user_password = true
  skip_final_snapshot     = true
  publicly_accessible     = false
  storage_encrypted       = false
}
""",
        compliant_hcl="""
resource "aws_kms_key" "target" {
  description             = "Benchmark database key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_db_instance" "target" {
  identifier              = "${var.name_prefix}-enc-db"
  allocated_storage       = 20
  engine                  = "postgres"
  instance_class          = "db.t3.micro"
  username                = "benchmark"
  manage_master_user_password = true
  skip_final_snapshot     = true
  publicly_accessible     = false
  storage_encrypted       = true
  kms_key_id              = aws_kms_key.target.arn
}
""",
    ),
    ControlSpec(
        control_id="ENC_NO_KEY_ROTATION",
        domain="ENC",
        cis_control="3.8",
        severity="MEDIUM",
        title="Key management rotation",
        vulnerable_summary="KMS key has automatic rotation disabled.",
        compliant_summary="KMS key has automatic rotation enabled.",
        resources=["aws_kms_key.target"],
        features=["basic resource"],
        vulnerable_hcl="""
resource "aws_kms_key" "target" {
  description             = "Benchmark rotation key"
  deletion_window_in_days = 7
  enable_key_rotation     = false
}
""",
        compliant_hcl="""
resource "aws_kms_key" "target" {
  description             = "Benchmark rotation key"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}
""",
    ),
    ControlSpec(
        control_id="STO_PUBLIC_DATABASE",
        domain="NET",
        cis_control="2.3.3",
        severity="CRITICAL",
        title="Managed database public accessibility",
        vulnerable_summary="Database instance is publicly accessible.",
        compliant_summary="Database instance is not publicly accessible.",
        resources=["aws_db_instance.target"],
        features=["basic resource"],
        vulnerable_hcl="""
resource "aws_db_instance" "target" {
  identifier                  = "${var.name_prefix}-net-db"
  allocated_storage           = 20
  engine                      = "postgres"
  instance_class              = "db.t3.micro"
  username                    = "benchmark"
  manage_master_user_password = true
  skip_final_snapshot         = true
  storage_encrypted           = true
  publicly_accessible         = true
}
""",
        compliant_hcl="""
resource "aws_db_instance" "target" {
  identifier                  = "${var.name_prefix}-net-db"
  allocated_storage           = 20
  engine                      = "postgres"
  instance_class              = "db.t3.micro"
  username                    = "benchmark"
  manage_master_user_password = true
  skip_final_snapshot         = true
  storage_encrypted           = true
  publicly_accessible         = false
}
""",
    ),
    # --------------------------- monitoring -------------------------------- #
    ControlSpec(
        control_id="MON_NO_TRAIL_VALIDATION",
        domain="MON",
        cis_control="3.2",
        severity="MEDIUM",
        title="Audit trail log file validation",
        vulnerable_summary="Trail has log file integrity validation disabled.",
        compliant_summary="Trail has log file integrity validation enabled.",
        resources=["aws_cloudtrail.target"],
        features=["resource references"],
        vulnerable_hcl="""
resource "aws_s3_bucket" "trail" {
  bucket = "${var.name_prefix}-mon-val-${var.environment}"
}

resource "aws_kms_key" "trail" {
  description             = "Benchmark trail key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_cloudtrail" "target" {
  name                          = "${var.name_prefix}-mon-val"
  s3_bucket_name                = aws_s3_bucket.trail.id
  kms_key_id                    = aws_kms_key.trail.arn
  is_multi_region_trail         = true
  enable_log_file_validation    = false
}
""",
        compliant_hcl="""
resource "aws_s3_bucket" "trail" {
  bucket = "${var.name_prefix}-mon-val-${var.environment}"
}

resource "aws_kms_key" "trail" {
  description             = "Benchmark trail key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_cloudtrail" "target" {
  name                          = "${var.name_prefix}-mon-val"
  s3_bucket_name                = aws_s3_bucket.trail.id
  kms_key_id                    = aws_kms_key.trail.arn
  is_multi_region_trail         = true
  enable_log_file_validation    = true
}
""",
    ),
    ControlSpec(
        control_id="MON_TRAIL_NOT_MULTIREGION",
        domain="MON",
        cis_control="3.1",
        severity="MEDIUM",
        title="Audit trail regional coverage",
        vulnerable_summary="Trail records events in a single region only.",
        compliant_summary="Trail records events across all regions.",
        resources=["aws_cloudtrail.target"],
        features=["resource references"],
        vulnerable_hcl="""
resource "aws_s3_bucket" "trail" {
  bucket = "${var.name_prefix}-mon-region-${var.environment}"
}

resource "aws_kms_key" "trail" {
  description             = "Benchmark trail key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_cloudtrail" "target" {
  name                       = "${var.name_prefix}-mon-region"
  s3_bucket_name             = aws_s3_bucket.trail.id
  kms_key_id                 = aws_kms_key.trail.arn
  enable_log_file_validation = true
  is_multi_region_trail      = false
}
""",
        compliant_hcl="""
resource "aws_s3_bucket" "trail" {
  bucket = "${var.name_prefix}-mon-region-${var.environment}"
}

resource "aws_kms_key" "trail" {
  description             = "Benchmark trail key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_cloudtrail" "target" {
  name                       = "${var.name_prefix}-mon-region"
  s3_bucket_name             = aws_s3_bucket.trail.id
  kms_key_id                 = aws_kms_key.trail.arn
  enable_log_file_validation = true
  is_multi_region_trail      = true
}
""",
    ),
    ControlSpec(
        control_id="MON_NO_LOG_ENCRYPTION",
        domain="MON",
        cis_control="3.5",
        severity="MEDIUM",
        title="Audit log encryption",
        vulnerable_summary="Trail logs are not encrypted with a customer-managed key.",
        compliant_summary="Trail logs are encrypted with a customer-managed KMS key.",
        resources=["aws_cloudtrail.target"],
        features=["resource references"],
        vulnerable_hcl="""
resource "aws_s3_bucket" "trail" {
  bucket = "${var.name_prefix}-mon-enc-${var.environment}"
}

resource "aws_cloudtrail" "target" {
  name                       = "${var.name_prefix}-mon-enc"
  s3_bucket_name             = aws_s3_bucket.trail.id
  enable_log_file_validation = true
  is_multi_region_trail      = true
}
""",
        compliant_hcl="""
resource "aws_s3_bucket" "trail" {
  bucket = "${var.name_prefix}-mon-enc-${var.environment}"
}

resource "aws_kms_key" "trail" {
  description             = "Benchmark trail key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_cloudtrail" "target" {
  name                       = "${var.name_prefix}-mon-enc"
  s3_bucket_name             = aws_s3_bucket.trail.id
  kms_key_id                 = aws_kms_key.trail.arn
  enable_log_file_validation = true
  is_multi_region_trail      = true
}
""",
    ),
    # ---------------------------- compute ---------------------------------- #
    ControlSpec(
        control_id="CMP_NO_IMDSV2",
        domain="CMP",
        cis_control="5.6",
        severity="HIGH",
        title="Instance metadata service authentication",
        vulnerable_summary="Instance metadata service permits unauthenticated IMDSv1 access.",
        compliant_summary="Instance metadata service requires IMDSv2 session tokens.",
        resources=["aws_instance.target"],
        features=["nested blocks"],
        vulnerable_hcl="""
resource "aws_instance" "target" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "t3.micro"

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "optional"
  }

  root_block_device {
    encrypted = true
  }
}
""",
        compliant_hcl="""
resource "aws_instance" "target" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "t3.micro"

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    encrypted = true
  }
}
""",
    ),
    ControlSpec(
        control_id="CMP_NO_IMAGE_SCANNING",
        domain="CMP",
        cis_control="n/a",
        severity="MEDIUM",
        title="Container registry image scanning",
        vulnerable_summary="Repository does not scan images on push.",
        compliant_summary="Repository scans images on push.",
        resources=["aws_ecr_repository.target"],
        features=["nested blocks"],
        vulnerable_hcl="""
resource "aws_ecr_repository" "target" {
  name                 = "${var.name_prefix}-cmp-scan"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}
""",
        compliant_hcl="""
resource "aws_ecr_repository" "target" {
  name                 = "${var.name_prefix}-cmp-scan"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
""",
    ),
    ControlSpec(
        control_id="CMP_MUTABLE_IMAGE_TAGS",
        domain="CMP",
        cis_control="n/a",
        severity="LOW",
        title="Container registry tag immutability",
        vulnerable_summary="Repository permits mutable image tags.",
        compliant_summary="Repository enforces immutable image tags.",
        resources=["aws_ecr_repository.target"],
        features=["nested blocks"],
        vulnerable_hcl="""
resource "aws_ecr_repository" "target" {
  name                 = "${var.name_prefix}-cmp-tags"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
""",
        compliant_hcl="""
resource "aws_ecr_repository" "target" {
  name                 = "${var.name_prefix}-cmp-tags"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
""",
    ),
    # --------------------------- serverless -------------------------------- #
    ControlSpec(
        control_id="SRV_NO_FUNCTION_ENCRYPTION",
        domain="SRV",
        cis_control="n/a",
        severity="HIGH",
        title="Function environment variable encryption",
        vulnerable_summary="Function environment variables are not encrypted with a KMS key.",
        compliant_summary="Function environment variables are encrypted with a KMS key.",
        resources=["aws_lambda_function.target"],
        features=["jsonencode", "resource references"],
        vulnerable_hcl="""
resource "aws_iam_role" "target" {
  name = "${var.name_prefix}-srv-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_kms_key" "target" {
  description             = "Benchmark function key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_lambda_function" "target" {
  function_name = "${var.name_prefix}-srv-enc"
  role          = aws_iam_role.target.arn
  handler       = "index.handler"
  runtime       = "python3.12"
  filename      = "function.zip"

  environment {
    variables = {
      STAGE = var.environment
    }
  }

  tracing_config {
    mode = "Active"
  }
}
""",
        compliant_hcl="""
resource "aws_iam_role" "target" {
  name = "${var.name_prefix}-srv-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_kms_key" "target" {
  description             = "Benchmark function key"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_lambda_function" "target" {
  function_name    = "${var.name_prefix}-srv-enc"
  role             = aws_iam_role.target.arn
  handler          = "index.handler"
  runtime          = "python3.12"
  filename         = "function.zip"
  kms_key_arn      = aws_kms_key.target.arn

  environment {
    variables = {
      STAGE = var.environment
    }
  }

  tracing_config {
    mode = "Active"
  }
}
""",
    ),
    # ----------------------------- secrets --------------------------------- #
    ControlSpec(
        control_id="SEC_HARDCODED_CREDENTIAL",
        domain="SEC",
        cis_control="1.4",
        severity="CRITICAL",
        title="Embedded credential material",
        vulnerable_summary="Function environment embeds a literal credential value.",
        compliant_summary="Function reads the credential from Secrets Manager by ARN.",
        resources=["aws_lambda_function.target"],
        features=["jsonencode", "resource references"],
        vulnerable_hcl="""
resource "aws_iam_role" "target" {
  name = "${var.name_prefix}-sec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_lambda_function" "target" {
  function_name = "${var.name_prefix}-sec-cred"
  role          = aws_iam_role.target.arn
  handler       = "index.handler"
  runtime       = "python3.12"
  filename      = "function.zip"

  environment {
    variables = {
      DB_PASSWORD = "SuperSecretP4ssw0rd!"
    }
  }
}
""",
        compliant_hcl="""
resource "aws_iam_role" "target" {
  name = "${var.name_prefix}-sec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_secretsmanager_secret" "target" {
  name = "${var.name_prefix}-sec-cred"
}

resource "aws_lambda_function" "target" {
  function_name = "${var.name_prefix}-sec-cred"
  role          = aws_iam_role.target.arn
  handler       = "index.handler"
  runtime       = "python3.12"
  filename      = "function.zip"

  environment {
    variables = {
      DB_PASSWORD_SECRET_ARN = aws_secretsmanager_secret.target.arn
    }
  }
}
""",
    ),
]


# --------------------------------------------------------------------------- #
# Emission
# --------------------------------------------------------------------------- #


def case_id(spec: ControlSpec, variant: str) -> str:
    """Builds a stable case identifier, e.g. ``STO-PUBLIC-BUCKET-VULN``."""
    slug = spec.control_id.replace("_", "-")
    return f"{slug}-{'VULN' if variant == 'vulnerable' else 'SAFE'}"


def render_case(spec: ControlSpec, variant: str) -> dict[str, str]:
    """Renders the files for one case."""
    is_vulnerable = variant == "vulnerable"
    identifier = case_id(spec, variant)
    body = spec.vulnerable_hcl if is_vulnerable else spec.compliant_hcl
    summary = spec.vulnerable_summary if is_vulnerable else spec.compliant_summary
    expected = "VIOLATION" if is_vulnerable else "COMPLIANT"

    main_tf = (
        f"# IaCSecBench case {identifier}\n"
        f"# Control : {spec.control_id} ({spec.title})\n"
        f"# Expected: {expected}\n"
        f"# Rationale: {summary}\n"
        f"#\n"
        f"# Generated by benchmark/generate_corpus.py. Edit the specification\n"
        f"# there rather than this file, so the vulnerable/compliant pair stays\n"
        f"# minimal and the annotation stays consistent.\n"
        f"\n{TERRAFORM_HEADER}{body}"
    )

    metadata = {
        "id": identifier,
        "title": f"{spec.title} ({expected})",
        "description": summary,
        "expected_result": "FAIL" if is_vulnerable else "PASS",
        "has_violation": is_vulnerable,
        "canonical_controls": [spec.control_id],
        "benchmark_category": spec.domain,
        "cis_control": spec.cis_control,
        "severity": spec.severity if is_vulnerable else "NONE",
        "provider": "aws",
        "benchmark_features": spec.features,
        "pair_id": spec.control_id,
        "pair_variant": variant,
        "generated_by": "benchmark/generate_corpus.py",
    }
    if is_vulnerable:
        metadata["expected_violations"] = [
            {
                "resource": resource,
                "control": spec.control_id,
                "description": summary,
            }
            for resource in spec.resources
        ]

    expected_json = {
        "benchmark_id": identifier,
        "expected_result": "FAIL" if is_vulnerable else "PASS",
        "canonical_controls": [spec.control_id],
        "severity": spec.severity if is_vulnerable else "NONE",
        "violations": (
            [{"resource": r, "control": spec.control_id} for r in spec.resources]
            if is_vulnerable
            else []
        ),
    }

    return {
        "main.tf": main_tf,
        "variables.tf": VARIABLES_TF,
        "metadata.json": json.dumps(metadata, indent=2) + "\n",
        "expected.json": json.dumps(expected_json, indent=2) + "\n",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the IaCSecBench controlled corpus")
    parser.add_argument("--write", action="store_true", help="write cases to disk")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="remove existing case directories first (required to drop stale cases)",
    )
    parser.add_argument("--dry-run", action="store_true", help="report what would be written")
    args = parser.parse_args(argv)

    controls = {spec.control_id for spec in SPECS}
    if len(controls) != len(SPECS):
        duplicates = [
            s.control_id for s in SPECS if [x.control_id for x in SPECS].count(s.control_id) > 1
        ]
        parser.error(f"duplicate control specifications: {sorted(set(duplicates))}")

    planned = [(spec, variant) for spec in SPECS for variant in ("vulnerable", "compliant")]

    print(
        f"{len(SPECS)} control specifications -> {len(planned)} cases "
        f"({len(SPECS)} vulnerable, {len(SPECS)} compliant)"
    )
    domains = sorted({s.domain for s in SPECS})
    print(f"domains: {', '.join(domains)}")

    if args.dry_run or not args.write:
        for spec, variant in planned:
            print(f"  {case_id(spec, variant):<38} {spec.control_id}")
        if not args.write:
            print("\nNothing written. Pass --write to emit, --clean to drop stale cases first.")
        return 0

    if args.clean and CASES_DIR.exists():
        removed = 0
        for existing in sorted(p for p in CASES_DIR.iterdir() if p.is_dir()):
            shutil.rmtree(existing)
            removed += 1
        print(f"removed {removed} existing case directories")

    CASES_DIR.mkdir(parents=True, exist_ok=True)
    for spec, variant in planned:
        identifier = case_id(spec, variant)
        target = CASES_DIR / identifier
        target.mkdir(exist_ok=True)
        for filename, content in render_case(spec, variant).items():
            (target / filename).write_text(content, encoding="utf-8")

    print(f"wrote {len(planned)} cases to {CASES_DIR.relative_to(ROOT)}/")
    print("\nNext: python -m evaluation.corpus --report --mode terraform")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
