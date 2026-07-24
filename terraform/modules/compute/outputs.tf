output "cluster_id" {
  description = "ID of the ECS Cluster"
  value       = aws_ecs_cluster.main.id
}

output "cluster_name" {
  description = "Name of the ECS Cluster"
  value       = aws_ecs_cluster.main.name
}

output "alb_dns_name" {
  description = "DNS Name of Application Load Balancer"
  value       = aws_lb.alb.dns_name
}

output "alb_arn" {
  description = "ARN of Application Load Balancer"
  value       = aws_lb.alb.arn
}

output "ecr_repository_url" {
  description = "URL of FastAPI ECR Repository"
  value       = aws_ecr_repository.fastapi.repository_url
}

output "typesense_endpoint" {
  description = "Internal service discovery DNS endpoint for Typesense"
  value       = "typesense.${var.app_name}.internal:8108"
}
