# AWS Lambda + API Gateway Infrastructure Deployment Guide

## What Was Built

Complete serverless infrastructure for deploying all 24 AI agents to AWS:

### ✅ Completed Infrastructure

1. **Lambda Functions** (`lambda.tf` - 365 lines)
   - 24 Lambda functions (one per agent)
   - Shared Lambda layer for dependencies
   - Dead Letter Queue (SQS) for failed invocations
   - CloudWatch log groups with 7-day retention
   - Optional VPC configuration
   - IAM execution role with Bedrock, S3, DynamoDB, EventBridge permissions

2. **API Gateway** (`api_gateway.tf` - 353 lines)
   - HTTP API (cheaper than REST API)
   - Routes for all 24 agents:
     - `POST /agents/{agent-name}` - Execute agent
     - `GET /agents/{agent-name}/status` - Get agent status
   - Utility endpoints:
     - `GET /health` - Health check
     - `GET /agents` - List all agents
   - CloudWatch logging and alarms (4XX/5XX errors)
   - Optional JWT authorizer
   - Optional custom domain support
   - CORS configuration

3. **Lambda Handler** (`lambda/handler.py` - 467 lines)
   - Unified handler for all 24 agents
   - Supports API Gateway, EventBridge, and direct invocations
   - Individual handler functions per agent
   - Health checks and agent listing
   - Error handling and logging

4. **Build System** (`lambda/build.sh`)
   - Automated Lambda packaging
   - Dependencies layer creation
   - Size optimization (removes tests, cache)

5. **Variables** (`variables.tf` - updated)
   - Lambda configuration (timeout, memory, VPC, URLs)
   - API Gateway configuration (CORS, throttling, auth)
   - CloudWatch and cost monitoring settings

6. **Outputs** (`outputs.tf` - updated)
   - Lambda function ARNs
   - API Gateway endpoints
   - Connection information

7. **Documentation**
   - Infrastructure README
   - Lambda README
   - Deployment guide (this file)

### Infrastructure Statistics

```
Total Terraform files: 12
Total lines of code: ~3,400
Lambda functions: 24
API routes: 48+ (2 per agent + utilities)
S3 buckets: 3
DynamoDB tables: 3
IAM roles: 4
CloudWatch log groups: 26+
EventBridge event bus: 1
```

## Deployment Steps

### Step 1: Prerequisites

Ensure you have:
- [ ] AWS account with admin access
- [ ] AWS CLI configured: `aws sts get-caller-identity`
- [ ] Terraform >= 1.5.0: `terraform version`
- [ ] Python 3.11+: `python3 --version`
- [ ] Bedrock model access requested in AWS Console

### Step 2: Build Lambda Packages

```bash
cd /Users/aaldertoosthuizen/Projects/agentic-services/infrastructure/lambda
./build.sh
```

Expected output:
```
🚀 Building Lambda packages...
📦 Building dependencies layer...
✅ Dependencies layer created: layer.zip (50-100 MB)
📦 Building deployment package...
✅ Deployment package created: deployment.zip (5-10 MB)
```

### Step 3: Configure Terraform

Create `/Users/aaldertoosthuizen/Projects/agentic-services/infrastructure/terraform/terraform.tfvars`:

```hcl
# Basic configuration
environment = "dev"
aws_region  = "eu-central-1"
owner_email = "your.email@nagarro.com"

# Lambda configuration
lambda_timeout     = 300   # 5 minutes
lambda_memory_size = 1024  # 1 GB

# API Gateway
api_auth_type    = "NONE"  # Use "JWT" or "AWS_IAM" for production
api_cors_origins = ["*"]   # Restrict in production

# Cost optimization
enable_cost_optimization     = true
enable_cloudwatch_encryption = false
enable_cost_alarms           = false
```

### Step 4: Initialize Terraform

```bash
cd /Users/aaldertoosthuizen/Projects/agentic-services/infrastructure/terraform
terraform init
```

