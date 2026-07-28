################################################################################
# RDS Instance Outputs
################################################################################

output "db_instance_id" {
  description = "ID of the RDS PostgreSQL instance"
  value       = aws_db_instance.main.id
}

output "db_instance_arn" {
  description = "ARN of the RDS PostgreSQL instance"
  value       = aws_db_instance.main.arn
}

output "db_instance_endpoint" {
  description = "Connection endpoint for RDS PostgreSQL"
  value       = aws_db_instance.main.endpoint
}

output "db_address" {
  description = "Database server hostname"
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "Database connection port"
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

################################################################################
# Database Authentication
################################################################################

output "db_username" {
  description = "Database master username"
  value       = aws_db_instance.main.username
}

################################################################################
# Database Configuration
################################################################################

output "parameter_group_name" {
  description = "PostgreSQL parameter group attached to RDS"
  value       = aws_db_parameter_group.postgis.name
}

################################################################################
# Security Outputs
################################################################################

output "db_security_group_ids" {
  description = "Security groups attached to RDS"
  value       = aws_db_instance.main.vpc_security_group_ids
}

################################################################################
# Secrets
#
# Password intentionally not exposed.
# Retrieve credentials through AWS Secrets Manager.
################################################################################

output "db_password" {
  description = "Deprecated. Database password is stored securely in Secrets Manager."
  value       = null
  sensitive   = true
}
