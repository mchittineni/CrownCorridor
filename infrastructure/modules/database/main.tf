################################################################################
# Generate Database Master Password
#
# Password is generated automatically and stored securely.
################################################################################

resource "random_password" "db_password" {

  length = 24

  special = true

  override_special = "!#$%&*()-_=+[]{}<>:?"

}

################################################################################
# PostgreSQL Parameter Group
#
# Security:
# - Force SSL connections
# - Enable PostgreSQL statistics extension
################################################################################

resource "aws_db_parameter_group" "postgis" {

  name = "${var.app_name}-${var.environment}-postgres15"

  family = "postgres15"

  description = "PostgreSQL 15 parameter group with security hardening"

  parameter {

    name = "shared_preload_libraries"

    value = "pg_stat_statements"

  }

  parameter {

    name = "rds.force_ssl"

    value = "1"

  }

  tags = merge(

    var.tags,

    {

      Name = "${var.app_name}-${var.environment}-postgres-parameters"

      Environment = var.environment

    }

  )

}

################################################################################
# PostgreSQL RDS Instance
################################################################################

resource "aws_db_instance" "main" {

  identifier = "${var.app_name}-${var.environment}-postgres"

  engine = "postgres"

  engine_version = "15"

  instance_class = var.instance_class

  allocated_storage = var.allocated_storage

  max_allocated_storage = 100

  storage_type = "gp3"

  storage_encrypted = true

  kms_key_id = var.kms_key_arn

  db_name = var.db_name

  username = var.db_username

  password = random_password.db_password.result

  manage_master_user_password = false

  db_subnet_group_name = var.db_subnet_group_name

  vpc_security_group_ids = [

    var.rds_sg_id

  ]

  parameter_group_name = aws_db_parameter_group.postgis.name

  ################################################################################
  # Availability & Backup
  ################################################################################

  multi_az = var.multi_az

  publicly_accessible = false

  backup_retention_period = 30

  backup_window = "03:00-04:00"

  maintenance_window = "sun:04:00-sun:05:00"

  copy_tags_to_snapshot = true

  skip_final_snapshot = var.environment == "dev"

  final_snapshot_identifier = var.environment != "dev" ? "${var.app_name}-${var.environment}-final-snapshot" : null

  deletion_protection = true

  ################################################################################
  # Security
  ################################################################################

  iam_database_authentication_enabled = true

  enabled_cloudwatch_logs_exports = [

    "postgresql",

    "upgrade"

  ]

  ################################################################################
  # Monitoring
  ################################################################################

  performance_insights_enabled = true

  performance_insights_kms_key_id = var.kms_key_arn

  monitoring_interval = 60

  monitoring_role_arn = var.rds_monitoring_role_arn != "" ? var.rds_monitoring_role_arn : null

  ################################################################################
  # Maintenance
  ################################################################################

  auto_minor_version_upgrade = true

  apply_immediately = var.environment == "dev"

  tags = merge(

    var.tags,

    {

      Name = "${var.app_name}-${var.environment}-postgres"

      Environment = var.environment

    }

  )

}