Expected output:
```
Initializing provider plugins...
- Installing hashicorp/aws v5.100.0...
Terraform has been successfully initialized!
```

### Step 5: Validate Configuration

```bash
terraform validate
```

Expected output:
```
Success! The configuration is valid.
```

### Step 6: Preview Changes

```bash
terraform plan
```

This will show:
- ~100+ resources to create
- S3 buckets, DynamoDB tables, Lambda functions, etc.
- No resources to destroy or modify (first deployment)

### Step 7: Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted. Deployment takes 5-10 minutes.

### Step 8: Verify Deployment

```bash
# Get API endpoint
export API_ENDPOINT=$(terraform output -raw api_gateway_endpoint)

# Test health check
curl $API_ENDPOINT/health

# List agents
curl $API_ENDPOINT/agents

# Test agent execution
curl -X POST $API_ENDPOINT/agents/infrastructure-scanner \
  -H "Content-Type: application/json" \
  -d '{"project_id": "test", "environment": "dev"}'
```

## Testing

### Manual Testing

```bash
# Set API endpoint
API_ENDPOINT=$(terraform output -raw api_gateway_endpoint)

# 1. Health check
curl $API_ENDPOINT/health | jq

# 2. List all agents
curl $API_ENDPOINT/agents | jq

# 3. Execute Discovery Phase agent
curl -X POST $API_ENDPOINT/agents/infrastructure-scanner \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test-migration",
    "environment": "production",
    "scan_scope": "compute"
  }' | jq

# 4. Check agent status
curl "$API_ENDPOINT/agents/infrastructure-scanner/status?project_id=test-migration" | jq

# 5. Execute Assessment Phase agent
curl -X POST $API_ENDPOINT/agents/cost-estimator \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test-migration",
    "target_cloud": "aws",
    "region": "eu-central-1"
  }' | jq
```

### Load Testing (Optional)

```bash
# Install artillery
npm install -g artillery

# Create test scenario
cat > load-test.yml <<EOF
config:
  target: $API_ENDPOINT
  phases:
    - duration: 60
      arrivalRate: 5
scenarios:
  - name: "Health check"
    flow:
      - get:
          url: "/health"
EOF

# Run load test
artillery run load-test.yml
```

## Monitoring

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/nagarro-agentic-dev-infrastructure-scanner --follow

# View API Gateway logs
aws logs tail /aws/apigateway/nagarro-agentic-dev --follow

# View all agent logs
for agent in infrastructure-scanner application-profiler data-discovery; do
  echo "=== $agent ==="
  aws logs tail /aws/lambda/nagarro-agentic-dev-$agent --since 1h
