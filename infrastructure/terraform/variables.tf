# =============================================================================
# Terraform Variables
# =============================================================================
# All configurable parameters for the infrastructure
# Override values by:
# 1. Creating terraform.tfvars file
# 2. Using -var flag: terraform apply -var="environment=production"
# 3. Environment variables: TF_VAR_environment=production
# =============================================================================

# -----------------------------------------------------------------------------
# General Configuration
# -----------------------------------------------------------------------------

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-central-1"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production"
  }
}

variable "project_name" {
  description = "Project name used in resource naming"
  type        = string
  default     = "nagarro-agentic"
}

variable "owner_email" {
  description = "Email of the infrastructure owner"
  type        = string
  default     = "platform-team@nagarro.com"
}

# -----------------------------------------------------------------------------
# Network Configuration
# -----------------------------------------------------------------------------

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to use"
  type        = list(string)
  default     = ["eu-central-1a", "eu-central-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets (costs $35/month per gateway)"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway for cost optimization (not recommended for production)"
  type        = bool
  default     = true # Set false for production (higher availability)
}

# -----------------------------------------------------------------------------
# ECS Configuration
# -----------------------------------------------------------------------------

variable "ecs_task_cpu" {
  description = "CPU units for ECS task (256 = 0.25 vCPU, 512 = 0.5 vCPU, 1024 = 1 vCPU)"
  type        = number
  default     = 512
}

variable "ecs_task_memory" {
  description = "Memory for ECS task in MB (512, 1024, 2048, 4096, 8192)"
  type        = number
  default     = 1024
}

variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}

variable "ecs_min_capacity" {
  description = "Minimum number of ECS tasks for auto-scaling"
  type        = number
  default     = 1
}

variable "ecs_max_capacity" {
  description = "Maximum number of ECS tasks for auto-scaling"
  type        = number
  default     = 4
}

# -----------------------------------------------------------------------------
# S3 Configuration
# -----------------------------------------------------------------------------

variable "s3_discovery_bucket_name" {
  description = "Name for discovery data S3 bucket"
  type        = string
  default     = "" # Auto-generated if empty
}

variable "s3_artifacts_bucket_name" {
  description = "Name for artifacts S3 bucket"
  type        = string
  default     = "" # Auto-generated if empty
}

variable "s3_logs_bucket_name" {
  description = "Name for logs S3 bucket"
  type        = string
  default     = "" # Auto-generated if empty
}

variable "s3_lifecycle_days" {
  description = "Days before moving S3 objects to Glacier (cost optimization)"
  type        = number
  default     = 90
}

variable "s3_expiration_days" {
  description = "Days before deleting old S3 objects"
  type        = number
  default     = 730 # 2 years
}

# -----------------------------------------------------------------------------
# DynamoDB Configuration
# -----------------------------------------------------------------------------

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode (PROVISIONED or PAY_PER_REQUEST)"
  type        = string
  default     = "PAY_PER_REQUEST" # Recommended for variable workloads
}

variable "dynamodb_read_capacity" {
  description = "Read capacity units (only used if billing_mode = PROVISIONED)"
  type        = number
  default     = 5
}

variable "dynamodb_write_capacity" {
  description = "Write capacity units (only used if billing_mode = PROVISIONED)"
  type        = number
  default     = 5
}

variable "dynamodb_point_in_time_recovery" {
  description = "Enable point-in-time recovery for DynamoDB (recommended for production)"
  type        = bool
  default     = false # Set true for production
}

# -----------------------------------------------------------------------------
# Bedrock Configuration
# -----------------------------------------------------------------------------

variable "bedrock_model_id" {
  description = "Bedrock model ID to use for AI inference"
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20240620-v2:0"
}

variable "bedrock_claude_models" {
  description = "List of Claude models to grant access to"
  type        = list(string)
  default = [
    "anthropic.claude-3-5-sonnet-20240620-v2:0",
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-7-sonnet-20250219-v1:0"
  ]
}

variable "bedrock_model_region" {
  description = "AWS region where Bedrock model is available"
  type        = string
  default     = "eu-central-1"
}

# -----------------------------------------------------------------------------
# CloudWatch Configuration
# -----------------------------------------------------------------------------

variable "cloudwatch_log_retention_days" {
  description = "Days to retain CloudWatch logs"
  type        = number
  default     = 7 # Cost optimization (use 30 for production)
}

variable "cloudwatch_retention_days" {
  description = "Alias for cloudwatch_log_retention_days"
  type        = number
  default     = 7
}

variable "enable_cloudwatch_encryption" {
  description = "Enable KMS encryption for CloudWatch Logs"
  type        = bool
  default     = false # Set to true for production
}

variable "cloudwatch_alarm_email" {
  description = "Email address for CloudWatch alarm notifications"
  type        = string
  default     = "alerts@nagarro.com"
}

variable "enable_cost_alarms" {
  description = "Enable cost anomaly detection and alerts"
  type        = bool
  default     = false # Set to true for production
}

variable "cost_alert_email" {
  description = "Email address for cost alerts"
  type        = string
  default     = ""
}

