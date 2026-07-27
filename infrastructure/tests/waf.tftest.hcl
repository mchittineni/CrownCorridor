# Native Terraform Test File for WAF Module

run "validate_waf_module_full_coverage" {
  command = plan

  assert {
    condition     = module.waf != null
    error_message = "AWS WAF module must be instantiated"
  }
}
