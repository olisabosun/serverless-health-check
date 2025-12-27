output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "${module.api_gateway.api_endpoint}/health"
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = module.dynamodb.table_name
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = module.lambda.function_name
}
