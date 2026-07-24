variable "environment" {
  description = "Execution environment"
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
  description = "VPC CIDR block"
  type        = string
}

variable "aws_account_id" {
  description = "AWS Account ID for CloudTrail bucket policies"
  type        = string
  default     = "123456789012"
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
