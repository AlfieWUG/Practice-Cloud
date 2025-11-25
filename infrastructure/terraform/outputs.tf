# =============================================================================
# Terraform Outputs
# =============================================================================
# These values are displayed after 'terraform apply' and can be queried with
# 'terraform output' or used by other Terraform configurations
# =============================================================================

# -----------------------------------------------------------------------------
# VPC Outputs
# -----------------------------------------------------------------------------

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "nat_gateway_ips" {
  description = "Elastic IPs of NAT Gateways"
  value       = aws_eip.nat[*].public_ip
}

# -----------------------------------------------------------------------------
# ECS Outputs
# -----------------------------------------------------------------------------

output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.agent_runner.name
}

# -----------------------------------------------------------------------------
# ALB & Dashboard Outputs
# -----------------------------------------------------------------------------

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = aws_lb.main.zone_id
}

output "dashboard_url" {
  description = "URL to access the Dashboard"
  value       = var.dashboard_domain_name != "" ? "https://${var.dashboard_domain_name}" : "https://${aws_lb.main.dns_name}"
}

output "dashboard_custom_domain" {
  description = "Custom domain name (if configured)"
  value       = var.dashboard_domain_name != "" ? var.dashboard_domain_name : null
}

output "acm_certificate_arn" {
  description = "ARN of the ACM certificate for HTTPS"
  value       = var.acm_certificate_arn != "" ? var.acm_certificate_arn : (var.dashboard_domain_name != "" ? aws_acm_certificate.dashboard[0].arn : null)
}

# -----------------------------------------------------------------------------
# S3 Outputs
# -----------------------------------------------------------------------------

output "s3_discovery_bucket" {
  description = "Name of the discovery data bucket"
  value       = aws_s3_bucket.discovery.id
}

output "s3_artifacts_bucket" {
  description = "Name of the artifacts bucket"
  value       = aws_s3_bucket.artifacts.id
}

output "s3_logs_bucket" {
  description = "Name of the logs bucket"
  value       = aws_s3_bucket.logs.id
}

output "s3_discovery_bucket_arn" {
  description = "ARN of the discovery bucket"
  value       = aws_s3_bucket.discovery.arn
}

output "s3_artifacts_bucket_arn" {
  description = "ARN of the artifacts bucket"
  value       = aws_s3_bucket.artifacts.arn
}

# -----------------------------------------------------------------------------
# DynamoDB Outputs
# -----------------------------------------------------------------------------

output "dynamodb_agent_states_table" {
  description = "Name of the AgentStates DynamoDB table"
  value       = aws_dynamodb_table.agent_states.name
}

output "dynamodb_workflow_history_table" {
  description = "Name of the WorkflowHistory DynamoDB table"
  value       = aws_dynamodb_table.workflow_history.name
}

output "dynamodb_project_metadata_table" {
  description = "Name of the ProjectMetadata DynamoDB table"
  value       = aws_dynamodb_table.project_metadata.name
}

# -----------------------------------------------------------------------------
# IAM Outputs
# -----------------------------------------------------------------------------

output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task.arn
}

# -----------------------------------------------------------------------------
# EventBridge Outputs
# -----------------------------------------------------------------------------

output "eventbridge_bus_name" {
  description = "Name of the EventBridge event bus"
  value       = aws_cloudwatch_event_bus.main.name
}

output "eventbridge_bus_arn" {
  description = "ARN of the EventBridge event bus"
  value       = aws_cloudwatch_event_bus.main.arn
}

# -----------------------------------------------------------------------------
# CloudWatch Outputs
# -----------------------------------------------------------------------------

output "cloudwatch_log_group_ecs" {
  description = "Name of the ECS CloudWatch log group"
  value       = aws_cloudwatch_log_group.ecs.name
}

output "cloudwatch_log_group_application" {
  description = "Name of the application CloudWatch log group"
  value       = aws_cloudwatch_log_group.application.name
}

# -----------------------------------------------------------------------------
# Bedrock Outputs
# -----------------------------------------------------------------------------

output "bedrock_model_id" {
  description = "ID of the Bedrock model being used"
  value       = var.bedrock_model_id
}

# -----------------------------------------------------------------------------
# Lambda Outputs
# -----------------------------------------------------------------------------

output "lambda_function_arns" {
  description = "Map of Lambda function names to ARNs"
  value       = { for k, v in aws_lambda_function.agents : k => v.arn }
}

output "lambda_function_names" {
  description = "List of all Lambda function names"
  value       = [for k, v in aws_lambda_function.agents : v.function_name]
}

output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution.arn
}

output "lambda_layer_arn" {
  description = "ARN of the Lambda dependencies layer"
  value       = aws_lambda_layer_version.agent_dependencies.arn
}

output "lambda_dlq_url" {
  description = "URL of the Lambda Dead Letter Queue"
  value       = aws_sqs_queue.dlq.url
}

# -----------------------------------------------------------------------------
# API Gateway Outputs
# -----------------------------------------------------------------------------

output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = aws_apigatewayv2_api.agents.id
}

output "api_gateway_endpoint" {
  description = "Default endpoint URL of the API Gateway"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "api_gateway_custom_domain" {
  description = "Custom domain URL (if configured)"
  value       = var.api_custom_domain != "" ? "https://${var.api_custom_domain}" : null
}

output "api_health_endpoint" {
  description = "Health check endpoint"
  value       = "${aws_apigatewayv2_stage.default.invoke_url}/health"
}

output "api_list_agents_endpoint" {
  description = "Endpoint to list all agents"
  value       = "${aws_apigatewayv2_stage.default.invoke_url}/agents"
}

output "api_agent_endpoints" {
  description = "Map of agent names to their API endpoints"
  value = {
    for agent in concat(local.discovery_agents, local.assessment_agents, local.execution_agents, local.optimization_agents) :
    agent => "${aws_apigatewayv2_stage.default.invoke_url}/agents/${agent}"
  }
}

output "api_cloudwatch_log_group" {
  description = "CloudWatch log group for API Gateway"
  value       = aws_cloudwatch_log_group.api_gateway.name
}

# -----------------------------------------------------------------------------
# General Outputs
# -----------------------------------------------------------------------------

output "environment" {
  description = "Current environment"
  value       = var.environment
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

# -----------------------------------------------------------------------------
# Connection Information
# -----------------------------------------------------------------------------

output "connection_info" {
  description = "Quick reference for connecting to resources"
  value = {
    region             = var.aws_region
    environment        = var.environment
    vpc_id             = aws_vpc.main.id
    ecs_cluster        = aws_ecs_cluster.main.name
    discovery_bucket   = aws_s3_bucket.discovery.id
    agent_states_table = aws_dynamodb_table.agent_states.name
    api_endpoint       = aws_apigatewayv2_stage.default.invoke_url
    api_health         = "${aws_apigatewayv2_stage.default.invoke_url}/health"
    lambda_count       = length(aws_lambda_function.agents)
  }
}

# =============================================================================
# Usage Examples:
# =============================================================================
# # View all outputs
# terraform output
#
# # View specific output
# terraform output vpc_id
#
# # Get JSON format (useful for scripts)
# terraform output -json
#
# # Use in other Terraform configs
# data "terraform_remote_state" "agentic" {
#   backend = "s3"
#   config = {
#     bucket = "nagarro-agentic-terraform-state"
#     key    = "dev/terraform.tfstate"
#     region = "eu-central-1"
#   }
# }
# 
# # Reference outputs
# vpc_id = data.terraform_remote_state.agentic.outputs.vpc_id
# =============================================================================
