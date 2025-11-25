# =============================================================================
# VPC and Networking Infrastructure
# =============================================================================
# Creates complete network infrastructure:
# - VPC with DNS support
# - Public and private subnets across 2 availability zones
# - Internet Gateway for public internet access
# - NAT Gateway for private subnet internet access
# - Route tables and associations
# - Security groups for ECS tasks and ALB
# =============================================================================

# -----------------------------------------------------------------------------
# VPC
# -----------------------------------------------------------------------------

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-vpc"
    }
  )
}

# -----------------------------------------------------------------------------
# Internet Gateway
# -----------------------------------------------------------------------------
# Allows resources in public subnets to access the internet

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-igw"
    }
  )
}

# -----------------------------------------------------------------------------
# Public Subnets
# -----------------------------------------------------------------------------
# Subnets with direct internet access via Internet Gateway

resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-public-${var.availability_zones[count.index]}"
      Type = "public"
    }
  )
}

# -----------------------------------------------------------------------------
# Private Subnets
# -----------------------------------------------------------------------------
# Subnets for ECS tasks, no direct internet access

resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-private-${var.availability_zones[count.index]}"
      Type = "private"
    }
  )
}

# -----------------------------------------------------------------------------
# Elastic IPs for NAT Gateways
# -----------------------------------------------------------------------------

resource "aws_eip" "nat" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.availability_zones)) : 0

  domain = "vpc"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-nat-eip-${count.index + 1}"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# -----------------------------------------------------------------------------
# NAT Gateways
# -----------------------------------------------------------------------------
# Allows private subnet resources to access internet
# COST: ~$35/month per NAT Gateway

resource "aws_nat_gateway" "main" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.availability_zones)) : 0

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-nat-${count.index + 1}"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# -----------------------------------------------------------------------------
# Route Table for Public Subnets
# -----------------------------------------------------------------------------

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-public-rt"
    }
  )
}

# -----------------------------------------------------------------------------
# Route Table Associations for Public Subnets
# -----------------------------------------------------------------------------

resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# -----------------------------------------------------------------------------
# Route Tables for Private Subnets
# -----------------------------------------------------------------------------

resource "aws_route_table" "private" {
  count = var.single_nat_gateway ? 1 : length(var.availability_zones)

  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = var.single_nat_gateway ? aws_nat_gateway.main[0].id : aws_nat_gateway.main[count.index].id
    }
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-private-rt-${count.index + 1}"
    }
  )
}

# -----------------------------------------------------------------------------
# Route Table Associations for Private Subnets
# -----------------------------------------------------------------------------

resource "aws_route_table_association" "private" {
  count = length(aws_subnet.private)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = var.single_nat_gateway ? aws_route_table.private[0].id : aws_route_table.private[count.index].id
}

# -----------------------------------------------------------------------------
# Security Group for ECS Tasks
# -----------------------------------------------------------------------------
# Controls inbound/outbound traffic for ECS containers

resource "aws_security_group" "ecs_tasks" {
  name        = "${local.name_prefix}-ecs-tasks-sg"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.main.id

  # Ingress rule for HTTP (from ALB if you add one later)
  ingress {
    description = "HTTP from anywhere (restrict in production)"
    from_port   = 8501 # Streamlit default port
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = var.allowed_ip_ranges
  }

  # Allow all outbound traffic
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ecs-tasks-sg"
    }
  )
}

# -----------------------------------------------------------------------------
# VPC Endpoints (Cost Optimization)
# -----------------------------------------------------------------------------
# Avoid NAT Gateway charges for S3 and DynamoDB traffic

resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.s3"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-s3-endpoint"
    }
  )
}

resource "aws_vpc_endpoint_route_table_association" "s3_private" {
  count = length(aws_route_table.private)

  route_table_id  = aws_route_table.private[count.index].id
  vpc_endpoint_id = aws_vpc_endpoint.s3.id
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.dynamodb"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-dynamodb-endpoint"
    }
  )
}

resource "aws_vpc_endpoint_route_table_association" "dynamodb_private" {
  count = length(aws_route_table.private)

  route_table_id  = aws_route_table.private[count.index].id
  vpc_endpoint_id = aws_vpc_endpoint.dynamodb.id
}

# =============================================================================
# Network Architecture Summary
# =============================================================================
# 
# ┌─────────────────────────────────────────────────────────────────┐
# │                           Internet                               │
# └────────────────────────────┬────────────────────────────────────┘
#                              │
#                     ┌────────▼────────┐
#                     │ Internet Gateway │
#                     └────────┬────────┘
#                              │
#              ┌───────────────┴───────────────┐
#              │                               │
#     ┌────────▼────────┐           ┌────────▼────────┐
#     │ Public Subnet 1  │           │ Public Subnet 2  │
#     │  10.0.101.0/24   │           │  10.0.102.0/24   │
#     │   (AZ-1a)        │           │   (AZ-1b)        │
#     └────────┬────────┘           └────────┬────────┘
#              │                               │
#        ┌─────▼─────┐                  ┌─────▼─────┐
#        │NAT Gateway│                  │NAT Gateway│
#        └─────┬─────┘                  └─────┬─────┘
#              │                               │
#     ┌────────▼────────┐           ┌────────▼────────┐
#     │ Private Subnet 1 │           │ Private Subnet 2 │
#     │  10.0.1.0/24     │           │  10.0.2.0/24     │
#     │   (AZ-1a)        │           │   (AZ-1b)        │
#     │  [ECS Tasks]     │           │  [ECS Tasks]     │
#     └─────────────────┘           └─────────────────┘
#
# VPC Endpoints (S3, DynamoDB) → Cost savings by avoiding NAT charges
#
# =============================================================================
