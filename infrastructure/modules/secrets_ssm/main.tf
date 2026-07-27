# Secrets Manager Secret: Database Credentials
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.app_name}/${var.environment}/database"
  description             = "Encrypted database credentials for ${var.app_name}"
  kms_key_id              = var.kms_key_arn
  recovery_window_in_days = 0

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
    engine   = "postgres"
    host     = var.db_address
    port     = var.db_port
    dbname   = var.db_name
    username = var.db_username
    password = var.db_password
  })
}

# Secrets Manager Secret: Typesense API Key
resource "aws_secretsmanager_secret" "typesense_api_key" {
  name                    = "${var.app_name}/${var.environment}/typesense"
  description             = "Encrypted Typesense API Key for ${var.app_name}"
  kms_key_id              = var.kms_key_arn
  recovery_window_in_days = 0

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-typesense-key"
      Environment = var.environment
    }
  )
}

resource "aws_secretsmanager_secret_version" "typesense_api_key" {
  secret_id     = aws_secretsmanager_secret.typesense_api_key.id
  secret_string = var.typesense_api_key
}

# --- AWS SYSTEMS MANAGER (SSM) PARAMETER STORE ---

resource "aws_ssm_parameter" "env" {
  name  = "/${var.app_name}/${var.environment}/ENVIRONMENT"
  type  = "String"
  value = var.environment

  tags = var.tags
}

resource "aws_ssm_parameter" "supported_states" {
  name  = "/${var.app_name}/${var.environment}/SUPPORTED_STATES"
  type  = "StringList"
  value = "AP,TS"

  tags = var.tags
}

resource "aws_ssm_parameter" "zero_pii_enforced" {
  name  = "/${var.app_name}/${var.environment}/ZERO_PII_ENFORCED"
  type  = "String"
  value = "true"

  tags = var.tags
}
