resource "aws_apigatewayv2_api" "health_api" {
  name          = var.api_name
  protocol_type = "HTTP"

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.health_api.id
  name        = "$default"
  auto_deploy = true

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id             = aws_apigatewayv2_api.health_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = var.lambda_invoke_arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "health" {
  api_id    = aws_apigatewayv2_api.health_api.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "health_post" {
  api_id    = aws_apigatewayv2_api.health_api.id
  route_key = "POST /health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}
