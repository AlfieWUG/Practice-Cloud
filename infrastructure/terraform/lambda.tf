# =============================================================================
# Lambda Functions for Agentic Services
# =============================================================================
# Creates Lambda functions for all 24 agents across 4 phases:
# - Discovery Phase (8 agents)
# - Assessment Phase (5 agents)
# - Execution Phase (6 agents)
# - Optimization Phase (5 agents)
# =============================================================================

# -----------------------------------------------------------------------------
# Lambda Execution Role
# -----------------------------------------------------------------------------
resource "aws_iam_role" "lambda_execution" {
  name = "${local.name_prefix}-lambda-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-lambda-execution-role"
  })
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Attach VPC execution policy (if Lambda needs VPC access)
resource "aws_iam_role_policy_attachment" "lambda_vpc_execution" {
  count      = var.enable_lambda_vpc ? 1 : 0
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Custom policy for agent permissions
resource "aws_iam_role_policy" "lambda_agent_permissions" {
  name = "${local.name_prefix}-lambda-agent-policy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_model_id}"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.discovery.arn,
          "${aws_s3_bucket.discovery.arn}/*",
          aws_s3_bucket.artifacts.arn,
          "${aws_s3_bucket.artifacts.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.agent_states.arn,
          aws_dynamodb_table.workflow_history.arn,
          aws_dynamodb_table.project_metadata.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "events:PutEvents"
        ]
        Resource = aws_cloudwatch_event_bus.main.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${local.name_prefix}-*"
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage"
        ]
        Resource = aws_sqs_queue.dlq.arn
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# Lambda Layer for Dependencies
# -----------------------------------------------------------------------------
resource "aws_lambda_layer_version" "agent_dependencies" {
  filename            = var.lambda_layer_path
  layer_name          = "${local.name_prefix}-dependencies"
  compatible_runtimes = ["python3.11", "python3.12"]
  description         = "Common dependencies for agentic services (boto3, etc.)"

  lifecycle {
    create_before_destroy = true
  }
}

# -----------------------------------------------------------------------------
# Lambda Functions - Discovery Phase (8 agents)
# -----------------------------------------------------------------------------
locals {
  discovery_agents = [
    "discovery",
    "analysis",
    "planning",
    "artifact_generation",
    "network_scanner",
    "application_profiler",
    "performance_monitor",
    "data_classifier"
  ]

  assessment_agents = [
    "dependency_mapper",
    "compliance_checker",
    "cost_estimator",
    "risk_assessment",
    "capacity_planner"
  ]

  execution_agents = [
    "infrastructure_provisioner",
    "data_migration",
    "application_migration",
    "configuration",
    "testing",
    "rollback"
  ]

  optimization_agents = [
    "performance_optimizer",
    "cost_optimizer",
    "security_hardening",
    "monitoring_setup",
    "documentation"
  ]

  all_agents = concat(
    local.discovery_agents,
    local.assessment_agents,
    local.execution_agents,
    local.optimization_agents
  )
}

# Create Lambda function for each agent
resource "aws_lambda_function" "agents" {
  for_each = toset(local.all_agents)

  filename      = var.lambda_package_path
  function_name = "${local.name_prefix}-${each.key}"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "handler.${each.key}_handler"
  runtime       = "python3.11"
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  layers = [aws_lambda_layer_version.agent_dependencies.arn]

  environment {
    variables = {
      ENVIRONMENT             = var.environment
      AWS_REGION_NAME         = var.aws_region
      S3_DISCOVERY_BUCKET     = aws_s3_bucket.discovery.id
      S3_ARTIFACTS_BUCKET     = aws_s3_bucket.artifacts.id
      DYNAMODB_STATES_TABLE   = aws_dynamodb_table.agent_states.name
      DYNAMODB_HISTORY_TABLE  = aws_dynamodb_table.workflow_history.name
      DYNAMODB_METADATA_TABLE = aws_dynamodb_table.project_metadata.name
      EVENT_BUS_NAME          = aws_cloudwatch_event_bus.main.name
      BEDROCK_MODEL_ID        = var.bedrock_model_id
      LOG_LEVEL               = var.environment == "production" ? "INFO" : "DEBUG"
    }
  }

  dynamic "vpc_config" {
    for_each = var.enable_lambda_vpc ? [1] : []
    content {
      subnet_ids         = aws_subnet.private[*].id
      security_group_ids = [aws_security_group.lambda.id]
    }
  }

  tags = merge(local.common_tags, {
    Name  = "${local.name_prefix}-${each.key}"
    Agent = each.key
    Phase = contains(local.discovery_agents, each.key) ? "discovery" : (
      contains(local.assessment_agents, each.key) ? "assessment" : (
        contains(local.execution_agents, each.key) ? "execution" : "optimization"
      )
    )
  })

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.lambda_agent_permissions,
    aws_cloudwatch_log_group.lambda_logs
  ]
}

