# =============================================================================
# Main Terraform Configuration
# =============================================================================
# This is the main entry point for the infrastructure.
# It references modules and resources defined in other files.
#
# File organization:
# - main.tf         (this file) - Main configuration and locals
# - providers.tf    - AWS provider configuration
# - variables.tf    - Input variables
# - outputs.tf      - Output values
# - vpc.tf         - Network infrastructure
# - ecs.tf         - Container orchestration
# - s3.tf          - Storage buckets
# - dynamodb.tf    - Database tables
# - iam.tf         - Permissions and roles
# - eventbridge.tf - Event bus
# - bedrock.tf     - AI model access
# - cloudwatch.tf  - Monitoring and logging
# =============================================================================

# -----------------------------------------------------------------------------
# Local Values
# -----------------------------------------------------------------------------
# Computed values used throughout the configuration
# -----------------------------------------------------------------------------

locals {
  # Resource naming convention: project-environment-resource
  name_prefix = "${var.project_name}-${var.environment}"

  # Common tags applied to all resources
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Repository  = "agentic-services"
  }

  # S3 bucket names (auto-generated if not provided)
  discovery_bucket_name = var.s3_discovery_bucket_name != "" ? var.s3_discovery_bucket_name : "${local.name_prefix}-discovery-${data.aws_caller_identity.current.account_id}"
  artifacts_bucket_name = var.s3_artifacts_bucket_name != "" ? var.s3_artifacts_bucket_name : "${local.name_prefix}-artifacts-${data.aws_caller_identity.current.account_id}"
  logs_bucket_name      = var.s3_logs_bucket_name != "" ? var.s3_logs_bucket_name : "${local.name_prefix}-logs-${data.aws_caller_identity.current.account_id}"

  # ECS task definition
  ecs_task_family  = "${local.name_prefix}-agent-runner"
  ecs_service_name = "${local.name_prefix}-service"

  # DynamoDB table names
  agent_states_table     = "${local.name_prefix}-agent-states"
  workflow_history_table = "${local.name_prefix}-workflow-history"
  project_metadata_table = "${local.name_prefix}-project-metadata"

  # CloudWatch log group names
  ecs_log_group         = "/ecs/${local.name_prefix}"
  application_log_group = "/app/${local.name_prefix}"

  # EventBridge
  event_bus_name = "${local.name_prefix}-event-bus"
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------
# Fetches information from AWS
# -----------------------------------------------------------------------------

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# Get current AWS region
data "aws_region" "current" {}

# Get available availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# =============================================================================
# Resource Deployment Order
# =============================================================================
# Terraform will automatically determine dependencies, but here's the logical order:
#
# 1. VPC & Networking (vpc.tf)
#    - VPC
#    - Subnets (public, private)
#    - Internet Gateway
#    - NAT Gateway
#    - Route Tables
#    - Security Groups
#
# 2. IAM Roles (iam.tf)
#    - ECS Task Execution Role
#    - ECS Task Role
#    - Policies for S3, DynamoDB, Bedrock, EventBridge
#
# 3. S3 Buckets (s3.tf)
#    - Discovery bucket
#    - Artifacts bucket
#    - Logs bucket
#
# 4. DynamoDB Tables (dynamodb.tf)
#    - AgentStates table
#    - WorkflowHistory table
#    - ProjectMetadata table
#
# 5. CloudWatch (cloudwatch.tf)
#    - Log Groups
#    - Alarms
#    - Dashboards
#
# 6. EventBridge (eventbridge.tf)
#    - Event Bus
#    - Event Rules
#
# 7. Bedrock (bedrock.tf)
#    - Model Access Configuration
#
# 8. ECS (ecs.tf)
#    - ECS Cluster
#    - Task Definitions
#    - Services
#    - Auto-scaling
#
# =============================================================================

# =============================================================================
# Usage Instructions
# =============================================================================
# 1. Initialize Terraform:
#    terraform init
#
# 2. Review what will be created:
#    terraform plan
#
# 3. Create infrastructure:
#    terraform apply
#
# 4. View outputs:
#    terraform output
#
# 5. Destroy infrastructure (when needed):
#    terraform destroy
#
# =============================================================================
# Cost Optimization Tips
# =============================================================================
# - Start with dev environment (lower resources)
# - Use single NAT Gateway (single_nat_gateway = true)
# - Keep ECS task size small (512 CPU, 1024 memory)
# - Enable S3 lifecycle policies
# - Use DynamoDB on-demand billing
# - Set short CloudWatch log retention (7 days for dev)
# - Review costs with: aws ce get-cost-and-usage
#
# =============================================================================
