# =============================================================================
# DynamoDB Tables
# =============================================================================
# Creates three DynamoDB tables:
# 1. AgentStates - Stores agent execution state
# 2. WorkflowHistory - Stores workflow execution history
# 3. ProjectMetadata - Stores project information
#
# Features:
# - On-demand billing (pay per request)
# - Encryption at rest
# - Point-in-time recovery (optional, for production)
# - Global secondary indexes for querying
# =============================================================================

# -----------------------------------------------------------------------------
# AgentStates Table
# -----------------------------------------------------------------------------
# Stores state for each agent execution

resource "aws_dynamodb_table" "agent_states" {
  name         = local.agent_states_table
  billing_mode = var.dynamodb_billing_mode
  hash_key     = "project_id"
  range_key    = "agent_id"

  # Only set read/write capacity if using PROVISIONED billing
  read_capacity  = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_read_capacity : null
  write_capacity = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_write_capacity : null

  attribute {
    name = "project_id"
    type = "S"
  }

  attribute {
    name = "agent_id"
    type = "S"
  }

  attribute {
    name = "agent_type"
    type = "S"
  }

  attribute {
    name = "updated_at"
    type = "S"
  }

  # GSI for querying by agent type
  global_secondary_index {
    name            = "AgentTypeIndex"
    hash_key        = "agent_type"
    range_key       = "updated_at"
    projection_type = "ALL"

    read_capacity  = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_read_capacity : null
    write_capacity = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_write_capacity : null
  }

  server_side_encryption {
    enabled = var.enable_encryption
  }

  point_in_time_recovery {
    enabled = var.dynamodb_point_in_time_recovery
  }

  tags = merge(
    local.common_tags,
    {
      Name = local.agent_states_table
    }
  )
}

# -----------------------------------------------------------------------------
# WorkflowHistory Table
# -----------------------------------------------------------------------------
# Stores workflow execution history and logs

resource "aws_dynamodb_table" "workflow_history" {
  name         = local.workflow_history_table
  billing_mode = var.dynamodb_billing_mode
  hash_key     = "workflow_id"
  range_key    = "timestamp"

  read_capacity  = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_read_capacity : null
  write_capacity = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_write_capacity : null

  attribute {
    name = "workflow_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "project_id"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  # GSI for querying by project
  global_secondary_index {
    name            = "ProjectIndex"
    hash_key        = "project_id"
    range_key       = "timestamp"
    projection_type = "ALL"

    read_capacity  = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_read_capacity : null
    write_capacity = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_write_capacity : null
  }

  # GSI for querying by status
  global_secondary_index {
    name            = "StatusIndex"
    hash_key        = "status"
    range_key       = "timestamp"
    projection_type = "ALL"

    read_capacity  = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_read_capacity : null
    write_capacity = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_write_capacity : null
  }

  server_side_encryption {
    enabled = var.enable_encryption
  }

  point_in_time_recovery {
    enabled = var.dynamodb_point_in_time_recovery
  }

  tags = merge(
    local.common_tags,
    {
      Name = local.workflow_history_table
    }
  )
}

# -----------------------------------------------------------------------------
# ProjectMetadata Table
# -----------------------------------------------------------------------------
# Stores project information and metadata

resource "aws_dynamodb_table" "project_metadata" {
  name         = local.project_metadata_table
  billing_mode = var.dynamodb_billing_mode
  hash_key     = "project_id"

  read_capacity  = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_read_capacity : null
  write_capacity = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_write_capacity : null

  attribute {
    name = "project_id"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  attribute {
    name = "customer_id"
    type = "S"
  }

  # GSI for querying by customer
  global_secondary_index {
    name            = "CustomerIndex"
    hash_key        = "customer_id"
    range_key       = "created_at"
    projection_type = "ALL"

    read_capacity  = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_read_capacity : null
    write_capacity = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_write_capacity : null
  }

  server_side_encryption {
    enabled = var.enable_encryption
  }

  point_in_time_recovery {
    enabled = var.dynamodb_point_in_time_recovery
  }

  tags = merge(
    local.common_tags,
    {
      Name = local.project_metadata_table
    }
  )
}

# =============================================================================
# Cost Optimization Notes
# =============================================================================
# 1. On-Demand Billing (default):
#    - Pay per request: $1.25 per million writes, $0.25 per million reads
#    - Best for unpredictable workloads
#    - Free tier: 25 GB storage, 25 RCU, 25 WCU
#
# 2. Provisioned Billing:
#    - Set var.dynamodb_billing_mode = "PROVISIONED"
#    - 50-70% cheaper for predictable workloads
#    - Requires capacity planning
#
# 3. Point-in-Time Recovery:
#    - Additional cost: ~$0.20 per GB/month
#    - Recommended for production only
#
# 4. Encryption:
#    - Free (no additional cost)
#
# 5. Estimated costs (development):
#    - Storage: Free (under 25 GB)
#    - Requests: $5-10/month
#    - Total: $5-10/month
# =============================================================================
