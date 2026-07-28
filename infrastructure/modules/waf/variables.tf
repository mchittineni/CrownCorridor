#############################################
# Application Configuration
#############################################

variable "environment" {
  description = "Execution environment (dev, staging, prod)"
  type        = string

  validation {
    condition = contains(
      ["dev", "staging", "prod"],
      var.environment
    )

    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "app_name" {
  description = "Name of the application"
  type        = string

  validation {
    condition     = length(var.app_name) >= 3
    error_message = "Application name must contain at least 3 characters."
  }
}

#############################################
# WAF Rate Limiting
#############################################

variable "rate_limit_threshold" {
  description = "Maximum number of requests allowed per 5 minute window per IP address"
  type        = number
  default     = 2000

  validation {
    condition     = var.rate_limit_threshold >= 100
    error_message = "Rate limit threshold must be at least 100 requests."
  }
}

#############################################
# Resource Tags
#############################################

variable "tags" {
  description = "Resource tags applied to WAF resources"
  type        = map(string)

  default = {
    ManagedBy = "Terraform"
    Project   = "CrownCorridor"
  }
}
