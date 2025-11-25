# =============================================================================
# Terraform & Provider Configuration
# =============================================================================
# Defines Terraform version and AWS provider settings
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# =============================================================================
# AWS Provider Configuration
# =============================================================================
# Configures AWS connection using credentials from:
# 1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
# 2. AWS CLI config (~/.aws/credentials)
# 3. IAM role (if running on EC2)
# =============================================================================

provider "aws" {
  region = var.aws_region

  # Default tags applied to all resources
  default_tags {
    tags = {
      Project     = "nagarro-agentic-services"
      Environment = var.environment
      ManagedBy   = "terraform"
      Owner       = var.owner_email
      CostCenter  = "cloud-migration"
    }
  }
}

# =============================================================================
# Notes:
# =============================================================================
# - Make sure AWS CLI is configured: aws configure
# - Test connection: aws sts get-caller-identity
# - Region is set via variable (default: eu-central-1)
# - All resources automatically get tagged with Project, Environment, etc.
# =============================================================================
