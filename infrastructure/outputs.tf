##############################################
# Frontend CDN
##############################################

output "cloudfront_web_portal_url" {
  description = "Public HTTPS URL of the static Web UI hosted through CloudFront CDN"
  value       = "https://${module.cdn.cloudfront_domain_name}"
}

output "cloudfront_distribution_id" {
  description = "CloudFront Distribution ID"
  value       = module.cdn.cloudfront_distribution_id
}

##############################################
# API Layer
##############################################

output "api_gateway_endpoint" {
  description = "Public execution endpoint URL for API Gateway HTTP API"
  value       = module.api_gateway.api_gateway_endpoint
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name for FastAPI backend"
  value       = module.compute.alb_dns_name
}

##############################################
# Authentication
##############################################

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID used for authentication"
  value       = module.auth.user_pool_id
}

output "cognito_client_id" {
  description = "Cognito User Pool App Client ID"
  value       = module.auth.user_pool_client_id
}

##############################################
# Container Platform
##############################################

output "ecs_cluster_name" {
  description = "ECS Fargate cluster name"
  value       = module.compute.cluster_name
}

output "ecr_repository_url" {
  description = "Amazon ECR repository URL for FastAPI container images"
  value       = module.compute.ecr_repository_url
}

##############################################
# Database
##############################################

output "rds_endpoint" {
  description = "Private RDS PostgreSQL/PostGIS connection endpoint"
  value       = module.database.db_instance_endpoint
}

output "database_name" {
  description = "Application database name"
  value       = module.database.db_name
}

output "database_username" {
  description = "Database master username"
  value       = module.database.db_username
}

output "database_password" {
  description = "Database master password"
  value       = module.database.db_password
  sensitive   = true
}

##############################################
# Search Service
##############################################

output "typesense_internal_endpoint" {
  description = "Private AWS Cloud Map endpoint for Typesense service discovery"
  value       = module.compute.typesense_endpoint
}

##############################################
# Security & Compliance
##############################################

output "kms_key_arn" {
  description = "AWS KMS Customer Managed Key ARN"
  value       = module.security.kms_key_arn
}

output "waf_web_acl_arn" {
  description = "AWS WAF Web ACL ARN"
  value       = module.waf.web_acl_arn
}

output "guardduty_detector_id" {
  description = "AWS GuardDuty detector ID"
  value       = module.security.guardduty_detector_id
}

##############################################
# Monitoring & Alerting
##############################################

output "sns_alerts_topic_arn" {
  description = "ARN of SNS security and operational alert topic"
  value       = module.events_alerting.sns_topic_arn
}

output "eventbridge_etl_rule_name" {
  description = "EventBridge scheduled ETL pipeline rule name"
  value       = module.events_alerting.eventbridge_rule_name
}
