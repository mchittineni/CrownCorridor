variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Target execution environment (e.g. dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "app_name" {
  description = "Application identifier name"
  type        = string
  default     = "crowncorridor"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "typesense_api_key" {
  description = "API key for Typesense search cluster"
  type        = string
  sensitive   = true
}

variable "alert_email" {
  description = "Notification subscriber email address for SNS operational alerts"
  type        = string
}

variable "aws_account_id" {
  description = "AWS Account ID for CloudTrail & security policies"
  type        = string
  default     = "123456789012"
}
