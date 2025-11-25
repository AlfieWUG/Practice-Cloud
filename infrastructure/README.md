# Agentic AI Services Platform - Infrastructure

Complete Infrastructure as Code (IaC) for deploying the Agentic AI Services Platform to AWS using Terraform.

## Architecture Overview

The platform deploys 24 AI agents organized in 4 migration phases:

- **Discovery Phase** (8 agents): Infrastructure scanning, application profiling, data discovery, etc.
- **Assessment Phase** (5 agents): Dependency mapping, compliance checking, cost estimation, etc.
- **Execution Phase** (6 agents): Infrastructure provisioning, data/app migration, testing, etc.
- **Optimization Phase** (5 agents): Performance/cost optimization, security hardening, monitoring, documentation

## Infrastructure Components

### Core Services

1. **Lambda Functions** - 24 serverless functions (one per agent)
2. **API Gateway** - HTTP API for REST endpoints
3. **S3 Buckets** - Discovery data, artifacts, and logs
4. **DynamoDB** - Agent state, workflow history, project metadata
5. **EventBridge** - Event-driven agent orchestration
6. **CloudWatch** - Logging, monitoring, and alerting
7. **AWS Bedrock** - AI/ML inference with Claude models
8. **VPC** - Optional isolated network environment
9. **IAM** - Roles and policies for secure access
10. **ECS** - Container orchestration (optional)

### Cost Optimization

- Lambda functions (pay per invocation)
- API Gateway HTTP API (cheaper than REST API)
- DynamoDB on-demand pricing
- S3 lifecycle policies (Glacier transition)
- No NAT Gateway by default
- Lambda outside VPC (faster cold starts)
- 7-day CloudWatch log retention

**Estimated Monthly Cost:** $50-150 for dev/test (varies with usage)

## Directory Structure

```
infrastructure/
├── terraform/           # Terraform IaC
│   ├── main.tf         # Main configuration
│   ├── providers.tf    # AWS provider setup
│   ├── variables.tf    # Input variables
│   ├── outputs.tf      # Output values
│   ├── vpc.tf          # VPC networking
│   ├── iam.tf          # IAM roles/policies
│   ├── s3.tf           # S3 buckets
│   ├── dynamodb.tf     # DynamoDB tables
│   ├── lambda.tf       # Lambda functions
│   ├── api_gateway.tf  # API Gateway
│   ├── eventbridge.tf  # Event bus
│   ├── cloudwatch.tf   # Monitoring
│   ├── bedrock.tf      # Bedrock access
│   └── ecs.tf          # ECS cluster (optional)
│
└── lambda/             # Lambda deployment
    ├── handler.py      # Unified Lambda handler
    ├── build.sh        # Build script
    ├── .gitignore      # Ignore build artifacts
    └── README.md       # Lambda docs
```

## Prerequisites

Before deploying:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured: `aws configure`
3. **Terraform** >= 1.5.0: `brew install terraform`
4. **Python** 3.11+: `brew install python@3.11`
5. **Bedrock Model Access** - Request access in AWS Console:
   - anthropic.claude-3-5-sonnet-20240620-v2:0
   - anthropic.claude-3-5-sonnet-20241022-v2:0
   - anthropic.claude-3-7-sonnet-20250219-v1:0

## Quick Start

### 1. Build Lambda Packages

```bash
cd lambda
./build.sh
```

This creates:
- `layer.zip` - Dependencies (boto3, anthropic, etc.)
- `deployment.zip` - Application code

### 2. Configure Terraform

Create `terraform/terraform.tfvars`:

```hcl
environment    = "dev"
aws_region     = "eu-central-1"
owner_email    = "your.email@nagarro.com"

# Enable features as needed
enable_monitoring         = true
enable_cost_optimization  = true
enable_cloudwatch_encryption = false
enable_cost_alarms        = false

# Lambda configuration
lambda_timeout      = 300
lambda_memory_size  = 1024

# API Gateway
api_auth_type       = "NONE"  # Change to "JWT" or "AWS_IAM" for production
api_cors_origins    = ["*"]   # Restrict in production
```

### 3. Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy
terraform apply
```

### 4. Get Deployment Information

```bash
# View all outputs
terraform output

# Get API endpoint
terraform output api_gateway_endpoint

# Get specific output
terraform output -json connection_info
```

## API Endpoints

After deployment, the API Gateway provides:

### Health Check
```bash
curl https://{api-id}.execute-api.eu-central-1.amazonaws.com/prod/health
```

### List All Agents
```bash
curl https://{api-id}.execute-api.eu-central-1.amazonaws.com/prod/agents
```

### Execute Agent
```bash
curl -X POST https://{api-id}.execute-api.eu-central-1.amazonaws.com/prod/agents/infrastructure-scanner \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my-migration",
    "environment": "production",
    "target_cloud": "aws"
  }'
