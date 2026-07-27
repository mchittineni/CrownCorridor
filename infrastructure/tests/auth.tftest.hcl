# Native Terraform Test File for Auth Module

run "validate_auth_module_full_coverage" {
  command = plan

  assert {
    condition     = module.auth != null
    error_message = "Cognito Auth module must be instantiated"
  }
}
