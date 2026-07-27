output "api_gateway_id" {
  description = "ID of API Gateway HTTP API"
  value       = aws_apigatewayv2_api.main.id
}

output "api_gateway_endpoint" {
  description = "Execution endpoint of API Gateway HTTP API"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "authorizer_id" {
  description = "ID of Cognito JWT Authorizer"
  value       = aws_apigatewayv2_authorizer.cognito.id
}
