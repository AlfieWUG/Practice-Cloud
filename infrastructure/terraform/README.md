# Agentic Services - AWS Infrastructure as Code (Terraform)

This directory contains all the Terraform configuration files needed to deploy the Agentic Services platform to AWS.

## 📁 File Structure

```
infrastructure/terraform/
├── backend.tf           # Remote state configuration (S3 + DynamoDB)
├── providers.tf         # AWS provider configuration
├── variables.tf         # Input variables and validation
├── main.tf              # Main configuration and locals
├── outputs.tf           # Output values after deployment
├── vpc.tf               # VPC, subnets, NAT, security groups
├── s3.tf                # S3 buckets for discovery, artifacts, logs
├── dynamodb.tf          # DynamoDB tables for state and workflow
├── iam.tf               # IAM roles and policies (least privilege)
├── ecs.tf               # ECS Fargate cluster, task, service
├── eventbridge.tf       # Event bus for agent coordination
├── bedrock.tf           # Bedrock model access configuration
├── cloudwatch.tf        # Monitoring, alarms, dashboards
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** installed and configured:
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, and region
   ```

2. **Terraform** installed (version 1.0+):
   ```bash
   terraform version
   ```

3. **AWS Account Requirements**:
   - Active AWS account with billing enabled
   - IAM permissions to create: VPC, ECS, S3, DynamoDB, IAM, EventBridge, Bedrock, CloudWatch
   - Bedrock model access enabled (see Bedrock setup below)

### Step 1: Setup Remote State Backend (One-time)

Before deploying, create the S3 bucket and DynamoDB table for Terraform state:

```bash
cd infrastructure/terraform

# Create S3 bucket for state (replace with your unique bucket name)
aws s3api create-bucket \
  --bucket agentic-services-terraform-state-<your-account-id> \
  --region us-east-1

# Enable versioning on state bucket
aws s3api put-bucket-versioning \
  --bucket agentic-services-terraform-state-<your-account-id> \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name agentic-services-terraform-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

Then update `backend.tf` with your bucket name and region.

### Step 2: Enable Bedrock Model Access (One-time)

Navigate to AWS Console → Bedrock → Model access:
1. Request access for:
   - `anthropic.claude-3-5-sonnet-20240620-v2:0`
   - `anthropic.claude-3-5-sonnet-20241022-v2:0`
   - `anthropic.claude-3-7-sonnet-20250219-v1:0`
2. Access is usually granted instantly for Claude models

### Step 3: Customize Variables

Create a `terraform.tfvars` file to override defaults:

```hcl
# terraform.tfvars
project_name = "agentic-services"
environment  = "dev"
aws_region   = "us-east-1"

# Networking
vpc_cidr             = "10.0.0.0/16"
availability_zones   = ["us-east-1a", "us-east-1b"]

# ECS Configuration
ecs_task_cpu         = 512
ecs_task_memory      = 1024
ecs_desired_count    = 1

# Cost Controls
enable_cost_alarms      = true
cost_alert_email        = "your-email@example.com"
cost_anomaly_threshold  = 50.0

# Monitoring
cloudwatch_retention_days = 7
```

### Step 4: Deploy Infrastructure

```bash
# Initialize Terraform (download providers and modules)
terraform init

# Review planned changes
terraform plan

# Apply configuration (create resources)
terraform apply

# When prompted, type 'yes' to confirm
```

The deployment will take approximately **5-10 minutes**.

### Step 5: Verify Deployment

After successful deployment, Terraform will output important resource information:

```bash
# View outputs
terraform output

