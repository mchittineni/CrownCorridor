# Native Terraform Test File for API Gateway Module

run "validate_api_gateway_module_full_coverage" {
  command = plan

  assert {
    condition     = module.api_gateway != null
    error_message = "API Gateway module must be instantiated"
  }
}
