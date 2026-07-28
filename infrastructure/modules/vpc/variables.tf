#############################################
# Environment Configuration
#############################################

variable "environment" {
  description = "Execution environment (dev, staging, prod)"
  type        = string
  default     = "dev"

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
  default     = "crowncorridor"
}

#############################################
# VPC Configuration
#############################################

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_dns_support" {
  description = "Enable DNS resolution inside VPC"
  type        = bool
  default     = true
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames inside VPC"
  type        = bool
  default     = true
}

#############################################
# Availability Zones
#############################################

variable "availability_zones" {
  description = "Availability Zones where resources will be deployed"
  type        = list(string)

  default = [
    "us-east-1a",
    "us-east-1b"
  ]
}

#############################################
# Subnet CIDR Configuration
#############################################

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets hosting ALB and internet resources"
  type        = list(string)

  default = [
    "10.0.1.0/24",
    "10.0.2.0/24"
  ]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private application subnets hosting ECS workloads"
  type        = list(string)

  default = [
    "10.0.10.0/24",
    "10.0.11.0/24"
  ]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for isolated database subnets hosting RDS"
  type        = list(string)

  default = [
    "10.0.20.0/24",
    "10.0.21.0/24"
  ]
}

#############################################
# NAT Gateway Configuration
#############################################

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnet internet access"
  type        = bool
  default     = true
}

#############################################
# Resource Tags
#############################################

variable "tags" {
  description = "Common resource tags"
  type        = map(string)

  default = {
    ManagedBy = "Terraform"
    Project   = "CrownCorridor"
  }
}
