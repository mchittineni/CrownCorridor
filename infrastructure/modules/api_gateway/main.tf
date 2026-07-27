data "aws_region" "current" {}

# Amazon API Gateway HTTP API
resource "aws_apigatewayv2_api" "main" {
  name          = "${var.app_name}-${var.environment}-api-gateway"
  protocol_type = "HTTP"

  cors_configuration {
    allow_credentials = true
    allow_headers     = ["Authorization", "Content-Type", "X-Api-Key", "X-Amz-Date", "X-Amz-Security-Token"]
    allow_methods     = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_origins     = ["*"]
    max_age           = 3600
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-apigw"
      Environment = var.environment
    }
  )
}

# Cognito JWT Authorizer
resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.main.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "cognito-jwt-authorizer"

  jwt_configuration {
    audience = [var.cognito_client_id]
    issuer   = "https://cognito-idp.${data.aws_region.current.region}.amazonaws.com/${var.cognito_user_pool_id}"
  }
}

# Integration with HTTP Backend
resource "aws_apigatewayv2_integration" "backend" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "HTTP_PROXY"

  integration_uri    = var.backend_integration_uri
  integration_method = "ANY"
  connection_type    = "INTERNET"
}

# Public Health Check Route (No Auth required)
resource "aws_apigatewayv2_route" "health" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.backend.id}"
}

# Protected API Routes (Cognito JWT Auth required)
resource "aws_apigatewayv2_route" "api_proxy" {
  api_id             = aws_apigatewayv2_api.main.id
  route_key          = "ANY /api/v1/{proxy+}"
  target             = "integrations/${aws_apigatewayv2_integration.backend.id}"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
  authorization_type = "JWT"
}

# API Gateway Stage with Throttling Controls
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = var.throttling_burst_limit
    throttling_rate_limit  = var.throttling_rate_limit
  }

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}
