output "db_instance_id" {
  description = "ID of the RDS DB Instance"
  value       = aws_db_instance.main.id
}

output "db_instance_endpoint" {
  description = "Connection endpoint for RDS PostgreSQL"
  value       = aws_db_instance.main.endpoint
}

output "db_address" {
  description = "Database server host address"
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "Database port"
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "db_username" {
  description = "Database master username"
  value       = aws_db_instance.main.username
}

output "db_password" {
  description = "Database master password (sensitive)"
  value       = random_password.db_password.result
  sensitive   = true
}
