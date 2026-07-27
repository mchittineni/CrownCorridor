output "s3_bucket_name" {
  description = "Name of the S3 static web UI bucket"
  value       = aws_s3_bucket.web_ui.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 static web UI bucket"
  value       = aws_s3_bucket.web_ui.arn
}

output "cloudfront_distribution_id" {
  description = "ID of CloudFront distribution"
  value       = aws_cloudfront_distribution.cdn.id
}

output "cloudfront_domain_name" {
  description = "Domain name of CloudFront distribution"
  value       = aws_cloudfront_distribution.cdn.domain_name
}
