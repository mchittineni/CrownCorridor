################################################################################
# ECS Cluster Outputs
################################################################################

output "cluster_id" {
  description = "ID of the ECS Cluster"
  value       = aws_ecs_cluster.main.id
}


output "cluster_name" {
  description = "Name of the ECS Cluster"
  value       = aws_ecs_cluster.main.name
}


################################################################################
# Application Load Balancer Outputs
################################################################################

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.alb.dns_name
}


output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.alb.arn
}


output "alb_zone_id" {
  description = "Route53 hosted zone ID of the Application Load Balancer"
  value       = aws_lb.alb.zone_id
}


output "alb_target_group_arn" {
  description = "ARN of the FastAPI ALB target group"
  value       = aws_lb_target_group.fastapi.arn
}


################################################################################
# ECR Outputs
################################################################################

output "ecr_repository_url" {
  description = "URL of FastAPI ECR repository"
  value       = aws_ecr_repository.fastapi.repository_url
}


output "ecr_repository_arn" {
  description = "ARN of FastAPI ECR repository"
  value       = aws_ecr_repository.fastapi.arn
}


################################################################################
# ECS Service Outputs
################################################################################

output "fastapi_service_name" {
  description = "Name of FastAPI ECS service"
  value       = aws_ecs_service.fastapi.name
}


output "typesense_service_name" {
  description = "Name of Typesense ECS service"
  value       = aws_ecs_service.typesense.name
}


################################################################################
# Service Discovery Outputs
################################################################################

output "typesense_endpoint" {
  description = "Internal Cloud Map DNS endpoint for Typesense"
  value       = "typesense.${var.app_name}.internal:8108"
}


output "service_discovery_namespace_id" {
  description = "ID of the Cloud Map private DNS namespace"
  value       = aws_service_discovery_private_dns_namespace.internal.id
}


################################################################################
# Storage Outputs
################################################################################

output "typesense_efs_id" {
  description = "ID of the EFS filesystem used by Typesense"
  value       = aws_efs_file_system.typesense.id
}


output "alb_logs_bucket_name" {
  description = "S3 bucket storing ALB access logs"
  value       = aws_s3_bucket.alb_logs.id
}


################################################################################
# Security Outputs
################################################################################

output "fastapi_log_group_name" {
  description = "CloudWatch log group for FastAPI"
  value       = aws_cloudwatch_log_group.fastapi.name
}


output "typesense_log_group_name" {
  description = "CloudWatch log group for Typesense"
  value       = aws_cloudwatch_log_group.typesense.name
}