done
```

### CloudWatch Dashboard

Access: AWS Console > CloudWatch > Dashboards > `nagarro-agentic-dev-dashboard`

### Metrics to Monitor

1. **Lambda**
   - Invocation count
   - Error rate
   - Duration
   - Concurrent executions

2. **API Gateway**
   - Request count
   - 4XX/5XX errors
   - Integration latency
   - Data processed

3. **DynamoDB**
   - Read/write capacity units
   - Throttled requests
   - System errors

## Cost Estimation

### Expected Monthly Costs (Dev Environment)

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 10K invocations/month @ 1GB, 30s avg | $5-10 |
| API Gateway | 10K requests/month | $0.10 |
| DynamoDB | On-demand, light usage | $2-5 |
| S3 | 10GB storage | $0.25 |
| CloudWatch Logs | 5GB ingestion, 7-day retention | $2.50 |
| EventBridge | 10K events | $0.10 |
| Bedrock | 100K tokens (varies by usage) | $30-50 |
| **TOTAL** | | **~$40-70/month** |

### Cost Optimization Tips

1. Reduce Lambda memory if agents don't need 1GB
2. Reduce CloudWatch log retention to 3 days
3. Use S3 Intelligent-Tiering
4. Set DynamoDB auto-scaling limits
5. Enable cost anomaly detection

## Troubleshooting

### Issue: Lambda timeout

**Symptoms:** Agent executions fail after 5 minutes

**Solution:**
```hcl
# In terraform.tfvars
lambda_timeout = 600  # Increase to 10 minutes
```

Then: `terraform apply`

### Issue: Lambda out of memory

**Symptoms:** "Runtime exited with error: signal: killed"

**Solution:**
```hcl
# In terraform.tfvars
lambda_memory_size = 2048  # Increase to 2GB
```

Then: `terraform apply`

### Issue: API Gateway 403 errors

**Symptoms:** "Missing Authentication Token"

**Cause:** Incorrect endpoint or route

**Solution:** Verify endpoint with `terraform output api_gateway_endpoint`

### Issue: Bedrock access denied

**Symptoms:** "You don't have access to the model"

**Solution:**
1. Go to AWS Console > Bedrock > Model access
2. Request access to Claude models
3. Wait for approval (usually instant)

### Issue: Build fails - dependencies too large

**Symptoms:** Lambda layer > 250MB

**Solution:**
```bash
# Use slim dependencies
pip install boto3 --target python/ --platform manylinux2014_x86_64 --only-binary=:all:
```

## Maintenance

### Update Agent Code

```bash
# 1. Make changes to agent code in src/
# 2. Rebuild Lambda package
cd infrastructure/lambda
./build.sh

# 3. Redeploy
cd ../terraform
terraform apply -target=aws_lambda_function.agents
```

### Add New Agent

1. Create agent class in `src/agentic_services/agents/`
2. Add import to `infrastructure/lambda/handler.py`
3. Add to `AGENT_REGISTRY` in handler
4. Create handler function (e.g., `new_agent_handler`)
5. Add to `local.all_agents` in `terraform/lambda.tf`
6. Rebuild and deploy

### Rollback Deployment

```bash
# View state history
terraform state list

# Rollback to previous state (if you have backup)
cp terraform.tfstate.backup terraform.tfstate
terraform apply
```

## Security Hardening (Production)

Before production deployment:

1. **Enable encryption**
   ```hcl
   enable_cloudwatch_encryption = true
   enable_encryption = true
   ```

2. **Enable authentication**
   ```hcl
   api_auth_type = "JWT"  # or "AWS_IAM"
   jwt_issuer = "https://your-auth-provider.com"
   jwt_audience = "your-api-audience"
   ```

3. **Restrict CORS**
   ```hcl
   api_cors_origins = ["https://yourdomain.com"]
   ```

4. **Enable backups**
   ```hcl
   enable_backup = true
   dynamodb_point_in_time_recovery = true
   ```

5. **Enable cost alerts**
   ```hcl
   enable_cost_alarms = true
   cost_alert_email = "ops@nagarro.com"
   cost_anomaly_threshold = 100
   ```

6. **Restrict IP access**
   ```hcl
   allowed_ip_ranges = ["YOUR_OFFICE_IP/32"]
   ```

## Next Steps

1. ✅ **Done**: Lambda + API Gateway infrastructure built
2. 🔄 **Next**: Test all 24 agents via API Gateway
3. 🔄 **Next**: Build Streamlit dashboard integration with API
4. 🔄 **Next**: Set up CI/CD pipeline for automated deployments
5. 🔄 **Next**: Configure monitoring alerts
6. 🔄 **Next**: Production deployment with hardening

## References

- [Infrastructure README](README.md) - Complete infrastructure documentation
- [Lambda README](lambda/README.md) - Lambda-specific documentation
- [Terraform Files](terraform/) - All IaC files
- [Agent Source Code](../src/agentic_services/agents/) - All 24 agents

## Support

Issues? Check:
1. CloudWatch logs for errors
2. Terraform state: `terraform state list`
3. AWS Console for resource status
4. This deployment guide for troubleshooting
