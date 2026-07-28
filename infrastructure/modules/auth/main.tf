data "aws_region" "current" {}

################################################################################
# Cognito User Pool
################################################################################

resource "aws_cognito_user_pool" "main" {

  name = "${var.app_name}-${var.environment}-user-pool"

  deletion_protection = "ACTIVE"

  username_attributes = [
    "email"
  ]

  auto_verified_attributes = [
    "email"
  ]

  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  password_policy {

    minimum_length = 14

    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = true

    temporary_password_validity_days = 7
  }

  mfa_configuration = "OPTIONAL"

  software_token_mfa_configuration {

    enabled = true

  }

  account_recovery_setting {

    recovery_mechanism {

      name = "verified_email"

      priority = 1

    }

  }

  user_pool_add_ons {

    advanced_security_mode = "ENFORCED"

  }

  user_pool_tier = "ESSENTIALS"

  user_attribute_update_settings {

    attributes_require_verification_before_update = [
      "email"
    ]

  }

  lambda_config {
    # Add triggers here if required:
    #
    # pre_token_generation = aws_lambda_function.token_trigger.arn
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-user-pool"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )

  lifecycle {

    prevent_destroy = true

  }

}

################################################################################
# Cognito Application Client
################################################################################

resource "aws_cognito_user_pool_client" "client" {

  name = "${var.app_name}-${var.environment}-client"

  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret = false

  explicit_auth_flows = [

    "ALLOW_USER_SRP_AUTH",

    "ALLOW_REFRESH_TOKEN_AUTH"

  ]

  prevent_user_existence_errors = "ENABLED"

  refresh_token_rotation {

    feature = "ENABLED"

  }

  access_token_validity = 60

  id_token_validity = 60

  refresh_token_validity = 30

  token_validity_units {

    access_token = "minutes"

    id_token = "minutes"

    refresh_token = "days"

  }

  supported_identity_providers = [

    "COGNITO"

  ]

  allowed_oauth_flows_user_pool_client = false

  lifecycle {

    prevent_destroy = true

  }

}

################################################################################
# Cognito Hosted UI Domain
################################################################################

resource "aws_cognito_user_pool_domain" "domain" {

  domain = var.cognito_domain_prefix

  user_pool_id = aws_cognito_user_pool.main.id

}
