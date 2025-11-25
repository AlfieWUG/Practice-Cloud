# =============================================================================
# ECS (Elastic Container Service)
# =============================================================================
# Creates ECS cluster and task definitions for running containerized agents
# =============================================================================

resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  setting {
    name  = "containerInsights"
    value = var.enable_monitoring ? "enabled" : "disabled"
  }

  tags = local.common_tags
}

resource "aws_ecs_task_definition" "agent_runner" {
  family                   = local.ecs_task_family
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "agent-runner"
    image     = "776031435874.dkr.ecr.eu-central-1.amazonaws.com/nagarro-agentic-services:latest"
    essential = true

    portMappings = [{
      containerPort = 8501
      protocol      = "tcp"
    }]

    environment = [
      { name = "AWS_REGION", value = var.aws_region },
      { name = "ENVIRONMENT", value = var.environment },
      { name = "S3_DISCOVERY_BUCKET", value = aws_s3_bucket.discovery.id },
      { name = "S3_ARTIFACTS_BUCKET", value = aws_s3_bucket.artifacts.id },
      { name = "DYNAMODB_AGENT_STATES_TABLE", value = aws_dynamodb_table.agent_states.name },
      { name = "DYNAMODB_WORKFLOW_HISTORY_TABLE", value = aws_dynamodb_table.workflow_history.name },
      { name = "DYNAMODB_PROJECT_METADATA_TABLE", value = aws_dynamodb_table.project_metadata.name },
      { name = "EVENT_BUS_NAME", value = aws_cloudwatch_event_bus.main.name },
      { name = "BEDROCK_MODEL_ID", value = var.bedrock_model_id }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])

  tags = local.common_tags
}

resource "aws_ecs_service" "agent_runner" {
  name            = local.ecs_service_name
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.agent_runner.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.dashboard.arn
    container_name   = "agent-runner"
    container_port   = 8501
  }

  depends_on = [aws_lb_listener.https]

  tags = local.common_tags
}
