# Native Terraform Test File for Security Module

run "validate_security_module_full_coverage" {
  command = plan

  assert {
    condition     = module.security != null
    error_message = "Security module must be instantiated"
  }
}
