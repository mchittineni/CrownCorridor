variable "environment" {
  description = "Execution environment"
  type        = string
}

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "kms_key_arn" {
  description = "KMS Key ARN for secrets encryption"
  type        = string
}

variable "db_address" {
  description = "RDS DB Host Address"
  type        = string
}

variable "db_port" {
  description = "RDS DB Port"
  type        = number
}

variable "db_name" {
  description = "RDS DB Name"
  type        = string
}

variable "db_username" {
  description = "RDS DB Username"
  type        = string
}

variable "db_password" {
  description = "RDS DB Password"
  type        = string
  sensitive   = true
}

variable "typesense_api_key" {
  description = "Typesense API Key"
  type        = string
  sensitive   = true
  default     = "crowncorridor_super_secret_typesense_key_2026"
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
