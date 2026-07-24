output "kms_key_arn" {
  description = "ARN of the AWS KMS Customer Managed Key"
  value       = aws_kms_key.main.arn
}

output "kms_key_id" {
  description = "ID of the AWS KMS Customer Managed Key"
  value       = aws_kms_key.main.key_id
}

output "ecs_execution_role_arn" {
  description = "ARN of the ECS Execution Role"
  value       = aws_iam_role.ecs_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS Task Role"
  value       = aws_iam_role.ecs_task_role.arn
}

output "api_gateway_sg_id" {
  description = "ID of the API Gateway / ALB Security Group"
  value       = aws_security_group.api_gateway.id
}

output "fastapi_sg_id" {
  description = "ID of the FastAPI Microservice Security Group"
  value       = aws_security_group.fastapi.id
}

output "typesense_sg_id" {
  description = "ID of the Typesense Security Group"
  value       = aws_security_group.typesense.id
}

output "efs_sg_id" {
  description = "ID of the EFS Storage Security Group"
  value       = aws_security_group.efs.id
}

output "rds_sg_id" {
  description = "ID of the RDS Database Security Group"
  value       = aws_security_group.rds.id
}

output "guardduty_detector_id" {
  description = "ID of the AWS GuardDuty Detector"
  value       = aws_guardduty_detector.main.id
}
