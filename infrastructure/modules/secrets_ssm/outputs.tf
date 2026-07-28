################################################################################
# AWS Secrets Manager Outputs
################################################################################

output "db_secret_arn" {
  description = "ARN of the AWS Secrets Manager database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "db_secret_id" {
  description = "ID of the AWS Secrets Manager database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.id
}

output "typesense_key_secret_arn" {
  description = "ARN of the AWS Secrets Manager Typesense API key secret"
  value       = aws_secretsmanager_secret.typesense_api_key.arn
}

output "typesense_key_secret_id" {
  description = "ID of the AWS Secrets Manager Typesense API key secret"
  value       = aws_secretsmanager_secret.typesense_api_key.id
}

################################################################################
# AWS Systems Manager Parameter Store Outputs
################################################################################

output "ssm_env_param_name" {
  description = "Name of the SSM SecureString environment parameter"
  value       = aws_ssm_parameter.env.name
}

output "ssm_env_param_arn" {
  description = "ARN of the SSM SecureString environment parameter"
  value       = aws_ssm_parameter.env.arn
}

output "ssm_supported_states_param_name" {
  description = "Name of the SSM supported states parameter"
  value       = aws_ssm_parameter.supported_states.name
}

output "ssm_zero_pii_param_name" {
  description = "Name of the SSM Zero PII enforcement parameter"
  value       = aws_ssm_parameter.zero_pii_enforced.name
}
