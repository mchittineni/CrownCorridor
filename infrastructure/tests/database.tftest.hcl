# Native Terraform Test File for Database Module

run "validate_database_module_full_coverage" {
  command = plan

  assert {
    condition     = module.database.db_name == "iacsecbench_db"
    error_message = "Initial database name must be iacsecbench_db"
  }

  assert {
    condition     = module.database.db_username == "dbadmin"
    error_message = "Master username must be dbadmin"
  }
}
