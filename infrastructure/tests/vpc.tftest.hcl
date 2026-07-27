# Native Terraform Test File for VPC Module

run "validate_vpc_module_full_coverage" {
  command = plan

  assert {
    condition     = module.vpc.vpc_cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR block must be 10.0.0.0/16"
  }

  assert {
    condition     = length(module.vpc.public_subnet_ids) == 2
    error_message = "Public subnets must be provisioned across 2 Availability Zones"
  }

  assert {
    condition     = length(module.vpc.private_subnet_ids) == 2
    error_message = "Private compute subnets must be provisioned across 2 Availability Zones"
  }

  assert {
    condition     = length(module.vpc.database_subnet_ids) == 2
    error_message = "Database subnets must be provisioned across 2 Availability Zones"
  }

  assert {
    condition     = module.vpc.db_subnet_group_name == "crowncorridor-dev-db-subnet-group"
    error_message = "DB subnet group name must match dev naming convention"
  }
}