# Expected outputs:
# - VPC ID, Subnet IDs, Security Groups
# - ECS Cluster, Service, Task Definition ARNs
# - S3 Bucket Names
# - DynamoDB Table Names
# - IAM Role ARNs
# - EventBridge Bus ARN
# - CloudWatch Dashboard URL
```

## 📊 Architecture Overview

### Network Architecture

```
┌─────────────────────────────────────────────────────┐
│                    AWS Cloud                        │
│  ┌─────────────────────────────────────────────┐   │
│  │              VPC (10.0.0.0/16)              │   │
│  │                                             │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  │   │
│  │  │  Public Subnet  │  │  Public Subnet  │  │   │
│  │  │  (AZ-A)         │  │  (AZ-B)         │  │   │
│  │  │  - NAT Gateway  │  │  - NAT Gateway  │  │   │
│  │  └────────┬────────┘  └────────┬────────┘  │   │
│  │           │                    │           │   │
│  │  ┌────────▼────────┐  ┌────────▼────────┐  │   │
│  │  │ Private Subnet  │  │ Private Subnet  │  │   │
│  │  │  (AZ-A)         │  │  (AZ-B)         │  │   │
│  │  │  - ECS Tasks    │  │  - ECS Tasks    │  │   │
│  │  └─────────────────┘  └─────────────────┘  │   │
│  │                                             │   │
│  │  VPC Endpoints: S3, DynamoDB                │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  External Services:                                 │
│  - S3 Buckets (Discovery, Artifacts, Logs)         │
│  - DynamoDB Tables (AgentStates, Workflow)         │
│  - EventBridge (Agent Coordination)                │
│  - Bedrock (Claude Models)                         │
│  - CloudWatch (Monitoring & Logs)                  │
└─────────────────────────────────────────────────────┘
```

### Agent Workflow

```
User Request
    ↓
┌───────────────────────────────────────┐
│       Orchestrator (ECS Task)         │
└───────────┬───────────────────────────┘
            ↓
    ┌───────────────┐
    │  EventBridge  │ ← Coordinates agent execution
    └───────┬───────┘
            ↓
    ┌───────────────────────────────────┐
    │      Agent Execution Flow         │
    │                                   │
    │  1. DiscoveryAgent                │
    │     ↓ (emits discovery.completed) │
    │  2. AnalysisAgent                 │
    │     ↓ (emits analysis.completed)  │
    │  3. PlanningAgent                 │
    │     ↓ (emits planning.completed)  │
    │  4. ArtifactGenerationAgent       │
    │     ↓ (emits artifact.completed)  │
    └───────────────────────────────────┘
            ↓
    ┌───────────────┐
    │  State Store  │ (DynamoDB + S3)
    └───────────────┘
