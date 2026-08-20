# Native Terraform Test File for Events & Alerting Module

run "validate_events_alerting_module_full_coverage" {
  command = plan

  assert {
    condition     = module.events_alerting.eventbridge_rule_name == "iacsecbench-dev-weekly-etl-cron"
    error_message = "EventBridge cron rule name must match default dev convention"
  }
}