# -----------------------------------------------------------------------------
# CloudWatch Log Groups for Lambda Functions
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_log_group" "lambda_logs" {
  for_each = toset(local.all_agents)

  name              = "/aws/lambda/${local.name_prefix}-${each.key}"
  retention_in_days = var.cloudwatch_log_retention_days

  tags = merge(local.common_tags, {
    Name  = "${local.name_prefix}-${each.key}-logs"
    Agent = each.key
  })
}

# -----------------------------------------------------------------------------
# Lambda Function URLs (for direct HTTPS invocation)
# -----------------------------------------------------------------------------
resource "aws_lambda_function_url" "agents" {
  for_each = var.enable_lambda_urls ? toset(local.all_agents) : []

  function_name      = aws_lambda_function.agents[each.key].function_name
  authorization_type = "AWS_IAM"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["POST"]
    allow_headers     = ["date", "keep-alive", "content-type"]
    expose_headers    = ["keep-alive", "date"]
    max_age           = 86400
  }
}

# -----------------------------------------------------------------------------
# Lambda Permissions for API Gateway
# -----------------------------------------------------------------------------
resource "aws_lambda_permission" "api_gateway" {
  for_each = toset(local.all_agents)

  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agents[each.key].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.agents.execution_arn}/*/*"
}

# -----------------------------------------------------------------------------
# Lambda Permissions for EventBridge
# -----------------------------------------------------------------------------
resource "aws_lambda_permission" "eventbridge" {
  for_each = toset(local.all_agents)

  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agents[each.key].function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_bus.main.arn
}

# -----------------------------------------------------------------------------
# Lambda Security Group (if VPC is enabled)
# -----------------------------------------------------------------------------
resource "aws_security_group" "lambda" {
  count = var.enable_lambda_vpc ? 1 : 0

  name        = "${local.name_prefix}-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-lambda-sg"
  })
}

# -----------------------------------------------------------------------------
# Lambda Auto-Scaling (Reserved Concurrency)
# -----------------------------------------------------------------------------
resource "aws_lambda_function_event_invoke_config" "agents" {
  for_each = toset(local.all_agents)

  function_name                = aws_lambda_function.agents[each.key].function_name
  maximum_retry_attempts       = var.lambda_max_retry_attempts
  maximum_event_age_in_seconds = var.lambda_max_event_age

  destination_config {
    on_failure {
      destination = aws_sqs_queue.dlq.arn
    }
  }
}

# -----------------------------------------------------------------------------
# Dead Letter Queue for Failed Invocations
# -----------------------------------------------------------------------------
resource "aws_sqs_queue" "dlq" {
  name                      = "${local.name_prefix}-lambda-dlq"
  message_retention_seconds = 1209600 # 14 days

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-lambda-dlq"
  })
}

# Allow Lambda to send messages to DLQ
resource "aws_sqs_queue_policy" "dlq" {
  queue_url = aws_sqs_queue.dlq.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action   = "sqs:SendMessage"
      Resource = aws_sqs_queue.dlq.arn
    }]
  })
}

# =============================================================================
# Notes:
# =============================================================================
# - All 24 agents are created as separate Lambda functions
# - Each agent has its own CloudWatch log group
# - Agents can be invoked via API Gateway or EventBridge
# - Failed invocations go to a Dead Letter Queue
# - VPC configuration is optional (disable for cost savings in dev)
# - Lambda layer contains shared dependencies
# =============================================================================
