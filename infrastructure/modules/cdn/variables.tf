################################################################################
# CDN Module Variables
################################################################################


variable "environment" {
  description = "Deployment environment (dev, test, staging, prod)"
  type        = string

  validation {
    condition = contains(
      ["dev", "test", "staging", "prod"],
      var.environment
    )

    error_message = "Environment must be one of: dev, test, staging, or prod."
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


################################################################################
# Security
################################################################################


variable "kms_key_arn" {
  description = "ARN of the customer-managed KMS key used for S3 encryption"
  type        = string
}


variable "waf_web_acl_arn" {
  description = "ARN of AWS WAF Web ACL attached to CloudFront"
  type        = string
  default     = ""
}


variable "acm_cert_arn" {
  description = "ARN of ACM certificate used by CloudFront HTTPS"
  type        = string
  default     = ""
}


################################################################################
# CloudFront Failover
################################################################################


variable "failover_bucket_domain_name" {
  description = "Regional domain name of the secondary S3 bucket used for CloudFront origin failover"

  type = string

  default = ""
}


################################################################################
# Metadata
################################################################################


variable "tags" {
  description = "Resource tags applied to CDN resources"

  type = map(string)

  default = {}
}