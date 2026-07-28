################################################################################
# CDN Module - CloudFront + Private S3 Static Website Hosting
#
# Architecture:
#
# Users
#   |
#   v
# CloudFront Distribution
#   |
#   +--> Primary S3 Bucket (OAC protected)
#   |
#   +--> Secondary S3 Bucket (Failover / DR)
#
# Security:
# - S3 bucket is private
# - CloudFront uses Origin Access Control (OAC)
# - TLS enforced
# - KMS encryption enabled
# - Security headers enabled
# - WAF integration supported
################################################################################

data "aws_region" "current" {}

################################################################################
# Static Website S3 Bucket
################################################################################

resource "aws_s3_bucket" "web_ui" {

  bucket = "${var.app_name}-${var.environment}-web-ui"

  # Allow deletion only in development environments
  force_destroy = var.environment == "dev"

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-web-ui"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

################################################################################
# Enable S3 Versioning
################################################################################

resource "aws_s3_bucket_versioning" "web_ui" {

  bucket = aws_s3_bucket.web_ui.id

  versioning_configuration {
    status = "Enabled"
  }
}

################################################################################
# Enable S3 Encryption using Customer Managed KMS Key
################################################################################

resource "aws_s3_bucket_server_side_encryption_configuration" "web_ui" {

  bucket = aws_s3_bucket.web_ui.id

  rule {

    apply_server_side_encryption_by_default {

      kms_master_key_id = var.kms_key_arn

      sse_algorithm = "aws:kms"

    }

    bucket_key_enabled = true
  }
}

################################################################################
# Block Public Access
#
# CloudFront accesses S3 using OAC instead of public permissions
################################################################################

resource "aws_s3_bucket_public_access_block" "web_ui" {

  bucket = aws_s3_bucket.web_ui.id

  block_public_acls = true

  block_public_policy = true

  ignore_public_acls = true

  restrict_public_buckets = true
}

################################################################################
# S3 Lifecycle Policy
#
# Removes old versions to control storage cost
################################################################################

resource "aws_s3_bucket_lifecycle_configuration" "web_ui" {
  bucket = aws_s3_bucket.web_ui.id

  rule {
    id     = "cleanup-old-versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

################################################################################
# CloudFront Access Logs Bucket
################################################################################

resource "aws_s3_bucket" "cloudfront_logs" {
  bucket        = "${var.app_name}-${var.environment}-cloudfront-logs"
  force_destroy = var.environment == "dev"

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-cloudfront-logs"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

resource "aws_s3_bucket_versioning" "cloudfront_logs" {
  bucket = aws_s3_bucket.cloudfront_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

################################################################################
# CloudFront Logs Bucket Encryption
################################################################################

resource "aws_s3_bucket_server_side_encryption_configuration" "cloudfront_logs" {

  bucket = aws_s3_bucket.cloudfront_logs.id

  rule {

    apply_server_side_encryption_by_default {

      kms_master_key_id = var.kms_key_arn

      sse_algorithm = "aws:kms"

    }

    bucket_key_enabled = true

  }
}

################################################################################
# CloudFront Logs Bucket Public Access Block
################################################################################

resource "aws_s3_bucket_public_access_block" "cloudfront_logs" {

  bucket = aws_s3_bucket.cloudfront_logs.id

  block_public_acls = true

  block_public_policy = true

  ignore_public_acls = true

  restrict_public_buckets = true
}

################################################################################
# CloudFront Logs Lifecycle
################################################################################

resource "aws_s3_bucket_lifecycle_configuration" "cloudfront_logs" {
  bucket = aws_s3_bucket.cloudfront_logs.id

  rule {
    id     = "expire-cloudfront-logs"
    status = "Enabled"

    expiration {
      days = 365
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

################################################################################
# CloudFront Origin Access Control
################################################################################

resource "aws_cloudfront_origin_access_control" "oac" {

  name = "${var.app_name}-${var.environment}-oac"

  description = "CloudFront access control for private S3 bucket"

  origin_access_control_origin_type = "s3"

  signing_behavior = "always"

  signing_protocol = "sigv4"
}

################################################################################
# CloudFront Security Headers
################################################################################

resource "aws_cloudfront_response_headers_policy" "security" {

  name = "${var.app_name}-${var.environment}-security-policy"

  security_headers_config {

    strict_transport_security {

      override = true

      access_control_max_age_sec = 31536000

      include_subdomains = true

      preload = true

    }

    content_type_options {

      override = true

    }

    xss_protection {

      override = true

      protection = true

      mode_block = true

    }

    referrer_policy {

      override = true

      referrer_policy = "no-referrer"

    }

  }
}

################################################################################
# S3 Bucket Policy
#
# Allows ONLY CloudFront access
# Denies insecure transport
################################################################################

resource "aws_s3_bucket_policy" "web_ui" {

  bucket = aws_s3_bucket.web_ui.id

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Sid = "AllowCloudFrontRead"

        Effect = "Allow"

        Principal = {

          Service = "cloudfront.amazonaws.com"

        }

        Action = "s3:GetObject"

        Resource = "${aws_s3_bucket.web_ui.arn}/*"

        Condition = {

          StringEquals = {

            "AWS:SourceArn" = aws_cloudfront_distribution.cdn.arn

          }

        }

      },

      {

        Sid = "RequireTLS"

        Effect = "Deny"

        Principal = "*"

        Action = "s3:*"

        Resource = [

          aws_s3_bucket.web_ui.arn,

          "${aws_s3_bucket.web_ui.arn}/*"

        ]

        Condition = {

          Bool = {

            "aws:SecureTransport" = false

          }

        }

      }

    ]

  })
}

################################################################################
# CloudFront Distribution
################################################################################

resource "aws_cloudfront_distribution" "cdn" {

  enabled = true

  is_ipv6_enabled = true

  default_root_object = "index.html"

  # Attach AWS WAF if supplied
  web_acl_id = var.waf_web_acl_arn != "" ? var.waf_web_acl_arn : null

  ####################################################################
  # Primary Origin
  ####################################################################

  origin {

    domain_name = aws_s3_bucket.web_ui.bucket_regional_domain_name

    origin_id = "primary-s3"

    origin_access_control_id = aws_cloudfront_origin_access_control.oac.id

  }

  ####################################################################
  # Secondary Origin for Failover
  ####################################################################

  origin {

    domain_name = var.failover_bucket_domain_name

    origin_id = "secondary-s3"

  }

  ####################################################################
  # Origin Failover Group
  ####################################################################

  origin_group {

    origin_id = "s3-origin-group"

    failover_criteria {

      status_codes = [

        500,

        502,

        503,

        504

      ]

    }

    member {

      origin_id = "primary-s3"

    }

    member {

      origin_id = "secondary-s3"

    }

  }

  ####################################################################
  # Cache Behaviour
  ####################################################################

  default_cache_behavior {

    target_origin_id = "s3-origin-group"

    allowed_methods = [

      "GET",

      "HEAD",

      "OPTIONS"

    ]

    cached_methods = [

      "GET",

      "HEAD"

    ]

    viewer_protocol_policy = "redirect-to-https"

    compress = true

    response_headers_policy_id = aws_cloudfront_response_headers_policy.security.id

    forwarded_values {

      query_string = false

      cookies {

        forward = "none"

      }

    }

    min_ttl = 0

    default_ttl = 3600

    max_ttl = 86400

  }

  ####################################################################
  # TLS Configuration
  ####################################################################

  viewer_certificate {

    acm_certificate_arn = var.acm_cert_arn != "" ? var.acm_cert_arn : null

    cloudfront_default_certificate = var.acm_cert_arn == ""

    ssl_support_method = var.acm_cert_arn != "" ? "sni-only" : null

    minimum_protocol_version = "TLSv1.2_2021"

  }

  ####################################################################
  # Geographic Restrictions
  ####################################################################

  restrictions {

    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["IN"]
    }

  }

  ####################################################################
  # Access Logging
  ####################################################################

  logging_config {

    bucket = aws_s3_bucket.cloudfront_logs.bucket_regional_domain_name

    prefix = "cloudfront/"

  }

  tags = merge(

    var.tags,

    {

      Name = "${var.app_name}-${var.environment}-cdn"

      Environment = var.environment

      ManagedBy = "Terraform"

    }

  )

}
