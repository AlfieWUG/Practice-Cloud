# =============================================================================
# CloudWatch Monitoring
# =============================================================================
# Log groups, alarms, dashboards, and cost anomaly detection
# =============================================================================

# KMS key for CloudWatch Logs encryption (optional)
resource "aws_kms_key" "logs" {
  count                   = var.enable_cloudwatch_encryption ? 1 : 0
  description             = "${local.name_prefix} CloudWatch Logs encryption key"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-logs-kms"
    }
  )
}

resource "aws_kms_alias" "logs" {
  count         = var.enable_cloudwatch_encryption ? 1 : 0
  name          = "alias/${local.name_prefix}-logs"
  target_key_id = aws_kms_key.logs[0].key_id
}

resource "aws_kms_key_policy" "logs" {
  count  = var.enable_cloudwatch_encryption ? 1 : 0
  key_id = aws_kms_key.logs[0].key_id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:CreateGrant",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          ArnLike = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:*"
          }
        }
      }
    ]
  })
}

# =============================================================================
# Log Groups
# =============================================================================

# ECS task logs
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${local.name_prefix}"
  retention_in_days = var.cloudwatch_retention_days
  kms_key_id        = var.enable_cloudwatch_encryption ? aws_kms_key.logs[0].arn : null

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ecs-logs"
    }
  )
}

# Main application log group (ECS container logs)
resource "aws_cloudwatch_log_group" "application" {
  name              = "/ecs/${local.name_prefix}/application"
  retention_in_days = var.cloudwatch_retention_days
  kms_key_id        = var.enable_cloudwatch_encryption ? aws_kms_key.logs[0].arn : null

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-app-logs"
    }
  )
}

# Agent execution logs
resource "aws_cloudwatch_log_group" "agents" {
  name              = "/ecs/${local.name_prefix}/agents"
  retention_in_days = var.cloudwatch_retention_days
  kms_key_id        = var.enable_cloudwatch_encryption ? aws_kms_key.logs[0].arn : null

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-agent-logs"
    }
  )
}

# =============================================================================
# CloudWatch Alarms
# =============================================================================

# High CPU alarm for ECS service
resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "${local.name_prefix}-ecs-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ECS CPU utilization"
  treat_missing_data  = "notBreaching"

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.agent_runner.name
  }

  tags = local.common_tags
}

# High memory alarm for ECS service
resource "aws_cloudwatch_metric_alarm" "ecs_memory_high" {
  alarm_name          = "${local.name_prefix}-ecs-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ECS memory utilization"
  treat_missing_data  = "notBreaching"

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.agent_runner.name
  }

  tags = local.common_tags
}

# DynamoDB throttled requests alarm
resource "aws_cloudwatch_metric_alarm" "dynamodb_throttle" {
  count               = var.enable_cost_alarms ? 1 : 0
  alarm_name          = "${local.name_prefix}-dynamodb-throttle"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "SystemErrors"
  namespace           = "AWS/DynamoDB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors DynamoDB throttling"
  treat_missing_data  = "notBreaching"

  tags = local.common_tags
}

# =============================================================================
# Cost Anomaly Detection
# =============================================================================

resource "aws_ce_anomaly_monitor" "service" {
  count             = var.enable_cost_alarms ? 1 : 0
  name              = "${local.name_prefix}-cost-monitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"

  tags = local.common_tags
}

resource "aws_ce_anomaly_subscription" "alerts" {
  count     = var.enable_cost_alarms ? 1 : 0
  name      = "${local.name_prefix}-cost-alerts"
  frequency = "DAILY"

  monitor_arn_list = [
    aws_ce_anomaly_monitor.service[0].arn
  ]

  subscriber {
    type    = "EMAIL"
    address = var.cost_alert_email
  }

  threshold_expression {
    dimension {
      key           = "ANOMALY_TOTAL_IMPACT_ABSOLUTE"
      match_options = ["GREATER_THAN_OR_EQUAL"]
      values        = [tostring(var.cost_anomaly_threshold)]
    }
  }

  tags = local.common_tags
}

# =============================================================================
# CloudWatch Dashboard
# =============================================================================

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", { stat = "Average", label = "CPU" }],
            [".", "MemoryUtilization", { stat = "Average", label = "Memory" }]
          ]
          period = 300
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "ECS Service Metrics"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", { stat = "Sum" }],
            [".", "ConsumedWriteCapacityUnits", { stat = "Sum" }]
          ]
          period = 300
          stat   = "Sum"
          region = data.aws_region.current.name
          title  = "DynamoDB Capacity"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/S3", "NumberOfObjects", { stat = "Average" }],
            [".", "BucketSizeBytes", { stat = "Average" }]
          ]
          period = 86400
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "S3 Storage Metrics"
        }
      },
      {
        type = "log"
        properties = {
          query  = "SOURCE '${aws_cloudwatch_log_group.application.name}' | fields @timestamp, @message | sort @timestamp desc | limit 100"
          region = data.aws_region.current.name
          title  = "Recent Application Logs"
        }
      }
    ]
  })
}

# =============================================================================
# Cost Optimization Notes
# =============================================================================
# - CloudWatch Logs: First 5GB/month free, then $0.50/GB ingested
# - CloudWatch Metrics: First 10 custom metrics free, then $0.30/metric/month
# - Alarms: First 10 alarms free, then $0.10/alarm/month
# - Dashboards: First 3 free, then $3/dashboard/month
# - Log retention: Shorter retention = lower costs (7 days for dev, 30+ for prod)
# =============================================================================
