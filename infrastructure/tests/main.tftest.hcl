# Master Native Terraform Integration Test Suite

run "verify_root_module_integration" {
  command = plan

  # 1. VPC Outputs
  assert {
    condition     = module.vpc.vpc_cidr_block == "10.0.0.0/16"
    error_message = "Root VPC CIDR block must be 10.0.0.0/16"
  }

  assert {
    condition     = length(module.vpc.public_subnet_ids) == 2
    error_message = "Public subnet count must be 2"
  }

  assert {
    condition     = length(module.vpc.private_subnet_ids) == 2
    error_message = "Private compute subnet count must be 2"
  }

  assert {
    condition     = length(module.vpc.database_subnet_ids) == 2
    error_message = "Private database subnet count must be 2"
  }

  # 2. Database Outputs
  assert {
    condition     = module.database.db_name == "iacsecbench_db"
    error_message = "Root RDS Database name must be iacsecbench_db"
  }

  assert {
    condition     = module.database.db_username == "dbadmin"
    error_message = "Root RDS master username must be dbadmin"
  }

  # 3. Compute Outputs
  assert {
    condition     = module.compute.typesense_endpoint == "typesense.iacsecbench.internal:8108"
    error_message = "Typesense service discovery endpoint must match iacsecbench.internal:8108"
  }

  assert {
    condition     = module.compute.cluster_name == "iacsecbench-dev-cluster"
    error_message = "ECS cluster name must match dev naming convention"
  }

  # 4. Secrets & SSM Outputs
  assert {
    condition     = module.secrets_ssm.ssm_env_param_name == "/iacsecbench/dev/ENVIRONMENT"
    error_message = "SSM environment parameter name must match default dev path"
  }

  # 5. Events & Alerting Outputs
  assert {
    condition     = module.events_alerting.eventbridge_rule_name == "iacsecbench-dev-weekly-etl-cron"
    error_message = "EventBridge weekly ETL cron rule name must match dev naming convention"
  }
}
