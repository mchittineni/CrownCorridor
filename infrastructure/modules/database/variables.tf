################################################################################
# General Configuration
################################################################################

variable "environment" {
  description = "Execution environment (dev, staging, prod)"
  type        = string

  validation {
    condition = contains(
      ["dev", "staging", "prod"],
      var.environment
    )

    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "app_name" {
  description = "Name of the application"
  type        = string
}

################################################################################
# Networking
################################################################################

variable "db_subnet_group_name" {
  description = "RDS DB subnet group name"
  type        = string
}

variable "rds_sg_id" {
  description = "Security group ID attached to RDS PostgreSQL"
  type        = string
}

################################################################################
# Encryption
################################################################################

variable "kms_key_arn" {
  description = "Customer managed KMS key ARN used for RDS encryption"
  type        = string
}

################################################################################
# Database Configuration
################################################################################

variable "db_name" {
  description = "Initial PostgreSQL database name"
  type        = string
  default     = "iacsecbench_db"
}

variable "db_username" {
  description = "Master username for PostgreSQL"
  type        = string
  default     = "dbadmin"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]*$", var.db_username))
    error_message = "Database username must contain only letters, numbers and underscores."
  }
}

variable "engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15"
}

################################################################################
# Instance Configuration
################################################################################

variable "instance_class" {
  description = "RDS PostgreSQL instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "allocated_storage" {
  description = "Initial allocated storage size in GB"
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum storage autoscaling limit in GB"
  type        = number
  default     = 100
}

################################################################################
# High Availability
################################################################################

variable "multi_az" {
  description = "Enable Multi-AZ deployment for high availability"
  type        = bool
  default     = true
}

variable "deletion_protection" {
  description = "Enable RDS deletion protection"
  type        = bool
  default     = true
}

################################################################################
# Backup Configuration
################################################################################

variable "backup_retention_period" {
  description = "Number of days automated backups are retained"
  type        = number
  default     = 30
}

################################################################################
# Monitoring
################################################################################

variable "performance_insights_enabled" {
  description = "Enable RDS Performance Insights"
  type        = bool
  default     = true
}

variable "monitoring_interval" {
  description = "Enhanced monitoring interval in seconds. Set 0 to disable."
  type        = number
  default     = 60
}

variable "rds_monitoring_role_arn" {
  description = "IAM role ARN required for enhanced RDS monitoring"
  type        = string
  default     = ""
}

################################################################################
# Deployment Behaviour
################################################################################

variable "apply_immediately" {
  description = "Apply database modifications immediately"
  type        = bool
  default     = false
}

################################################################################
# Tags
################################################################################

variable "tags" {
  description = "Common resource tags"
  type        = map(string)
  default     = {}
}