```

### Get Agent Status
```bash
curl https://{api-id}.execute-api.eu-central-1.amazonaws.com/prod/agents/infrastructure-scanner/status?project_id=my-migration
```

## Configuration

### Variables

Key variables in `terraform/variables.tf`:

| Variable | Description | Default |
|----------|-------------|---------|
| `environment` | Environment name (dev/staging/prod) | `dev` |
| `aws_region` | AWS region | `eu-central-1` |
| `vpc_cidr` | VPC CIDR block | `10.0.0.0/16` |
| `lambda_timeout` | Lambda timeout (seconds) | `300` |
| `lambda_memory_size` | Lambda memory (MB) | `1024` |
| `api_auth_type` | API auth (NONE/JWT/AWS_IAM) | `NONE` |
| `enable_monitoring` | Enable CloudWatch monitoring | `true` |
| `enable_cost_optimization` | Use cost-optimized settings | `true` |

### Environments

Create environment-specific tfvars files:

**dev.tfvars**
```hcl
environment = "dev"
ecs_desired_count = 1
lambda_memory_size = 512
enable_backup = false
```

**prod.tfvars**
```hcl
environment = "production"
ecs_desired_count = 3
lambda_memory_size = 2048
enable_backup = true
enable_cloudwatch_encryption = true
enable_cost_alarms = true
cost_alert_email = "ops@nagarro.com"
api_auth_type = "JWT"
```

Deploy with:
```bash
terraform apply -var-file="prod.tfvars"
```

## Monitoring

### CloudWatch Logs

- Lambda logs: `/aws/lambda/nagarro-agentic-{env}-{agent-name}`
- API Gateway logs: `/aws/apigateway/nagarro-agentic-{env}`
- ECS logs: `/ecs/nagarro-agentic-{env}`

### CloudWatch Dashboards

Access dashboard: AWS Console > CloudWatch > Dashboards > `nagarro-agentic-{env}-dashboard`

### Alarms

- ECS CPU/Memory high
- DynamoDB throttling
- API Gateway 4XX/5XX errors
- Cost anomaly detection (if enabled)

## Security

### IAM Roles

- **Lambda Execution Role**: Access to Bedrock, S3, DynamoDB, EventBridge
- **ECS Task Role**: Same as Lambda
- **ECS Task Execution Role**: Pull images, write logs

### Encryption

- S3: AES-256 encryption at rest
- DynamoDB: AWS managed encryption
- CloudWatch: Optional KMS encryption
- All data encrypted in transit (TLS)

### Network Security

- Public access blocked on all S3 buckets
- Security groups restrict ECS task access
- VPC isolation optional (disabled by default for cost)
- API Gateway CORS configurable

### Best Practices

1. **Enable encryption** in production: `enable_cloudwatch_encryption = true`
2. **Use JWT or IAM auth**: `api_auth_type = "JWT"`
3. **Restrict CORS**: `api_cors_origins = ["https://yourdomain.com"]`
4. **Enable backups**: `enable_backup = true`
5. **Monitor costs**: `enable_cost_alarms = true`
6. **Rotate credentials** regularly
7. **Review IAM policies** periodically

## Troubleshooting

### Terraform Init Fails

```bash
# Clear cache
rm -rf .terraform .terraform.lock.hcl

# Reinitialize
terraform init
```

### Terraform Apply Fails

```bash
# Check AWS credentials
aws sts get-caller-identity

# Validate configuration
terraform validate

# Check specific resource
terraform plan -target=aws_lambda_function.agents
```

### Lambda Build Fails

```bash
# Update pip
pip install --upgrade pip

# Clean and rebuild
cd lambda
rm -rf build/ *.zip
./build.sh
```

### Lambda Invocation Fails

1. Check CloudWatch logs
2. Verify IAM permissions
3. Check environment variables
4. Review dead letter queue

### API Gateway 500 Errors

1. Check Lambda execution logs
2. Verify Lambda function exists
3. Test Lambda directly: `aws lambda invoke --function-name {name} out.json`
4. Check API Gateway integration

## Maintenance

### Update Lambda Code

```bash
# Rebuild packages
cd lambda
./build.sh

# Redeploy Lambda functions
cd ../terraform
terraform apply -target=aws_lambda_function.agents
```

### Update Terraform Version

```bash
# Upgrade providers
terraform init -upgrade

# Test
terraform plan
```

### Backup State

```bash
# Backup state file
cp terraform.tfstate terraform.tfstate.backup.$(date +%Y%m%d)

# Or use remote state (recommended)
# Configure in providers.tf:
terraform {
  backend "s3" {
    bucket = "your-terraform-state"
    key    = "agentic-services/terraform.tfstate"
    region = "eu-central-1"
  }
}
```

### Cost Monitoring

```bash
# Check current month costs
aws ce get-cost-and-usage \
  --time-period Start=2024-03-01,End=2024-03-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE

# Set budget alert
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://budget.json
```

## Destroying Infrastructure

**⚠️ WARNING: This will delete all resources and data!**

```bash
cd terraform

# Preview what will be deleted
terraform plan -destroy

# Destroy everything
terraform destroy
```

To keep data:
```bash
# Remove lifecycle rule from important resources in Terraform files
# Then destroy
terraform destroy
```

## References

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [AWS API Gateway v2 Docs](https://docs.aws.amazon.com/apigateway/)
- [AWS Bedrock User Guide](https://docs.aws.amazon.com/bedrock/)
- [Project README](../README.md)
- [Lambda Infrastructure README](lambda/README.md)

## Support

For issues or questions:
1. Check logs in CloudWatch
2. Review Terraform documentation
3. Consult AWS service documentation
4. Contact your DevOps team
