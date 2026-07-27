output "sns_topic_arn" {
  description = "ARN of the SNS Alerts Topic"
  value       = aws_sns_topic.alerts.arn
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge Weekly ETL Pipeline Cron Rule"
  value       = aws_cloudwatch_event_rule.weekly_etl.arn
}

output "eventbridge_rule_name" {
  description = "Name of the EventBridge Weekly ETL Pipeline Cron Rule"
  value       = aws_cloudwatch_event_rule.weekly_etl.name
}