```

## 🔧 Common Operations

### Update Infrastructure

After modifying any `.tf` files:

```bash
terraform plan   # Review changes
terraform apply  # Apply changes
```

### View Current State

```bash
terraform show
terraform state list
```

### Destroy Infrastructure

**⚠️ Warning: This will delete all resources and data!**

```bash
terraform destroy
# Type 'yes' to confirm
```

### Scale ECS Service

Update `terraform.tfvars`:

```hcl
ecs_desired_count = 2  # Scale to 2 tasks
```

Then apply:

```bash
terraform apply
```

## 💰 Cost Optimization

### Free Tier Resources (First 12 months)

- **VPC**: Free (subnets, route tables, IGW)
- **NAT Gateway**: ❌ Not free (~$32/month per NAT)
- **ECS**: Free (service/cluster itself)
- **Fargate**: 400,000 vCPU-seconds + 800,000 GB-seconds free
- **S3**: 5GB storage free, 20,000 GET, 2,000 PUT requests
- **DynamoDB**: 25GB storage, 200M requests free (on-demand)
- **CloudWatch**: 5GB logs ingestion, 10 custom metrics, 10 alarms free
- **EventBridge**: 3M events/month free

### Estimated Monthly Costs (Development Environment)

| Resource | Configuration | Monthly Cost |
|----------|---------------|--------------|
| NAT Gateways (2) | High availability | ~$64 |
| ECS Fargate | 0.5 vCPU, 1GB RAM, 8hrs/day | ~$12 |
| S3 Storage | 10GB across 3 buckets | ~$0.23 |
| DynamoDB | On-demand, low usage | ~$0-5 |
| Bedrock | 1M tokens/day (~30M/month) | ~$90-450 |
| CloudWatch | Logs + Metrics + Alarms | ~$5 |
| **Total** | | **~$170-540/month** |

### Cost Reduction Tips

1. **Remove NAT Gateways** (for dev):
   - Set `enable_nat_gateway = false` in `vpc.tf`
   - Use VPC endpoints only (already configured)
   - Saves ~$64/month

2. **Reduce ECS Task Size**:
   - Use 256 CPU / 512 MB for testing
   - Run only when needed (scale to 0 when idle)

3. **Optimize Bedrock Usage**:
   - Cache agent responses in DynamoDB
   - Use prompt compression techniques
   - Monitor token usage in CloudWatch

4. **CloudWatch Log Retention**:
   - Set retention to 1-3 days for dev (`cloudwatch_retention_days = 1`)

5. **Enable Cost Anomaly Detection**:
   - Already configured in `cloudwatch.tf`
   - Set `enable_cost_alarms = true` and provide email

## 🔐 Security Best Practices

All resources follow AWS security best practices:

- ✅ **Least Privilege IAM**: Separate execution and task roles with minimal permissions
- ✅ **Encryption at Rest**: S3 (AES-256), DynamoDB (AWS-managed KMS)
- ✅ **Encryption in Transit**: VPC endpoints, private subnets
- ✅ **Network Isolation**: ECS tasks in private subnets only
- ✅ **VPC Endpoints**: S3 and DynamoDB traffic stays within AWS network
- ✅ **Security Groups**: Restrictive ingress/egress rules
- ✅ **S3 Bucket Policies**: Block public access, versioning enabled
- ✅ **CloudWatch Logs**: Optional KMS encryption

### Security Checklist

- [ ] Rotate AWS access keys regularly
- [ ] Enable MFA for AWS root account
- [ ] Review IAM policies in `iam.tf` for your use case
- [ ] Enable S3 access logging (optional, add to `s3.tf`)
- [ ] Configure VPC Flow Logs (optional, add to `vpc.tf`)
- [ ] Set up AWS Config for compliance (external to Terraform)

## 🧪 Testing

### Test Deployment

After deployment, verify resources:

```bash
# Check ECS service status
aws ecs describe-services \
  --cluster agentic-services-dev-cluster \
  --services agentic-services-dev-service

# Check S3 buckets
aws s3 ls | grep agentic-services

# Check DynamoDB tables
aws dynamodb list-tables --query "TableNames[?contains(@, 'agentic-services')]"

# Check EventBridge bus
aws events list-event-buses --query "EventBuses[?Name=='agentic-services-dev-event-bus']"
```

### Run Agent Workflow (Manual Test)

```bash
# Put a test event into EventBridge
aws events put-events \
  --entries '[{
    "Source": "test.manual",
    "DetailType": "agent.test",
    "Detail": "{\"test\": true}",
    "EventBusName": "agentic-services-dev-event-bus"
  }]'

# Check CloudWatch logs
aws logs tail /ecs/agentic-services-dev/application --follow
```

## 📚 Additional Resources

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Terraform State Management](https://developer.hashicorp.com/terraform/language/state)

## 🐛 Troubleshooting

### Issue: "Error: Backend initialization failed"

**Solution**: Ensure S3 bucket and DynamoDB table exist (see Step 1).

### Issue: "Error: InsufficientCapacityException"

**Solution**: Try a different availability zone or wait and retry.

### Issue: Bedrock model access denied

**Solution**: Request model access in AWS Console → Bedrock → Model access.

### Issue: High costs unexpectedly

**Solution**: Check CloudWatch cost anomaly alerts, review S3 bucket sizes, and Bedrock token usage.

### Issue: ECS tasks not starting

**Solution**: Check CloudWatch logs for task failures, verify IAM roles have correct permissions.

## 📞 Support

For issues specific to this infrastructure:
1. Check CloudWatch Logs: `/ecs/agentic-services-dev/application`
2. Review Terraform plan output before applying changes
3. Validate AWS service quotas in your account

---

**Last Updated**: 2025-01-XX  
**Terraform Version**: 1.0+  
**AWS Provider Version**: 5.0+
