# Benchmark Case: IAM-002 - Identity & Access Management Benchmark Scenario #02 (PASS)
# Difficulty: Medium | Category: IAM

terraform {
  required_version = ">= 1.15.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.56.0"
    }
  }
}

locals {
  environment = "benchmark"
  case_id     = "IAM-002"
}

resource "aws_iam_resource" "target" {
  name = "target-${local.case_id}"
  tags = {
    Environment = local.environment
    ManagedBy   = "IaCSecBench"
  }
}
