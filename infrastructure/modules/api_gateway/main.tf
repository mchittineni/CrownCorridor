data "aws_region" "current" {}

################################################################################
# API Gateway HTTP API
################################################################################

resource "aws_apigatewayv2_api" "main" {
  name          = "${var.app_name}-${var.environment}-api-gateway"
  description   = "HTTP API for ${var.app_name}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_credentials = false
    allow_headers = [
      "Authorization",
      "Content-Type",
      "X-Api-Key",
      "X-Amz-Date",
      "X-Amz-Security-Token"
    ]

    allow_methods = [
      "GET",
      "POST",
      "PUT",
      "DELETE",
      "OPTIONS"
    ]

    # Configure this variable per environment
    allow_origins = var.allowed_origins

    expose_headers = [
      "Content-Length",
      "Content-Type"
    ]

    max_age = 3600
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-apigw"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

################################################################################
# Cognito JWT Authorizer
################################################################################

resource "aws_apigatewayv2_authorizer" "cognito" {

  api_id = aws_apigatewayv2_api.main.id

  name             = "cognito-jwt-authorizer"
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]

  jwt_configuration {
    audience = [var.cognito_client_id]
    issuer   = "https://cognito-idp.${data.aws_region.current.region}.amazonaws.com/${var.cognito_user_pool_id}"
  }
}

################################################################################
# Backend Integration
################################################################################

resource "aws_apigatewayv2_integration" "backend" {

  api_id = aws_apigatewayv2_api.main.id

  integration_type = "HTTP_PROXY"

  integration_uri    = var.backend_integration_uri
  integration_method = "ANY"
  connection_type    = "INTERNET"

  timeout_milliseconds = 30000
}

################################################################################
# CloudWatch Log Group
################################################################################

resource "aws_cloudwatch_log_group" "apigw_access" {

  name              = "/aws/apigateway/${var.app_name}-${var.environment}"
  retention_in_days = 365

  kms_key_id = var.kms_key_arn

  tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

################################################################################
# Public Health Endpoint
################################################################################

resource "aws_apigatewayv2_route" "health" {

  api_id = aws_apigatewayv2_api.main.id

  route_key = "GET /health"

  target = "integrations/${aws_apigatewayv2_integration.backend.id}"

  authorization_type = "NONE"
}

################################################################################
# Protected API
################################################################################

resource "aws_apigatewayv2_route" "api_proxy" {

  api_id = aws_apigatewayv2_api.main.id

  route_key = "ANY /api/v1/{proxy+}"

  target = "integrations/${aws_apigatewayv2_integration.backend.id}"

  authorization_type = "JWT"

  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

################################################################################
# Default Stage
################################################################################

resource "aws_apigatewayv2_stage" "default" {

  api_id = aws_apigatewayv2_api.main.id

  name = "$default"

  auto_deploy = true

  access_log_settings {

    destination_arn = aws_cloudwatch_log_group.apigw_access.arn

    format = jsonencode({
      requestId      = "$context.requestId"
      requestTime    = "$context.requestTime"
      routeKey       = "$context.routeKey"
      httpMethod     = "$context.httpMethod"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      sourceIp       = "$context.identity.sourceIp"
      userAgent      = "$context.identity.userAgent"
      integration    = "$context.integration.status"
      error          = "$context.error.message"
      latency        = "$context.responseLatency"
    })
  }

  default_route_settings {

    throttling_burst_limit = var.throttling_burst_limit
    throttling_rate_limit  = var.throttling_rate_limit

    detailed_metrics_enabled = true
    logging_level            = "INFO"
    data_trace_enabled       = false
  }

  tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}