variable "cost_anomaly_threshold" {
  description = "Dollar threshold for cost anomaly alerts"
  type        = number
  default     = 100
}

variable "enable_bedrock_logging" {
  description = "Enable detailed Bedrock model invocation logging"
  type        = bool
  default     = false
}

# -----------------------------------------------------------------------------
# Cost Optimization Flags
# -----------------------------------------------------------------------------

variable "enable_cost_optimization" {
  description = "Enable cost optimization features (use free tier alternatives)"
  type        = bool
  default     = true
}

variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring and dashboards"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automated backups (increases cost)"
  type        = bool
  default     = false # Set true for production
}

# -----------------------------------------------------------------------------
# Security Configuration
# -----------------------------------------------------------------------------

variable "allowed_ip_ranges" {
  description = "List of IP CIDR ranges allowed to access resources"
  type        = list(string)
  default     = ["0.0.0.0/0"] # WARNING: Open to world - restrict in production
}

variable "enable_encryption" {
  description = "Enable encryption for S3 and DynamoDB"
  type        = bool
  default     = true
}

variable "kms_key_deletion_window" {
  description = "Days before KMS key is deleted after destruction"
  type        = number
  default     = 7
}

# -----------------------------------------------------------------------------
# Lambda Configuration
# -----------------------------------------------------------------------------

variable "lambda_package_path" {
  description = "Path to Lambda deployment package (ZIP file)"
  type        = string
  default     = "../lambda/deployment.zip"
}

variable "lambda_layer_path" {
  description = "Path to Lambda layer package (ZIP file with dependencies)"
  type        = string
  default     = "../lambda/layer.zip"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300 # 5 minutes
}

variable "lambda_memory_size" {
  description = "Lambda function memory in MB"
  type        = number
  default     = 1024
}

variable "lambda_max_retry_attempts" {
  description = "Maximum retry attempts for Lambda invocations"
  type        = number
  default     = 2
}

variable "lambda_max_event_age" {
  description = "Maximum age of event in seconds before Lambda discards it"
  type        = number
  default     = 3600 # 1 hour
}

variable "enable_lambda_vpc" {
  description = "Deploy Lambda functions in VPC (increases cost, adds cold start latency)"
  type        = bool
  default     = false # Disable for cost optimization
}

variable "enable_lambda_urls" {
  description = "Enable Lambda function URLs for direct HTTPS invocation"
  type        = bool
  default     = false # Use API Gateway instead
}

# -----------------------------------------------------------------------------
# API Gateway Configuration
# -----------------------------------------------------------------------------

variable "api_cors_origins" {
  description = "CORS allowed origins for API Gateway"
  type        = list(string)
  default     = ["*"] # Restrict in production
}

variable "api_throttle_burst_limit" {
  description = "API Gateway throttle burst limit"
  type        = number
  default     = 100
}

variable "api_throttle_rate_limit" {
  description = "API Gateway throttle rate limit (requests per second)"
  type        = number
  default     = 50
}

variable "api_auth_type" {
  description = "API Gateway authorization type (NONE, JWT, AWS_IAM)"
  type        = string
  default     = "NONE" # Set to JWT or AWS_IAM for production

  validation {
    condition     = contains(["NONE", "JWT", "AWS_IAM"], var.api_auth_type)
    error_message = "API auth type must be NONE, JWT, or AWS_IAM"
  }
}

variable "jwt_audience" {
  description = "JWT audience for API Gateway authorizer"
  type        = string
  default     = ""
}

variable "jwt_issuer" {
  description = "JWT issuer for API Gateway authorizer"
  type        = string
  default     = ""
}

variable "api_custom_domain" {
  description = "Custom domain name for API Gateway"
  type        = string
  default     = "" # Leave empty to use default AWS domain
}

variable "api_certificate_arn" {
  description = "ACM certificate ARN for custom domain"
  type        = string
  default     = ""
}

variable "enable_api_keys" {
  description = "Enable API keys for client authentication"
  type        = bool
  default     = false
}

variable "api_key_clients" {
  description = "Map of client names to descriptions for API keys"
  type        = map(string)
  default     = {}
}

# -----------------------------------------------------------------------------
# Dashboard Domain Configuration
# -----------------------------------------------------------------------------

variable "dashboard_domain_name" {
  description = "Custom domain name for the Dashboard (e.g. nagarro.aims.de)"
  type        = string
  default     = "" # Leave empty to use ALB default domain
}

variable "route53_zone_id" {
  description = "Route53 hosted zone ID for the domain"
  type        = string
  default     = "" # Required if dashboard_domain_name is set
}

variable "acm_certificate_arn" {
  description = "Existing ACM certificate ARN (if you have one). Leave empty to create new."
  type        = string
  default     = ""
}

# =============================================================================
# Notes:
# =============================================================================
# - Create terraform.tfvars to override defaults:
#     environment = "production"
#     ecs_task_memory = 2048
#     enable_backup = true
#
# - Use different values per environment:
#     dev.tfvars
#     staging.tfvars
#     production.tfvars
#
# - Apply with: terraform apply -var-file="production.tfvars"
# =============================================================================
