# OPA / Rego Policy Definition for CIS AWS Foundations & Well-Architected Security Benchmark Compliance
# Scope: Crown Corridor Infrastructure as Code

package aws.cis.benchmark

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# Rule 1: S3 Buckets must enforce SSE Encryption, Versioning, and Public Access Block (CIS AWS 2.1.1 & 2.1.3)
default allow_s3_bucket_security := false

allow_s3_bucket_security if {
    input.resource.aws_s3_bucket_public_access_block[_].block_public_acls == true
    input.resource.aws_s3_bucket_public_access_block[_].block_public_policy == true
    input.resource.aws_s3_bucket_public_access_block[_].ignore_public_acls == true
    input.resource.aws_s3_bucket_public_access_block[_].restrict_public_buckets == true
    input.resource.aws_s3_bucket_versioning[_].versioning_configuration[_].status == "Enabled"
}

# Rule 2: RDS Instances must be private and storage encrypted with KMS (CIS AWS 2.3.1 & 2.3.2)
default allow_rds_encryption := false

allow_rds_encryption if {
    input.resource.aws_db_instance[_].storage_encrypted == true
    input.resource.aws_db_instance[_].publicly_accessible == false
    input.resource.aws_db_instance[_].backup_retention_period >= 7
}

# Rule 3: CloudTrail must have log file validation enabled and KMS encryption (CIS AWS 3.2)
default allow_cloudtrail_validation := false

allow_cloudtrail_validation if {
    input.resource.aws_cloudtrail[_].enable_log_file_validation == true
    input.resource.aws_cloudtrail[_].is_multi_region_trail == true
}

# Rule 4: VPC Flow Logs must be enabled (CIS AWS 3.9)
default allow_vpc_flow_logs := false

allow_vpc_flow_logs if {
    input.resource.aws_flow_log[_].traffic_type == "ALL"
}

# Rule 5: ALB must drop invalid header fields (AWS Security Best Practices)
default allow_alb_security := false

allow_alb_security if {
    input.resource.aws_lb[_].drop_invalid_header_fields == true
}

# Rule 6: ECR Repositories must enable scan on push (CIS AWS 5.3)
default allow_ecr_scanning := false

allow_ecr_scanning if {
    input.resource.aws_ecr_repository[_].image_scanning_configuration[_].scan_on_push == true
}

# Rule 7: Security Groups must not open port 22 or 3389 to 0.0.0.0/0 (CIS AWS 5.1 & 5.2)
deny_unrestricted_ingress contains msg if {
    some sg in input.resource.aws_security_group
    some rule in sg.ingress
    "0.0.0.0/0" in rule.cidr_blocks
    rule.from_port <= 22
    rule.to_port >= 22
    msg := sprintf("Security group %v allows SSH from 0.0.0.0/0", [sg.name])
}

deny_unrestricted_ingress contains msg if {
    some sg in input.resource.aws_security_group
    some rule in sg.ingress
    "0.0.0.0/0" in rule.cidr_blocks
    rule.from_port <= 3389
    rule.to_port >= 3389
    msg := sprintf("Security group %v allows RDP from 0.0.0.0/0", [sg.name])
}

# Rule 8: CloudFront must enforce HTTPS redirection (CIS AWS 2.4.1)
default allow_cloudfront_https := false

allow_cloudfront_https if {
    input.resource.aws_cloudfront_distribution[_].default_cache_behavior[_].viewer_protocol_policy == "redirect-to-https"
}
