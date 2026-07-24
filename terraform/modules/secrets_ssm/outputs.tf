output "db_secret_arn" {
  description = "ARN of the Secrets Manager DB credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "typesense_key_secret_arn" {
  description = "ARN of the Secrets Manager Typesense API key secret"
  value       = aws_secretsmanager_secret.typesense_api_key.arn
}

output "ssm_env_param_name" {
  description = "Name of the SSM environment parameter"
  value       = aws_ssm_parameter.env.name
}
