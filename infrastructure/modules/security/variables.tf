variable "environment" {
  description = "Execution environment (dev, staging, prod)"
  type        = string
}

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where security groups will be created"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block used for internal security group rules"
  type        = string
}

# AWS Account Information
variable "aws_account_id" {
  description = "AWS Account ID used for IAM policies and CloudTrail"
  type        = string
  default     = null
}

# AWS Region
variable "aws_region" {
  description = "AWS Region where security resources are deployed"
  type        = string
  default     = "us-east-1"
}

# GuardDuty Configuration
variable "enable_guardduty" {
  description = "Enable AWS GuardDuty threat detection"
  type        = bool
  default     = true
}

# Security Hub Configuration
variable "enable_securityhub" {
  description = "Enable AWS Security Hub posture monitoring"
  type        = bool
  default     = true
}

# CloudTrail Configuration
variable "cloudtrail_log_retention_days" {
  description = "Number of days to retain CloudTrail audit logs"
  type        = number
  default     = 365
}

# VPC Flow Logs Configuration
variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = true
}

# Resource Tags
variable "tags" {
  description = "Resource tags applied to all security resources"
  type        = map(string)
  default     = {}
}
