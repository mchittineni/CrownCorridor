# SNS Topic for System & Security Alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.app_name}-${var.environment}-alerts"

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-alerts"
      Environment = var.environment
    }
  )
}

resource "aws_sns_topic_subscription" "email_alerts" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# EventBridge Weekly ETL Pipeline Cron Rule
resource "aws_cloudwatch_event_rule" "weekly_etl" {
  name                = "${var.app_name}-${var.environment}-weekly-etl-cron"
  description         = "Triggers SRO data fetcher and Typesense index update pipeline every Sunday"
  schedule_expression = var.cron_expression

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-weekly-etl-cron"
      Environment = var.environment
    }
  )
}

# EventBridge Target forwarding to SNS Alerts (and optionally ECS Task Runner)
resource "aws_cloudwatch_event_target" "sns_notification" {
  rule      = aws_cloudwatch_event_rule.weekly_etl.name
  target_id = "SendSNSNotification"
  arn       = aws_sns_topic.alerts.arn
}

resource "aws_sns_topic_policy" "eventbridge_publish" {
  arn = aws_sns_topic.alerts.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowEventBridgePublish"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action   = "sns:Publish"
        Resource = aws_sns_topic.alerts.arn
      }
    ]
  })
}
