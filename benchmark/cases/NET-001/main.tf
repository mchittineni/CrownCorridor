# Benchmark Case: NET-001 - Networking & Firewalls Benchmark Scenario #01 (FAIL)
# Difficulty: Easy | Category: NET

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
  case_id     = "NET-001"
}

resource "aws_net_resource" "target" {
  name = "target-${local.case_id}"
  tags = {
    Environment = local.environment
    ManagedBy   = "IaCSecBench"
  }
}
