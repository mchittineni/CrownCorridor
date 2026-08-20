#############################################
# AWS WAFv2 Web ACL - CloudFront Scope
#############################################

resource "aws_wafv2_web_acl" "main" {

  name = "${var.app_name}-${var.environment}-web-acl"

  description = "CloudFront WAF protecting IaCSecBench against OWASP Top 10, malicious IPs, SQL injection and abuse"

  scope = "CLOUDFRONT"

  #############################################
  # Default Action
  #############################################

  default_action {
    allow {}
  }

  #############################################
  # 1. AWS Managed OWASP Common Rules
  #############################################

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

      metric_name = "${var.app_name}-${var.environment}-owasp-common"

      sampled_requests_enabled = true

    }

  }

  #############################################
  # 2. Known Bad Inputs
  #############################################

  rule {

    name     = "AWSManagedRulesKnownBadInputs"
    priority = 20

    override_action {

      none {}

    }

    statement {

      managed_rule_group_statement {

        name = "AWSManagedRulesKnownBadInputsRuleSet"

        vendor_name = "AWS"

      }

    }

    visibility_config {

      cloudwatch_metrics_enabled = true

      metric_name = "${var.app_name}-${var.environment}-bad-inputs"

      sampled_requests_enabled = true

    }

  }

  #############################################
  # 3. Amazon IP Reputation
  #############################################

  rule {

    name = "AWSManagedRulesAmazonIPReputation"

    priority = 30

    override_action {

      none {}

    }

    statement {

      managed_rule_group_statement {

        name = "AWSManagedRulesAmazonIpReputationList"

        vendor_name = "AWS"

      }

    }

    visibility_config {

      cloudwatch_metrics_enabled = true

      metric_name = "${var.app_name}-${var.environment}-ip-reputation"

      sampled_requests_enabled = true

    }

  }

  #############################################
  # 4. SQL Injection Protection
  #############################################

  rule {

    name = "AWSManagedRulesSQLInjection"

    priority = 40

    override_action {

      none {}

    }

    statement {

      managed_rule_group_statement {

        name = "AWSManagedRulesSQLiRuleSet"

        vendor_name = "AWS"

      }

    }

    visibility_config {

      cloudwatch_metrics_enabled = true

      metric_name = "${var.app_name}-${var.environment}-sql-injection"

      sampled_requests_enabled = true

    }

  }

  #############################################
  # 5. Rate Limiting
  #############################################

  rule {

    name = "RateLimitByIP"

    priority = 50

    action {

      block {}

    }

    statement {

      rate_based_statement {

        limit = var.rate_limit_threshold

        aggregate_key_type = "IP"

      }

    }

    visibility_config {

      cloudwatch_metrics_enabled = true

      metric_name = "${var.app_name}-${var.environment}-rate-limit"

      sampled_requests_enabled = true

    }

  }

  #############################################
  # ACL Visibility
  #############################################

  visibility_config {

    cloudwatch_metrics_enabled = true

    metric_name = "${var.app_name}-${var.environment}-waf"

    sampled_requests_enabled = true

  }

  tags = merge(

    var.tags,

    {

      Name = "${var.app_name}-${var.environment}-waf"

      Environment = var.environment

      ManagedBy = "Terraform"

    }

  )

}
