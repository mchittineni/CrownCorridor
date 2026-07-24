variable "environment" {
  description = "Execution environment"
  type        = string
}

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "kms_key_arn" {
  description = "KMS Key ARN for S3 encryption"
  type        = string
}

variable "waf_web_acl_arn" {
  description = "ARN of WAF Web ACL to attach to CloudFront"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
