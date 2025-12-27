output "function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.health_check.function_name
}

output "function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.health_check.arn
}

output "invoke_arn" {
  description = "Invoke ARN of the Lambda function"
  value       = aws_lambda_function.health_check.invoke_arn
}