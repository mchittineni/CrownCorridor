################################################################################
# SNS Topic - Security & System Alerts
################################################################################

resource "aws_sns_topic" "alerts" {

  name = "${var.app_name}-${var.environment}-alerts"

  # Customer managed KMS encryption
  # Fixes CKV_AWS_26
  kms_master_key_id = var.kms_key_arn

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-alerts"
      Environment = var.environment
    }
  )
}

################################################################################
# SNS Email Subscription
################################################################################

resource "aws_sns_topic_subscription" "email_alerts" {

  count = var.alert_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alerts.arn

  protocol = "email"

  endpoint = var.alert_email
}

################################################################################
# EventBridge Rule - Weekly ETL Trigger
################################################################################

resource "aws_cloudwatch_event_rule" "weekly_etl" {

  name = "${var.app_name}-${var.environment}-weekly-etl-cron"

  description = <<EOF
Triggers SRO data fetcher and Typesense indexing pipeline weekly.
EOF

  schedule_expression = var.cron_expression

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-weekly-etl-cron"
      Environment = var.environment
    }
  )
}

################################################################################
# EventBridge -> SNS Target
################################################################################

resource "aws_cloudwatch_event_target" "sns_notification" {

  rule = aws_cloudwatch_event_rule.weekly_etl.name

  target_id = "SendSNSNotification"

  arn = aws_sns_topic.alerts.arn

  retry_policy {

    maximum_retry_attempts       = 3
    maximum_event_age_in_seconds = 3600

  }
}

################################################################################
# Allow EventBridge to Publish to SNS
################################################################################

resource "aws_sns_topic_policy" "eventbridge_publish" {

  arn = aws_sns_topic.alerts.arn

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      # Enforce HTTPS only
      {
        Sid = "DenyHTTP"

        Effect = "Deny"

        Principal = "*"

        Action = [
          "sns:Publish"
        ]

        Resource = aws_sns_topic.alerts.arn

        Condition = {

          Bool = {

            "aws:SecureTransport" = "false"

          }

        }
      },

      # EventBridge publish permission
      {
        Sid = "AllowEventBridgePublish"

        Effect = "Allow"

        Principal = {

          Service = "events.amazonaws.com"

        }

        Action = [
          "sns:Publish"
        ]

        Resource = aws_sns_topic.alerts.arn

      }

    ]

  })
}

################################################################################
# SNS Data Protection Policy
# Protects against accidental sensitive data publishing
################################################################################

resource "aws_sns_topic_data_protection_policy" "alerts" {

  arn = aws_sns_topic.alerts.arn

  policy = jsonencode({

    Description = "SNS data protection policy"

    Version = "2021-06-01"

    Statement = [

      {

        Sid = "DenySensitiveInformation"

        DataDirection = "Outbound"

        Principal = [
          "*"
        ]

        DataIdentifier = [

          "arn:aws:sns:data-identifier/EmailAddress",

          "arn:aws:sns:data-identifier/CreditCardNumber"

        ]

        Operation = {

          Deny = {}

        }

      }

    ]

  })
}
