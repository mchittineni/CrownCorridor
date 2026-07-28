################################################################################
# General Application Configuration
################################################################################

variable "environment" {
  description = "Execution environment (dev, staging, prod)"
  type        = string
}


variable "app_name" {
  description = "Name of the application"
  type        = string
}


################################################################################
# Networking
################################################################################

variable "vpc_id" {
  description = "VPC ID where ECS and ALB resources are deployed"
  type        = string
}


variable "public_subnet_ids" {
  description = "Public subnet IDs used by the Application Load Balancer"
  type        = list(string)
}


variable "private_subnet_ids" {
  description = "Private subnet IDs used by ECS Fargate tasks"
  type        = list(string)
}



################################################################################
# ECS IAM Roles
################################################################################

variable "ecs_execution_role_arn" {
  description = "IAM execution role ARN used by ECS tasks"
  type        = string
}


variable "ecs_task_role_arn" {
  description = "IAM task role ARN used by application containers"
  type        = string
}



################################################################################
# Security Groups
################################################################################

variable "fastapi_sg_id" {
  description = "Security group ID attached to FastAPI ECS tasks"
  type        = string
}


variable "typesense_sg_id" {
  description = "Security group ID attached to Typesense ECS tasks"
  type        = string
}


variable "efs_sg_id" {
  description = "Security group ID attached to EFS mount targets"
  type        = string
}



################################################################################
# Secrets Manager
################################################################################

variable "typesense_api_key_secret_arn" {
  description = "Secrets Manager ARN containing Typesense API key"
  type        = string
}


variable "db_secret_arn" {
  description = "Secrets Manager ARN containing database credentials"
  type        = string
}



################################################################################
# AWS Configuration
################################################################################

variable "aws_region" {
  description = "AWS region where infrastructure is deployed"
  type        = string
  default     = "us-east-1"
}



################################################################################
# Encryption
################################################################################

variable "kms_key_arn" {
  description = "Customer managed KMS key ARN used for encryption of ECR, EFS, S3 and CloudWatch logs"
  type        = string
}



################################################################################
# Container Image Configuration
################################################################################

variable "image_tag" {
  description = "FastAPI container image tag deployed from ECR"
  type        = string
  default     = "latest"
}



################################################################################
# Application Load Balancer
################################################################################

variable "acm_cert_arn" {
  description = "ACM certificate ARN used for HTTPS listener"
  type        = string
  default     = ""
}


variable "waf_web_acl_arn" {
  description = "AWS WAF Web ACL ARN attached to the Application Load Balancer"
  type        = string
  default     = ""
}



################################################################################
# ECS Auto Scaling
################################################################################

variable "fastapi_min_capacity" {
  description = "Minimum number of FastAPI ECS tasks"
  type        = number
  default     = 2
}


variable "fastapi_max_capacity" {
  description = "Maximum number of FastAPI ECS tasks"
  type        = number
  default     = 10
}



################################################################################
# Resource Tags
################################################################################

variable "tags" {
  description = "Common resource tags"
  type        = map(string)
  default     = {}
}