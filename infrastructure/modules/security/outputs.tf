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
  description = "ID of API Gateway / ALB Security Group"
  value       = aws_security_group.alb.id
}

output "fastapi_sg_id" {
  description = "ID of FastAPI Security Group"
  value       = aws_security_group.fastapi.id
}

output "typesense_sg_id" {
  description = "ID of Typesense Security Group"
  value       = aws_security_group.typesense.id
}

output "efs_sg_id" {
  description = "ID of EFS Storage Security Group"
  value       = aws_security_group.efs.id
}

output "rds_sg_id" {
  description = "ID of RDS PostgreSQL Security Group"
  value       = aws_security_group.rds.id
}

output "guardduty_detector_id" {
  description = "ID of AWS GuardDuty Detector"
  value       = aws_guardduty_detector.main.id
}

output "guardduty_enabled" {
  description = "GuardDuty enabled status"
  value       = aws_guardduty_detector.main.enable
}

output "securityhub_enabled" {
  description = "Security Hub enabled account ID"
  value       = aws_securityhub_account.main.id
}

output "cloudtrail_bucket_name" {
  description = "CloudTrail audit log bucket name"
  value       = aws_s3_bucket.cloudtrail.id
}

output "cloudtrail_topic_arn" {
  description = "SNS topic ARN used by CloudTrail notifications"
  value       = aws_sns_topic.cloudtrail.arn
}
