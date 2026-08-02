variable "name_prefix" {
  type        = string
  default     = "iacsecbench"
  description = "Prefix applied to generated resource names."

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.name_prefix))
    error_message = "name_prefix must contain only lowercase letters, digits and hyphens."
  }
}

variable "environment" {
  type        = string
  default     = "benchmark"
  description = "Deployment environment label."
}
