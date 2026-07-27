# Random Password for DB Master User
resource "random_password" "db_password" {
  length           = 24
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Parameter Group with PostGIS extensions
resource "aws_db_parameter_group" "postgis" {
  name        = "${var.app_name}-${var.environment}-postgis-pg"
  family      = "postgres15"
  description = "Parameter group for Crown Corridor PostGIS PostgreSQL"

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }

  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-postgis-pg"
      Environment = var.environment
    }
  )
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier                 = "${var.app_name}-${var.environment}-postgres"
  engine                     = "postgres"
  engine_version             = "15"
  auto_minor_version_upgrade = true
  instance_class             = var.instance_class
  allocated_storage          = var.allocated_storage
  max_allocated_storage      = 100
  storage_type               = "gp3"
  storage_encrypted          = true
  kms_key_id                 = var.kms_key_arn

  db_name  = var.db_name
  username = var.db_username
  password = random_password.db_password.result

  db_subnet_group_name   = var.db_subnet_group_name
  vpc_security_group_ids = [var.rds_sg_id]
  parameter_group_name   = aws_db_parameter_group.postgis.name

  multi_az                            = var.multi_az
  publicly_accessible                 = false
  iam_database_authentication_enabled = true
  enabled_cloudwatch_logs_exports     = ["postgresql", "upgrade"]
  skip_final_snapshot                 = var.environment == "dev" ? true : false
  final_snapshot_identifier           = var.environment != "dev" ? "${var.app_name}-${var.environment}-final-snapshot" : null

  backup_retention_period = 7
  deletion_protection     = var.environment == "prod" ? true : false

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-postgres"
      Environment = var.environment
    }
  )
}
