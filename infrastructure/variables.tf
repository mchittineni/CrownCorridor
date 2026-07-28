##############################################
# AWS Configuration
##############################################

variable "aws_region" {

  description = "AWS region for deployment"

  type = string

  default = "us-east-1"
}

variable "aws_account_id" {

  description = "AWS Account ID used for security policies and CloudTrail"

  type = string

  default = null
}

##############################################
# Application Configuration
##############################################

variable "environment" {

  description = "Target deployment environment (dev, staging, prod)"

  type = string

  default = "dev"
}

variable "app_name" {

  description = "Application identifier name"

  type = string

  default = "crowncorridor"
}

##############################################
# Network Configuration
##############################################

variable "vpc_cidr" {

  description = "CIDR block for the VPC"

  type = string

  default = "10.0.0.0/16"
}

variable "availability_zones" {

  description = "AWS availability zones"

  type = list(string)

  default = [
    "us-east-1a",
    "us-east-1b"
  ]
}

variable "public_subnet_cidrs" {

  description = "Public subnet CIDR blocks"

  type = list(string)

  default = [
    "10.0.1.0/24",
    "10.0.2.0/24"
  ]
}

variable "private_subnet_cidrs" {

  description = "Private application subnet CIDR blocks"

  type = list(string)

  default = [
    "10.0.10.0/24",
    "10.0.11.0/24"
  ]
}

variable "database_subnet_cidrs" {

  description = "Private database subnet CIDR blocks"

  type = list(string)

  default = [
    "10.0.20.0/24",
    "10.0.21.0/24"
  ]
}

##############################################
# Secrets
##############################################

variable "typesense_api_key" {

  description = "API key for Typesense search service"

  type = string

  sensitive = true
}

##############################################
# Monitoring
##############################################

variable "alert_email" {

  description = "Email address for SNS operational and security alerts"

  type = string

  default = ""
}

##############################################
# ACM / HTTPS
##############################################

variable "acm_certificate_arn" {

  description = "ACM certificate ARN for HTTPS listeners"

  type = string

  default = ""
}

##############################################
# Tags
##############################################

variable "tags" {

  description = "Global resource tags"

  type = map(string)

  default = {

    Project = "CrownCorridor"

  }
}
