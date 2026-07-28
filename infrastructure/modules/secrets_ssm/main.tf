################################################################################
# Secrets Manager - Database Credentials
################################################################################

resource "aws_secretsmanager_secret" "db_credentials" {

  name = "${var.app_name}/${var.environment}/database"

  description = "Encrypted PostgreSQL database credentials for ${var.app_name}"

  kms_key_id = var.kms_key_arn

  recovery_window_in_days = 7

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-db-credentials"
      Environment = var.environment
    }
  )
}

resource "aws_secretsmanager_secret_version" "db_credentials" {

  secret_id = aws_secretsmanager_secret.db_credentials.id

  secret_string = jsonencode({

    engine = "postgres"

    host = var.db_address

    port = var.db_port

    dbname = var.db_name

    username = var.db_username

    password = var.db_password

  })
}

################################################################################
# Database Credential Rotation
################################################################################

resource "aws_secretsmanager_secret_rotation" "db_credentials" {

  count = var.enable_secret_rotation ? 1 : 0

  secret_id = aws_secretsmanager_secret.db_credentials.id

  rotation_rules {

    automatically_after_days = var.rotation_days

  }

  rotation_lambda_arn = var.db_rotation_lambda_arn

}

################################################################################
# Secrets Manager - Typesense API Key
################################################################################

resource "aws_secretsmanager_secret" "typesense_api_key" {

  name = "${var.app_name}/${var.environment}/typesense"

  description = "Encrypted Typesense API key for ${var.app_name}"

  kms_key_id = var.kms_key_arn

  recovery_window_in_days = 7

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-typesense-key"
      Environment = var.environment
    }
  )
}

resource "aws_secretsmanager_secret_version" "typesense_api_key" {

  secret_id = aws_secretsmanager_secret.typesense_api_key.id

  secret_string = var.typesense_api_key

}

################################################################################
# SSM Parameter Store
################################################################################

resource "aws_ssm_parameter" "env" {

  name = "/${var.app_name}/${var.environment}/ENVIRONMENT"

  type = "SecureString"

  value = var.environment

  key_id = var.kms_key_arn

  tags = var.tags
}

resource "aws_ssm_parameter" "supported_states" {

  name = "/${var.app_name}/${var.environment}/SUPPORTED_STATES"

  type = "SecureString"

  value = "AP,TS"

  key_id = var.kms_key_arn

  tags = var.tags
}

resource "aws_ssm_parameter" "zero_pii_enforced" {

  name = "/${var.app_name}/${var.environment}/ZERO_PII_ENFORCED"

  type = "SecureString"

  value = "true"

  key_id = var.kms_key_arn

  tags = var.tags
}
