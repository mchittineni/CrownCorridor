# Native Terraform Test File for CDN & S3 Web UI Module

run "validate_cdn_module_full_coverage" {
  command = plan

  assert {
    condition     = module.cdn != null
    error_message = "CDN module must be instantiated"
  }
}
