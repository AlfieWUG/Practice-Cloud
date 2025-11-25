# =============================================================================
# API Gateway for Agentic Services
# =============================================================================
# Creates HTTP API with routes for all 24 Lambda functions
# Base URL structure: https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/agents/{agent-name}
# =============================================================================

# -----------------------------------------------------------------------------
# API Gateway HTTP API
# -----------------------------------------------------------------------------
resource "aws_apigatewayv2_api" "agents" {
  name          = "${local.name_prefix}-api"
  protocol_type = "HTTP"
  description   = "API Gateway for Agentic AI Services - 24 agents across 4 phases"

  cors_configuration {
    allow_origins = var.api_cors_origins
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["content-type", "authorization", "x-api-key"]
    max_age       = 300
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api"
  })
}

# -----------------------------------------------------------------------------
# API Gateway Stage
# -----------------------------------------------------------------------------
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.agents.id
  name        = var.environment
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      errorMessage   = "$context.error.message"
    })
  }

  default_route_settings {
    throttling_burst_limit = var.api_throttle_burst_limit
    throttling_rate_limit  = var.api_throttle_rate_limit
    logging_level          = var.environment == "production" ? "INFO" : "ERROR"
    data_trace_enabled     = var.environment != "production"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-stage"
  })
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${local.name_prefix}"
  retention_in_days = var.cloudwatch_log_retention_days

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-logs"
  })
}

# -----------------------------------------------------------------------------
# Lambda Integrations
# -----------------------------------------------------------------------------
resource "aws_apigatewayv2_integration" "agents" {
  for_each = toset(local.all_agents)

  api_id           = aws_apigatewayv2_api.agents.id
  integration_type = "AWS_PROXY"

  connection_type        = "INTERNET"
  description            = "Integration for ${each.key} agent"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.agents[each.key].invoke_arn
  payload_format_version = "2.0"
  timeout_milliseconds   = 30000 # API Gateway max is 30 seconds (Lambda can run longer)
}

# -----------------------------------------------------------------------------
# Routes for Each Agent
# -----------------------------------------------------------------------------

# POST /agents/{agent-name} - Execute agent
resource "aws_apigatewayv2_route" "agent_execute" {
  for_each = toset(local.all_agents)

  api_id    = aws_apigatewayv2_api.agents.id
  route_key = "POST /agents/${replace(each.key, "_", "-")}"
  target    = "integrations/${aws_apigatewayv2_integration.agents[each.key].id}"

  authorization_type = var.api_auth_type
  authorizer_id      = var.api_auth_type == "JWT" ? aws_apigatewayv2_authorizer.jwt[0].id : null
}

# GET /agents/{agent-name}/status - Get agent status
resource "aws_apigatewayv2_route" "agent_status" {
  for_each = toset(local.all_agents)

  api_id    = aws_apigatewayv2_api.agents.id
  route_key = "GET /agents/${replace(each.key, "_", "-")}/status"
  target    = "integrations/${aws_apigatewayv2_integration.agents[each.key].id}"

  authorization_type = var.api_auth_type
  authorizer_id      = var.api_auth_type == "JWT" ? aws_apigatewayv2_authorizer.jwt[0].id : null
}

# -----------------------------------------------------------------------------
# Additional Routes
# -----------------------------------------------------------------------------

# GET /health - Health check endpoint
resource "aws_apigatewayv2_route" "health" {
  api_id    = aws_apigatewayv2_api.agents.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.health.id}"
}

# Lambda for health check
resource "aws_lambda_function" "health_check" {
  filename      = var.lambda_package_path
  function_name = "${local.name_prefix}-health-check"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "handler.health_check_handler"
  runtime       = "python3.11"
  timeout       = 10
  memory_size   = 128

  layers = [aws_lambda_layer_version.agent_dependencies.arn]

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-health-check"
  })
}

