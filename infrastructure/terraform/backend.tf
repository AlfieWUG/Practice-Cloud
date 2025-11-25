# =============================================================================
# Terraform Backend Configuration
# =============================================================================
# This file configures where Terraform stores its state file.
# State file tracks what resources have been created in AWS.
#
# IMPORTANT: Uncomment and configure after creating the S3 bucket manually
# =============================================================================

# Uncomment after creating S3 bucket for state storage
# terraform {
#   backend "s3" {
#     bucket         = "nagarro-agentic-terraform-state"
#     key            = "dev/terraform.tfstate"
#     region         = "eu-central-1"
#     encrypt        = true
#     dynamodb_table = "terraform-state-lock"
#   }
# }

# =============================================================================
# Setup Instructions:
# =============================================================================
# 1. Create S3 bucket manually first:
#    aws s3 mb s3://nagarro-agentic-terraform-state --region eu-central-1
#
# 2. Enable versioning:
#    aws s3api put-bucket-versioning \
#      --bucket nagarro-agentic-terraform-state \
#      --versioning-configuration Status=Enabled
#
# 3. Create DynamoDB table for state locking:
#    aws dynamodb create-table \
#      --table-name terraform-state-lock \
#      --attribute-definitions AttributeName=LockID,AttributeType=S \
#      --key-schema AttributeName=LockID,KeyType=HASH \
#      --billing-mode PAY_PER_REQUEST \
#      --region eu-central-1
#
# 4. Uncomment the backend block above
# 5. Run: terraform init
#
# NOTE: For first-time setup, you can use local state (no backend block)
#       and migrate to S3 backend later.
# =============================================================================
