output "api_gateway_id" {
  description = "ID of the API Gateway HTTP API"
  value       = aws_apigatewayv2_api.main.id
}

output "api_gateway_endpoint" {
  description = "Default execution endpoint URL of the API Gateway HTTP API"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "api_gateway_execution_arn" {
  description = "Execution ARN of the API Gateway HTTP API"
  value       = aws_apigatewayv2_api.main.execution_arn
}

output "authorizer_id" {
  description = "ID of the Cognito JWT authorizer"
  value       = aws_apigatewayv2_authorizer.cognito.id
}

output "api_gateway_stage_name" {
  description = "Name of the API Gateway deployment stage"
  value       = aws_apigatewayv2_stage.default.name
}

output "api_gateway_access_log_group_arn" {
  description = "ARN of the CloudWatch Log Group used for API Gateway access logging"
  value       = aws_cloudwatch_log_group.apigw_access.arn
}
