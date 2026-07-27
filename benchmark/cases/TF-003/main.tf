# Benchmark Case: TF-003 - Terraform HCL Quality & Testing Benchmark Scenario #03 (FAIL)
# Difficulty: Hard | Category: TF

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
  case_id     = "TF-003"
}

resource "aws_tf_resource" "target" {
  name = "target-${local.case_id}"
  tags = {
    Environment = local.environment
    ManagedBy   = "IaCSecBench"
  }
}
