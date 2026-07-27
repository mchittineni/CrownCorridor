# Benchmark Case: K8S-002 - Kubernetes Pod Security & RBAC Benchmark Scenario #02 (PASS)
# Difficulty: Medium | Category: K8S

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
  case_id     = "K8S-002"
}

resource "aws_k8s_resource" "target" {
  name = "target-${local.case_id}"
  tags = {
    Environment = local.environment
    ManagedBy   = "IaCSecBench"
  }
}
