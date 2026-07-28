# OPA / Rego Policy Definition for CIS AWS Foundations & Well-Architected Security Benchmark Compliance
# Scope: Crown Corridor Infrastructure as Code

package aws.cis.benchmark

import future.keywords.contains
import future.keywords.if
import future.keywords.in

############################################
# S3 Security Controls
# CIS AWS 2.1.x
############################################

deny contains msg if {
  some bucket in input.resource_changes
  bucket.type == "aws_s3_bucket"
  
  # Check if a public access block exists for this bucket or globally in the plan
  not has_public_access_block(bucket)

  msg := sprintf("S3 bucket %s does not have Public Access Block enabled", [bucket.address])
}

has_public_access_block(bucket) if {
  some pab in input.resource_changes
  pab.type == "aws_s3_bucket_public_access_block"
}

deny contains msg if {
  some encryption in input.resource_changes
  encryption.type == "aws_s3_bucket_server_side_encryption_configuration"

  encryption.change.after.rule[_].apply_server_side_encryption_by_default.sse_algorithm != "aws:kms"

  msg := sprintf("S3 bucket %s is not encrypted using KMS", [encryption.address])
}

############################################
# RDS Security
# CIS AWS 2.3
############################################

deny contains msg if {
  some db in input.resource_changes
  db.type == "aws_db_instance"

  db.change.after.publicly_accessible == true

  msg := sprintf("RDS instance %s is publicly accessible", [db.address])
}

deny contains msg if {
  some db in input.resource_changes
  db.type == "aws_db_instance"

  db.change.after.storage_encrypted != true

  msg := sprintf("RDS instance %s does not use encryption", [db.address])
}

############################################
# CloudTrail Security
# CIS AWS 3.x
############################################

deny contains msg if {
  some trail in input.resource_changes
  trail.type == "aws_cloudtrail"

  trail.change.after.enable_log_file_validation != true

  msg := sprintf("CloudTrail %s does not enable log validation", [trail.address])
}

deny contains msg if {
  some trail in input.resource_changes
  trail.type == "aws_cloudtrail"

  trail.change.after.is_multi_region_trail != true

  msg := sprintf("CloudTrail %s is not multi-region", [trail.address])
}

############################################
# VPC Flow Logs
############################################

deny contains msg if {
  flow_logs := [rc | rc := input.resource_changes[_]; rc.type == "aws_flow_log"]
  count(flow_logs) == 0

  msg := "VPC Flow Logs are not enabled"
}

############################################
# ALB Security
############################################

deny contains msg if {
  some alb in input.resource_changes
  alb.type == "aws_lb"

  alb.change.after.drop_invalid_header_fields != true

  msg := sprintf("ALB %s does not drop invalid headers", [alb.address])
}

############################################
# ECR Security
############################################

deny contains msg if {
  some repo in input.resource_changes
  repo.type == "aws_ecr_repository"

  repo.change.after.image_scanning_configuration[0].scan_on_push != true

  msg := sprintf("ECR repository %s does not enable scan-on-push", [repo.address])
}

############################################
# Security Groups
# CIS AWS 5.1 / 5.2
############################################

deny contains msg if {
  some sg in input.resource_changes
  sg.type == "aws_security_group"

  some ingress in sg.change.after.ingress
  "0.0.0.0/0" in ingress.cidr_blocks
  ingress.from_port <= 22
  ingress.to_port >= 22

  msg := sprintf("Security Group %s exposes SSH port 22", [sg.address])
}

deny contains msg if {
  some sg in input.resource_changes
  sg.type == "aws_security_group"

  some ingress in sg.change.after.ingress
  "0.0.0.0/0" in ingress.cidr_blocks
  ingress.from_port <= 3389
  ingress.to_port >= 3389

  msg := sprintf("Security Group %s exposes RDP port 3389", [sg.address])
}

############################################
# CloudFront HTTPS
############################################

deny contains msg if {
  some cf in input.resource_changes
  cf.type == "aws_cloudfront_distribution"

  cf.change.after.default_cache_behavior[0].viewer_protocol_policy != "redirect-to-https"

  msg := sprintf("CloudFront distribution %s does not enforce HTTPS", [cf.address])
}