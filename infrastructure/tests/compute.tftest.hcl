# Native Terraform Test File for Compute Module

run "validate_compute_module_full_coverage" {
  command = plan

  assert {
    condition     = module.compute.cluster_name == "iacsecbench-dev-cluster"
    error_message = "ECS cluster name must match dev naming convention"
  }

  assert {
    condition     = module.compute.typesense_endpoint == "typesense.iacsecbench.internal:8108"
    error_message = "Typesense service discovery endpoint must match iacsecbench.internal:8108"
  }
}
