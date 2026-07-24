# AWS WAF Web ACL (CLOUDFRONT Scope)
resource "aws_wafv2_web_acl" "main" {
  name        = "${var.app_name}-${var.environment}-web-acl"
  description = "WAF Web ACL for Crown Corridor (OWASP Top 10, IP Reputation, Rate Limiting)"
  scope       = "CLOUDFRONT"

  default_action {
    allow {}
  }

  # 1. AWS Managed Common Rule Set (OWASP Top 10)
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 10

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-${var.environment}-common-rules"
      sampled_requests_enabled   = true
    }
  }

  # 2. Known Bad Inputs Rule Set
  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 20

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-${var.environment}-bad-inputs"
      sampled_requests_enabled   = true
    }
  }

  # 3. Amazon IP Reputation List
  rule {
    name     = "AWSManagedRulesAmazonIpReputationList"
    priority = 30

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-${var.environment}-ip-reputation"
      sampled_requests_enabled   = true
    }
  }

  # 4. Custom Rate Limiting Rule
  rule {
    name     = "IPRateLimitingRule"
    priority = 40

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = var.rate_limit_threshold
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-${var.environment}-rate-limit"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.app_name}-${var.environment}-waf-acl"
    sampled_requests_enabled   = true
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-waf-acl"
      Environment = var.environment
    }
  )
}
