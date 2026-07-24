variable "environment" {
  description = "Execution environment"
  type        = string
}

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "cognito_user_pool_id" {
  description = "Cognito User Pool ID for JWT Authorizer"
  type        = string
}

variable "cognito_client_id" {
  description = "Cognito User Pool Client ID"
  type        = string
}

variable "backend_integration_uri" {
  description = "Backend integration target URI (ALB DNS or VPC Link endpoint)"
  type        = string
}

variable "throttling_burst_limit" {
  description = "API Gateway Throttling Burst Limit"
  type        = number
  default     = 500
}

variable "throttling_rate_limit" {
  description = "API Gateway Throttling Rate Limit (req/sec)"
  type        = number
  default     = 1000
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
