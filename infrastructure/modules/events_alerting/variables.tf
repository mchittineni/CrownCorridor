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
  description = "Customer managed KMS key ARN for SNS topic encryption"
  type        = string
}

################################################################################
# EventBridge Configuration
################################################################################

variable "cron_expression" {
  description = "EventBridge cron expression for weekly ETL pipeline execution"

  type = string

  # Every Sunday at 02:00 AM UTC
  default = "cron(0 2 ? * SUN *)"
}

################################################################################
# Alert Configuration
################################################################################

variable "alert_email" {
  description = "Optional email subscriber for SNS alert notifications"

  type = string

  default = ""

  validation {
    condition = var.alert_email == "" || can(
      regex(
        "^[^@]+@[^@]+\\.[^@]+$",
        var.alert_email
      )
    )

    error_message = "alert_email must be a valid email address."
  }
}

################################################################################
# Resource Tags
################################################################################

variable "tags" {
  description = "Resource tags"

  type = map(string)

  default = {}
}
