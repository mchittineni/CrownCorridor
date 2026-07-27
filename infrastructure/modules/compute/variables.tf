variable "environment" {
  description = "Execution environment"
  type        = string
}

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public Subnet IDs for ALB"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private Subnet IDs for ECS Tasks"
  type        = list(string)
}

variable "ecs_execution_role_arn" {
  description = "ECS Execution Role ARN"
  type        = string
}

variable "ecs_task_role_arn" {
  description = "ECS Task Role ARN"
  type        = string
}

variable "fastapi_sg_id" {
  description = "FastAPI Security Group ID"
  type        = string
}

variable "typesense_sg_id" {
  description = "Typesense Security Group ID"
  type        = string
}

variable "efs_sg_id" {
  description = "EFS Security Group ID"
  type        = string
}

variable "typesense_api_key_secret_arn" {
  description = "Secrets Manager ARN for Typesense API Key"
  type        = string
}

variable "db_secret_arn" {
  description = "Secrets Manager ARN for RDS DB credentials"
  type        = string
}

variable "aws_region" {
  description = "AWS region for CloudWatch log groups"
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
