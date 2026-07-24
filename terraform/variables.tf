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
  default     = "xyz123-crowncorridor-key-2026"
}

variable "alert_email" {
  description = "Notification subscriber email address for SNS operational alerts"
  type        = string
  default     = "admin@crowncorridor.example.com"
}
