################################################################################
# General Configuration
################################################################################

variable "environment" {
  description = "Execution environment (dev, staging, prod)"
  type        = string

  validation {
    condition = contains(
      ["dev", "staging", "prod"],
      var.environment
    )

    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "app_name" {
  description = "Name of the application"
  type        = string
}

################################################################################
# Encryption
################################################################################

variable "kms_key_arn" {
  description = "Customer managed KMS Key ARN used for secret encryption"
  type        = string
}

################################################################################
# Database Credentials
################################################################################

variable "db_address" {
  description = "RDS PostgreSQL endpoint address"
  type        = string
}

variable "db_port" {
  description = "RDS PostgreSQL port"
  type        = number
  default     = 5432
}

variable "db_name" {
  description = "RDS PostgreSQL database name"
  type        = string
}

variable "db_username" {
  description = "RDS PostgreSQL master/application username"
  type        = string
}

variable "db_password" {
  description = "RDS PostgreSQL password"
  type        = string
  sensitive   = true
}

################################################################################
# Typesense Credentials
################################################################################

variable "typesense_api_key" {
  description = "Typesense API key"
  type        = string
  sensitive   = true
}

################################################################################
# Secrets Rotation
################################################################################

variable "enable_secret_rotation" {
  description = "Enable automatic AWS Secrets Manager rotation"
  type        = bool
  default     = true
}

variable "rotation_days" {
  description = "Number of days between automatic secret rotations"
  type        = number
  default     = 30
}

variable "db_rotation_lambda_arn" {
  description = "AWS Lambda ARN used for RDS PostgreSQL secret rotation"
  type        = string
  default     = ""
}

################################################################################
# Tags
################################################################################

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
