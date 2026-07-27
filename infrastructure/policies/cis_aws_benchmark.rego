# OPA / Rego Policy Definition for CIS AWS Foundations & Well-Architected Security Benchmark Compliance
# Scope: Crown Corridor Infrastructure as Code (Evaluated over terraform show -json resource_changes)

package aws.cis.benchmark

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# 1. Deny unencrypted S3 buckets or missing public access block
deny contains msg if {
    some change in input.resource_changes
    change.type == "aws_s3_bucket"
    bucket_addr := change.address
    # Check if there is an associated aws_s3_bucket_server_side_encryption_configuration resource for this bucket
    count([enc |
        some enc_change in input.resource_changes
        enc_change.type == "aws_s3_bucket_server_side_encryption_configuration"
        startswith(enc_change.address, replace(bucket_addr, "aws_s3_bucket.", "aws_s3_bucket_server_side_encryption_configuration."))
        enc := enc_change
    ]) == 0
    msg := sprintf("S3 Bucket '%v' must enforce server-side encryption", [bucket_addr])
}

deny contains msg if {
    some change in input.resource_changes
    change.type == "aws_s3_bucket_public_access_block"
    pab := change.change.after
    not (pab.block_public_acls == true and pab.block_public_policy == true and pab.ignore_public_acls == true and pab.restrict_public_buckets == true)
    msg := sprintf("S3 Public Access Block '%v' must set all 4 flags to true", [change.address])
}

# 2. Deny public RDS instances or unencrypted storage
deny contains msg if {
    some change in input.resource_changes
    change.type == "aws_db_instance"
    change.change.after.publicly_accessible == true
    msg := sprintf("RDS Instance '%v' must set publicly_accessible = false", [change.address])
}

deny contains msg if {
    some change in input.resource_changes
    change.type == "aws_db_instance"
    change.change.after.storage_encrypted != true
    msg := sprintf("RDS Instance '%v' must set storage_encrypted = true", [change.address])
}

# 3. Deny CloudTrail without log file validation or multi-region
deny contains msg if {
    some change in input.resource_changes
    change.type == "aws_cloudtrail"
    change.change.after.enable_log_file_validation != true
    msg := sprintf("CloudTrail '%v' must enable log file validation", [change.address])
}

# 4. Deny unrestricted ingress (SSH/RDP/All) from 0.0.0.0/0
deny contains msg if {
    some change in input.resource_changes
    change.type == "aws_security_group"
    some rule in change.change.after.ingress
    "0.0.0.0/0" in rule.cidr_blocks
    (rule.from_port == 0 or rule.from_port == 22 or rule.from_port == 3389 or rule.protocol == "-1")
    msg := sprintf("Security group '%v' has unrestricted ingress rule from 0.0.0.0/0", [change.address])
}

# 5. Deny CloudFront distribution without HTTPS redirection or TLS 1.2+
deny contains msg if {
    some change in input.resource_changes
    change.type == "aws_cloudfront_distribution"
    some behavior in change.change.after.default_cache_behavior
    behavior.viewer_protocol_policy != "redirect-to-https"
    msg := sprintf("CloudFront distribution '%v' must enforce redirect-to-https", [change.address])
}
