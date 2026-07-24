variable "environment" {
  description = "Execution environment"
  type        = string
}

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "rate_limit_threshold" {
  description = "Max number of requests per 5 minutes per IP address"
  type        = number
  default     = 2000
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
