variable "environment" {
  description = "Execution environment"
  type        = string
}

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "db_subnet_group_name" {
  description = "RDS DB Subnet Group Name"
  type        = string
}

variable "rds_sg_id" {
  description = "RDS Security Group ID"
  type        = string
}

variable "kms_key_arn" {
  description = "KMS Key ARN for DB encryption"
  type        = string
}

variable "db_name" {
  description = "Initial database name"
  type        = string
  default     = "crowncorridor_db"
}

variable "db_username" {
  description = "Master username for RDS PostgreSQL"
  type        = string
  default     = "dbadmin"
}

variable "instance_class" {
  description = "RDS DB Instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
