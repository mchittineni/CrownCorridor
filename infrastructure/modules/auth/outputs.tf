output "user_pool_id" {
  description = "ID of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.id
}


output "user_pool_arn" {
  description = "ARN of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.arn
}


output "user_pool_name" {
  description = "Name of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.name
}


output "user_pool_client_id" {
  description = "ID of the Cognito User Pool App Client"
  value       = aws_cognito_user_pool_client.client.id
}


output "user_pool_client_name" {
  description = "Name of the Cognito User Pool App Client"
  value       = aws_cognito_user_pool_client.client.name
}


output "user_pool_endpoint" {
  description = "Cognito User Pool endpoint"
  value       = aws_cognito_user_pool.main.endpoint
}


output "issuer_url" {
  description = "OIDC issuer URL used for JWT validation"
  value       = "https://${aws_cognito_user_pool.main.endpoint}"
}


output "cognito_domain" {
  description = "Cognito Hosted UI domain"
  value       = aws_cognito_user_pool_domain.domain.domain
}


output "cognito_domain_url" {
  description = "Full Cognito Hosted UI domain URL"
  value       = "https://${aws_cognito_user_pool_domain.domain.domain}.auth.${data.aws_region.current.region}.amazoncognito.com"
}