# =============================================================================
# EventBridge (Event Bus)
# =============================================================================
# Custom event bus for agent coordination and workflow orchestration
# =============================================================================

resource "aws_cloudwatch_event_bus" "main" {
  name = local.event_bus_name
  tags = local.common_tags
}

# Example rule for agent completion events
resource "aws_cloudwatch_event_rule" "agent_completed" {
  name           = "${local.name_prefix}-agent-completed"
  event_bus_name = aws_cloudwatch_event_bus.main.name

  event_pattern = jsonencode({
    source      = ["agent.discoveryagent", "agent.analysisagent", "agent.planningagent", "agent.artifactgenerationagent"]
    detail-type = ["discovery.completed", "analysis.completed", "planning.completed", "artifact_generation.completed"]
  })

  tags = local.common_tags
}

# Log all events to CloudWatch (useful for debugging)
resource "aws_cloudwatch_event_rule" "log_all_events" {
  name           = "${local.name_prefix}-log-all-events"
  event_bus_name = aws_cloudwatch_event_bus.main.name

  event_pattern = jsonencode({
    source = [{ prefix = "agent." }]
  })

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "log_all_events" {
  rule           = aws_cloudwatch_event_rule.log_all_events.name
  event_bus_name = aws_cloudwatch_event_bus.main.name
  arn            = aws_cloudwatch_log_group.application.arn
  target_id      = "CloudWatchLogGroup"
}

resource "aws_cloudwatch_log_resource_policy" "eventbridge_logs" {
  policy_name = "${local.name_prefix}-eventbridge-logs-policy"

  policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "events.amazonaws.com"
      }
      Action = [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      Resource = "${aws_cloudwatch_log_group.application.arn}:*"
    }]
  })
}
