variable "environment" {
  description = "Deployment environment (dev, test, staging, prod)"
  type        = string

  validation {
    condition = contains(
      ["dev", "test", "staging", "prod"],
      var.environment
    )

    error_message = "Environment must be one of: dev, test, staging, prod."
  }
}


variable "app_name" {
  description = "Name of the application"
  type        = string

  validation {
    condition     = length(var.app_name) > 2
    error_message = "Application name must contain at least 3 characters."
  }
}


variable "cognito_domain_prefix" {
  description = "Globally unique Cognito hosted UI domain prefix"
  type        = string
  default     = "iacsecbench-dev-auth"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.cognito_domain_prefix))
    error_message = "Cognito domain prefix must contain only lowercase letters, numbers, and hyphens."
  }
}


variable "tags" {
  description = "Resource tags applied to Cognito resources"
  type        = map(string)

  default = {
    ManagedBy = "Terraform"
  }
}
