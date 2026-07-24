variable "environment" {
  description = "Execution environment"
  type        = string
}

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "cron_expression" {
  description = "EventBridge cron expression for weekly ETL pipeline execution"
  type        = string
  default     = "cron(0 2 ? * SUN *)" # Every Sunday at 02:00 AM UTC
}

variable "alert_email" {
  description = "Optional alert subscriber email for SNS notification topic"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
