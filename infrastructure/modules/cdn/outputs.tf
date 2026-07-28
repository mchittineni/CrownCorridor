################################################################################
# S3 Static Website Bucket Outputs
################################################################################

output "s3_bucket_name" {
  description = "Name of the S3 bucket storing static web UI assets"
  value       = aws_s3_bucket.web_ui.id
}


output "s3_bucket_arn" {
  description = "ARN of the S3 bucket storing static web UI assets"
  value       = aws_s3_bucket.web_ui.arn
}


output "s3_bucket_domain_name" {
  description = "Regional domain name of the S3 web UI bucket"
  value       = aws_s3_bucket.web_ui.bucket_regional_domain_name
}


################################################################################
# CloudFront Outputs
################################################################################

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.cdn.id
}


output "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.cdn.arn
}


output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.cdn.domain_name
}


output "cloudfront_hosted_zone_id" {
  description = "Route53 hosted zone ID for the CloudFront distribution"
  value       = aws_cloudfront_distribution.cdn.hosted_zone_id
}


################################################################################
# CloudFront Security Outputs
################################################################################

output "cloudfront_origin_access_control_id" {
  description = "ID of the CloudFront Origin Access Control"
  value       = aws_cloudfront_origin_access_control.oac.id
}


output "cloudfront_response_headers_policy_id" {
  description = "ID of the CloudFront security response headers policy"
  value       = aws_cloudfront_response_headers_policy.security.id
}


################################################################################
# Logging Outputs
################################################################################

output "cloudfront_logs_bucket_name" {
  description = "Name of the S3 bucket storing CloudFront access logs"
  value       = aws_s3_bucket.cloudfront_logs.id
}


output "cloudfront_logs_bucket_arn" {
  description = "ARN of the CloudFront access logs bucket"
  value       = aws_s3_bucket.cloudfront_logs.arn
}