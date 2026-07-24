output "cloudfront_web_portal_url" {
  description = "Public URL of the static Web UI hosted via CloudFront CDN"
  value       = "https://${module.cdn.cloudfront_domain_name}"
}

output "api_gateway_endpoint" {
  description = "Public execution endpoint for API Gateway HTTP API"
  value       = module.api_gateway.api_gateway_endpoint
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID for Authentication"
  value       = module.auth.user_pool_id
}

output "cognito_client_id" {
  description = "Cognito User Pool Client ID"
  value       = module.auth.user_pool_client_id
}

output "alb_dns_name" {
  description = "FastAPI Backend ALB DNS Name"
  value       = module.compute.alb_dns_name
}

output "ecr_repository_url" {
  description = "FastAPI ECR Container Repository URL"
  value       = module.compute.ecr_repository_url
}

output "rds_endpoint" {
  description = "RDS PostGIS PostgreSQL connection endpoint"
  value       = module.database.db_instance_endpoint
}

output "typesense_internal_endpoint" {
  description = "Private Cloud Map endpoint for Typesense search"
  value       = module.compute.typesense_endpoint
}

output "sns_alerts_topic_arn" {
  description = "ARN of SNS Alert Notification Topic"
  value       = module.events_alerting.sns_topic_arn
}
