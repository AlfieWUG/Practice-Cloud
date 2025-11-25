# =============================================================================
# IAM Roles and Policies
# =============================================================================
# Creates IAM roles and policies following least privilege principle:
# 1. ECS Task Execution Role - Pull images, write logs
# 2. ECS Task Role - Application permissions (S3, DynamoDB, Bedrock, EventBridge)
# =============================================================================

# -----------------------------------------------------------------------------
# ECS Task Execution Role
# -----------------------------------------------------------------------------
# Used by ECS to pull container images and write logs to CloudWatch

resource "aws_iam_role" "ecs_task_execution" {
  name = "${local.name_prefix}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = local.common_tags
}

# Attach AWS managed policy for ECS task execution
resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# -----------------------------------------------------------------------------
# ECS Task Role
# -----------------------------------------------------------------------------
# Used by application code running in ECS tasks

resource "aws_iam_role" "ecs_task" {
  name = "${local.name_prefix}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# S3 Access Policy
# -----------------------------------------------------------------------------

resource "aws_iam_role_policy" "ecs_task_s3" {
  name = "${local.name_prefix}-ecs-task-s3-policy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.discovery.arn,
          "${aws_s3_bucket.discovery.arn}/*",
          aws_s3_bucket.artifacts.arn,
          "${aws_s3_bucket.artifacts.arn}/*",
          aws_s3_bucket.logs.arn,
          "${aws_s3_bucket.logs.arn}/*"
        ]
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# DynamoDB Access Policy
# -----------------------------------------------------------------------------

resource "aws_iam_role_policy" "ecs_task_dynamodb" {
  name = "${local.name_prefix}-ecs-task-dynamodb-policy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.agent_states.arn,
          "${aws_dynamodb_table.agent_states.arn}/index/*",
          aws_dynamodb_table.workflow_history.arn,
          "${aws_dynamodb_table.workflow_history.arn}/index/*",
          aws_dynamodb_table.project_metadata.arn,
          "${aws_dynamodb_table.project_metadata.arn}/index/*"
        ]
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# Bedrock Access Policy
# -----------------------------------------------------------------------------

resource "aws_iam_role_policy" "ecs_task_bedrock" {
  name = "${local.name_prefix}-ecs-task-bedrock-policy"
  role = aws_iam_role.ecs_task.id

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
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# EventBridge Access Policy
# -----------------------------------------------------------------------------

resource "aws_iam_role_policy" "ecs_task_eventbridge" {
  name = "${local.name_prefix}-ecs-task-eventbridge-policy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "events:PutEvents"
        ]
        Resource = aws_cloudwatch_event_bus.main.arn
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# CloudWatch Logs Policy (for application logging)
# -----------------------------------------------------------------------------

resource "aws_iam_role_policy" "ecs_task_logs" {
  name = "${local.name_prefix}-ecs-task-logs-policy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          aws_cloudwatch_log_group.ecs.arn,
          "${aws_cloudwatch_log_group.ecs.arn}:*",
          aws_cloudwatch_log_group.application.arn,
          "${aws_cloudwatch_log_group.application.arn}:*"
        ]
      }
    ]
  })
}

# =============================================================================
# Security Best Practices
# =============================================================================
# 1. Least Privilege: Policies grant only required permissions
# 2. Resource-Specific: Permissions limited to specific resources (not "*")
# 3. Separation of Concerns: 
#    - Execution role: ECS infrastructure operations
#    - Task role: Application operations
# 4. No Wildcard Resources: Explicit ARNs for S3, DynamoDB, etc.
# 5. Scoped Bedrock Access: Limited to specific model only
#
# Production Hardening:
# - Add IAM policy conditions (e.g., IP restrictions, MFA)
# - Enable CloudTrail for IAM API logging
# - Regular access review and rotation
# - Use IAM Access Analyzer to validate policies
# =============================================================================
