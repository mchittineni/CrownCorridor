################################################################################
# SNS Outputs
################################################################################

output "sns_topic_arn" {
  description = "ARN of the SNS Alerts Topic"
  value       = aws_sns_topic.alerts.arn
}

output "sns_topic_name" {
  description = "Name of the SNS Alerts Topic"
  value       = aws_sns_topic.alerts.name
}

################################################################################
# EventBridge Outputs
################################################################################

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge Weekly ETL Pipeline Cron Rule"
  value       = aws_cloudwatch_event_rule.weekly_etl.arn
}

output "eventbridge_rule_name" {
  description = "Name of the EventBridge Weekly ETL Pipeline Cron Rule"
  value       = aws_cloudwatch_event_rule.weekly_etl.name
}

################################################################################
# Subscription Outputs
################################################################################

output "alert_subscription_arn" {
  description = "ARN of the SNS email subscription (if configured)"
  value = try(
    aws_sns_topic_subscription.email_alerts[0].arn,
    null
  )
}

################################################################################
# Monitoring Integration Outputs
################################################################################

output "weekly_etl_schedule_expression" {
  description = "Schedule expression used by EventBridge ETL trigger"
  value       = aws_cloudwatch_event_rule.weekly_etl.schedule_expression
}
