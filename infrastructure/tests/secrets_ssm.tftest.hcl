# Native Terraform Test File for Secrets & SSM Module

run "validate_secrets_ssm_module_full_coverage" {
  command = plan

  assert {
    condition     = module.secrets_ssm.ssm_env_param_name == "/crowncorridor/dev/ENVIRONMENT"
    error_message = "SSM environment parameter name must match default dev path"
  }
}