resource "aws_apigatewayv2_integration" "health" {
  api_id                 = aws_apigatewayv2_api.agents.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.health_check.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_lambda_permission" "health_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.health_check.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.agents.execution_arn}/*/*"
}

# GET /agents - List all available agents
resource "aws_apigatewayv2_route" "list_agents" {
  api_id    = aws_apigatewayv2_api.agents.id
  route_key = "GET /agents"
  target    = "integrations/${aws_apigatewayv2_integration.list_agents.id}"
}

resource "aws_lambda_function" "list_agents" {
  filename      = var.lambda_package_path
  function_name = "${local.name_prefix}-list-agents"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "handler.list_agents_handler"
  runtime       = "python3.11"
  timeout       = 10
  memory_size   = 128

  layers = [aws_lambda_layer_version.agent_dependencies.arn]

  environment {
    variables = {
      ENVIRONMENT  = var.environment
      TOTAL_AGENTS = length(local.all_agents)
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-list-agents"
  })
}

resource "aws_apigatewayv2_integration" "list_agents" {
  api_id                 = aws_apigatewayv2_api.agents.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.list_agents.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_lambda_permission" "list_agents_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.list_agents.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.agents.execution_arn}/*/*"
}

# -----------------------------------------------------------------------------
# API Gateway Authorizer (Optional JWT)
# -----------------------------------------------------------------------------
resource "aws_apigatewayv2_authorizer" "jwt" {
  count = var.api_auth_type == "JWT" ? 1 : 0

  api_id           = aws_apigatewayv2_api.agents.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "${local.name_prefix}-jwt-authorizer"

  jwt_configuration {
    audience = [var.jwt_audience]
    issuer   = var.jwt_issuer
  }
}

# -----------------------------------------------------------------------------
# API Gateway Custom Domain (Optional)
# -----------------------------------------------------------------------------
resource "aws_apigatewayv2_domain_name" "custom" {
  count = var.api_custom_domain != "" ? 1 : 0

  domain_name = var.api_custom_domain

  domain_name_configuration {
    certificate_arn = var.api_certificate_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-custom-domain"
  })
}

resource "aws_apigatewayv2_api_mapping" "custom" {
  count = var.api_custom_domain != "" ? 1 : 0

  api_id      = aws_apigatewayv2_api.agents.id
  domain_name = aws_apigatewayv2_domain_name.custom[0].id
  stage       = aws_apigatewayv2_stage.default.id
}

# -----------------------------------------------------------------------------
# API Gateway Usage Plan and API Keys (Optional)
# -----------------------------------------------------------------------------
resource "aws_api_gateway_api_key" "clients" {
  for_each = var.enable_api_keys ? var.api_key_clients : {}

  name        = "${local.name_prefix}-${each.key}"
  description = "API key for ${each.value}"
  enabled     = true

  tags = merge(local.common_tags, {
    Name   = "${local.name_prefix}-${each.key}-key"
    Client = each.value
  })
}

# -----------------------------------------------------------------------------
# CloudWatch Alarms for API Gateway
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_metric_alarm" "api_4xx_errors" {
  count = var.enable_monitoring ? 1 : 0

  alarm_name          = "${local.name_prefix}-api-4xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "4XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = "50"
  alarm_description   = "API Gateway 4XX errors exceeded threshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    ApiId = aws_apigatewayv2_api.agents.id
  }

  alarm_actions = var.cloudwatch_alarm_email != "" ? [aws_sns_topic.alerts[0].arn] : []

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-4xx-alarm"
  })
}

resource "aws_cloudwatch_metric_alarm" "api_5xx_errors" {
  count = var.enable_monitoring ? 1 : 0

  alarm_name          = "${local.name_prefix}-api-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = "60"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "API Gateway 5XX errors exceeded threshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    ApiId = aws_apigatewayv2_api.agents.id
  }

  alarm_actions = var.cloudwatch_alarm_email != "" ? [aws_sns_topic.alerts[0].arn] : []

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-5xx-alarm"
  })
}

# SNS Topic for alarms
resource "aws_sns_topic" "alerts" {
  count = var.cloudwatch_alarm_email != "" && var.enable_monitoring ? 1 : 0

  name = "${local.name_prefix}-alerts"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alerts"
  })
}

resource "aws_sns_topic_subscription" "alerts_email" {
  count = var.cloudwatch_alarm_email != "" && var.enable_monitoring ? 1 : 0

  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.cloudwatch_alarm_email
}

# =============================================================================
# Notes:
# =============================================================================
# - HTTP API (not REST API) for lower cost and better performance
# - Each agent accessible at POST /agents/{agent-name}
# - Health check at GET /health
# - List all agents at GET /agents
# - Optional JWT authorizer for authentication
# - Optional custom domain with ACM certificate
# - CloudWatch alarms for 4XX and 5XX errors
# - CORS enabled for web app integration
# =============================================================================
