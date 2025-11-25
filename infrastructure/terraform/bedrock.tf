# =============================================================================
# AWS Bedrock Configuration
# =============================================================================
# Bedrock foundation model access configuration
# Note: Model access must be enabled in AWS Console first
# =============================================================================

# Data source to check current region for Bedrock availability
data "aws_region" "bedrock" {
  provider = aws
}

# =============================================================================
# Model Access Notes
# =============================================================================
# Before using Bedrock, you must request model access:
# 1. Navigate to AWS Console > Bedrock > Model access
# 2. Request access for these models:
#    - anthropic.claude-3-5-sonnet-20240620-v2:0 (Discovery + Analysis)
#    - anthropic.claude-3-5-sonnet-20241022-v2:0 (Planning)
#    - anthropic.claude-3-7-sonnet-20250219-v1:0 (Artifact Generation)
# 3. Wait for approval (usually instant for Claude models)
#
# Bedrock is available in: us-east-1, us-west-2, eu-central-1, ap-southeast-1, etc.
# =============================================================================

# IAM policy data for Bedrock model invocation (referenced by iam.tf)
data "aws_iam_policy_document" "bedrock_access" {
  statement {
    sid    = "BedrockInvokeModel"
    effect = "Allow"

    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream"
    ]

    resources = concat(
      [for model in var.bedrock_claude_models : "arn:aws:bedrock:${data.aws_region.bedrock.name}::foundation-model/${model}"],
      # Allow access to all Claude models if models list is empty
      var.bedrock_claude_models == [] ? ["arn:aws:bedrock:${data.aws_region.bedrock.name}::foundation-model/anthropic.claude*"] : []
    )
  }

  statement {
    sid    = "BedrockListModels"
    effect = "Allow"

    actions = [
      "bedrock:ListFoundationModels",
      "bedrock:GetFoundationModel"
    ]

    resources = ["*"]
  }
}

# =============================================================================
# CloudWatch Log Group for Bedrock Model Invocation Logs (Optional)
# =============================================================================
# Enable this if you want detailed model invocation logging for debugging
# Note: This incurs additional CloudWatch costs

resource "aws_cloudwatch_log_group" "bedrock_invocations" {
  count             = var.enable_bedrock_logging ? 1 : 0
  name              = "/aws/bedrock/${local.name_prefix}-model-invocations"
  retention_in_days = var.cloudwatch_retention_days
  kms_key_id        = var.enable_cloudwatch_encryption ? aws_kms_key.logs[0].arn : null

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-bedrock-logs"
    }
  )
}

# =============================================================================
# Cost Optimization Notes
# =============================================================================
# - Claude 3.5 Sonnet: ~$3/million input tokens, ~$15/million output tokens
# - Claude 3.7 Sonnet: ~$3/million input tokens, ~$15/million output tokens
# - Free tier: None for Bedrock (pay-per-use only)
# - Cost monitoring: Use CloudWatch metrics and set budget alerts
# =============================================================================
