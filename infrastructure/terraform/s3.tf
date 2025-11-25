# =============================================================================
# S3 Buckets
# =============================================================================
# Creates three S3 buckets:
# 1. Discovery Bucket - Stores discovery analysis results
# 2. Artifacts Bucket - Stores generated code and documentation
# 3. Logs Bucket - Stores application and access logs
#
# Features:
# - Encryption at rest (AES-256)
# - Versioning enabled
# - Lifecycle policies for cost optimization
# - Public access blocked
# - Server access logging
# =============================================================================

# -----------------------------------------------------------------------------
# Discovery Data Bucket
# -----------------------------------------------------------------------------

resource "aws_s3_bucket" "discovery" {
  bucket = local.discovery_bucket_name

  tags = merge(
    local.common_tags,
    {
      Name    = local.discovery_bucket_name
      Purpose = "discovery-data"
    }
  )
}

resource "aws_s3_bucket_versioning" "discovery" {
  bucket = aws_s3_bucket.discovery.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "discovery" {
  bucket = aws_s3_bucket.discovery.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "discovery" {
  bucket = aws_s3_bucket.discovery.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "discovery" {
  bucket = aws_s3_bucket.discovery.id

  rule {
    id     = "transition-to-glacier"
    status = "Enabled"

    filter {}

    transition {
      days          = var.s3_lifecycle_days
      storage_class = "GLACIER"
    }

    expiration {
      days = var.s3_expiration_days
    }
  }
}

# -----------------------------------------------------------------------------
# Artifacts Bucket
# -----------------------------------------------------------------------------

resource "aws_s3_bucket" "artifacts" {
  bucket = local.artifacts_bucket_name

  tags = merge(
    local.common_tags,
    {
      Name    = local.artifacts_bucket_name
      Purpose = "generated-artifacts"
    }
  )
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    id     = "transition-to-glacier"
    status = "Enabled"

    filter {}

    transition {
      days          = var.s3_lifecycle_days
      storage_class = "GLACIER"
    }

    expiration {
      days = var.s3_expiration_days
    }
  }
}

# -----------------------------------------------------------------------------
# Logs Bucket
# -----------------------------------------------------------------------------

resource "aws_s3_bucket" "logs" {
  bucket = local.logs_bucket_name

  tags = merge(
    local.common_tags,
    {
      Name    = local.logs_bucket_name
      Purpose = "application-logs"
    }
  )
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "expire-old-logs"
    status = "Enabled"

    filter {}

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    expiration {
      days = 90 # Delete logs after 90 days
    }
  }
}

# =============================================================================
# Cost Optimization Notes
# =============================================================================
# 1. Lifecycle policies move objects to Glacier after var.s3_lifecycle_days
#    - Glacier is 90% cheaper than S3 Standard
#    - Default: 90 days
#
# 2. Objects are deleted after var.s3_expiration_days
#    - Default: 730 days (2 years)
#    - Logs are deleted after 90 days
#
# 3. VPC Endpoints (in vpc.tf) avoid NAT Gateway charges for S3 traffic
#
# 4. Estimated costs (development):
#    - Storage: ~$5-10/month (under 100 GB)
#    - Requests: ~$1/month
#    - Total: ~$6-11/month
# =============================================================================
