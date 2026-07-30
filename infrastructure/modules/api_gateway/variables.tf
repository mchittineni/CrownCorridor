variable "environment" {
  description = "Deployment environment (e.g. dev, test, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "test", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, test, staging, or prod."
  }
}

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "cognito_user_pool_id" {
  description = "Amazon Cognito User Pool ID used by the JWT authorizer"
  type        = string
}

variable "cognito_client_id" {
  description = "Amazon Cognito User Pool App Client ID"
  type        = string
}

variable "backend_integration_uri" {
  description = "Backend integration URI (ALB endpoint, HTTP endpoint, or VPC Link)"
  type        = string
}

variable "allowed_origins" {
  description = "List of allowed CORS origins"

  type = list(string)

  default = [
    "http://localhost:3000"
  ]
}

variable "throttling_burst_limit" {
  description = "API Gateway burst request limit"
  type        = number
  default     = 500

  validation {
    condition     = var.throttling_burst_limit > 0
    error_message = "Burst limit must be greater than zero."
  }
}

variable "throttling_rate_limit" {
  description = "API Gateway steady-state requests per second"
  type        = number
  default     = 1000

  validation {
    condition     = var.throttling_rate_limit > 0
    error_message = "Rate limit must be greater than zero."
  }
}

variable "kms_key_arn" {
  description = "ARN of the customer-managed KMS key used to encrypt CloudWatch Logs"
  type        = string
}

variable "tags" {
  description = "Tags applied to all resources"
  type        = map(string)
  default     = {}
}
