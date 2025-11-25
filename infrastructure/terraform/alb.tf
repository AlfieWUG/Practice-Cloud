# =============================================================================
# Application Load Balancer (ALB)
# =============================================================================
# Provides public HTTPS access to the Streamlit Dashboard running on ECS
# Supports custom domain configuration
# =============================================================================

# -----------------------------------------------------------------------------
# Application Load Balancer
# -----------------------------------------------------------------------------
resource "aws_lb" "main" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection       = var.environment == "production" ? true : false
  enable_http2                     = true
  enable_cross_zone_load_balancing = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb"
  })
}

# -----------------------------------------------------------------------------
# Target Group for ECS Dashboard Service
# -----------------------------------------------------------------------------
resource "aws_lb_target_group" "dashboard" {
  name        = "${local.name_prefix}-dashboard-tg"
  port        = 8501
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/_stcore/health"
    protocol            = "HTTP"
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-dashboard-tg"
  })
}

# -----------------------------------------------------------------------------
# HTTP Listener (redirect to HTTPS)
# -----------------------------------------------------------------------------
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# -----------------------------------------------------------------------------
# HTTPS Listener
# -----------------------------------------------------------------------------
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_certificate_arn != "" ? var.acm_certificate_arn : aws_acm_certificate.dashboard[0].arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.dashboard.arn
  }

  depends_on = [aws_acm_certificate_validation.dashboard]
}

# -----------------------------------------------------------------------------
# Security Group for ALB
# -----------------------------------------------------------------------------
resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  # Allow inbound HTTP from anywhere
  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow inbound HTTPS from anywhere
  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-sg"
  })
}

# -----------------------------------------------------------------------------
# Update ECS Security Group to allow traffic from ALB
# -----------------------------------------------------------------------------
resource "aws_security_group_rule" "ecs_allow_alb" {
  type                     = "ingress"
  from_port                = 8501
  to_port                  = 8501
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecs_tasks.id
  source_security_group_id = aws_security_group.alb.id
  description              = "Allow inbound from ALB to Streamlit Dashboard"
}

# =============================================================================
# ACM Certificate (SSL/TLS)
# =============================================================================

# Certificate for custom domain (if provided)
resource "aws_acm_certificate" "dashboard" {
  count             = var.dashboard_domain_name != "" && var.acm_certificate_arn == "" ? 1 : 0
  domain_name       = var.dashboard_domain_name
  validation_method = "DNS"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-dashboard-cert"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Certificate validation
resource "aws_acm_certificate_validation" "dashboard" {
  count                   = var.dashboard_domain_name != "" && var.acm_certificate_arn == "" ? 1 : 0
  certificate_arn         = aws_acm_certificate.dashboard[0].arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# =============================================================================
# Route53 DNS Configuration
# =============================================================================

# Create DNS record for certificate validation
resource "aws_route53_record" "cert_validation" {
  for_each = var.dashboard_domain_name != "" && var.acm_certificate_arn == "" ? {
    for dvo in aws_acm_certificate.dashboard[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = var.route53_zone_id
}

# Create A record pointing to ALB
resource "aws_route53_record" "dashboard" {
  count   = var.dashboard_domain_name != "" && var.route53_zone_id != "" ? 1 : 0
  zone_id = var.route53_zone_id
  name    = var.dashboard_domain_name
  type    = "A"

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}
