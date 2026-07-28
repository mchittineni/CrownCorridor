#############################################
# AWS WAF Web ACL Outputs
#############################################

output "web_acl_arn" {
  description = "ARN of the AWS WAFv2 Web ACL"
  value       = aws_wafv2_web_acl.main.arn
}

output "web_acl_id" {
  description = "ID of the AWS WAFv2 Web ACL"
  value       = aws_wafv2_web_acl.main.id
}

output "web_acl_name" {
  description = "Name of the AWS WAFv2 Web ACL"
  value       = aws_wafv2_web_acl.main.name
}
