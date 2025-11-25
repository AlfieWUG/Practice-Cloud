# Lambda Infrastructure

This directory contains the Lambda handler and build scripts for deploying all 24 agentic AI services as AWS Lambda functions.

## Architecture

### Components

1. **handler.py** - Unified Lambda handler that:
   - Routes requests to appropriate agents
   - Handles API Gateway, EventBridge, and direct Lambda invocations
   - Provides health checks and agent listing endpoints
   - Individual handler functions for each of the 24 agents

2. **build.sh** - Build script that:
   - Creates a Lambda layer with dependencies (boto3, anthropic, openai, etc.)
   - Packages agent code and handler into deployment.zip
   - Optimizes package size by removing tests and cache files

3. **Terraform Integration** - The Lambda functions are deployed via:
   - `terraform/lambda.tf` - 24 Lambda functions (one per agent)
   - `terraform/api_gateway.tf` - HTTP API Gateway for REST endpoints

## Deployment

### Prerequisites

- Python 3.11+
- pip
- zip
- AWS credentials configured

### Build Lambda Packages

```bash
cd /Users/aaldertoosthuizen/Projects/agentic-services/infrastructure/lambda
./build.sh
```

This creates:
- `layer.zip` - Lambda layer with dependencies (~50-100 MB)
- `deployment.zip` - Application code with handler (~5-10 MB)

### Deploy with Terraform

```bash
cd /Users/aaldertoosthuizen/Projects/agentic-services/infrastructure/terraform

# Initialize Terraform
terraform init

# Review deployment plan
terraform plan

# Deploy infrastructure
terraform apply
```

## API Endpoints

Once deployed, the API Gateway provides these endpoints:

### Health Check
```bash
GET https://{api-id}.execute-api.eu-central-1.amazonaws.com/prod/health
```

### List All Agents
```bash
GET https://{api-id}.execute-api.eu-central-1.amazonaws.com/prod/agents
```

### Execute Agent
```bash
POST https://{api-id}.execute-api.eu-central-1.amazonaws.com/prod/agents/{agent-name}
Content-Type: application/json

{
  "project_id": "my-migration-project",
  "environment": "production",
  "target_cloud": "aws",
  "region": "eu-central-1"
}
```

### Get Agent Status
```bash
GET https://{api-id}.execute-api.eu-central-1.amazonaws.com/prod/agents/{agent-name}/status?project_id=my-migration-project
```

## Available Agents

### Discovery Phase (8 agents)
- `infrastructure-scanner` - Scan existing infrastructure
- `application-profiler` - Profile applications
- `data-discovery` - Discover data sources
- `integration-mapper` - Map integrations
- `security-auditor` - Audit security
- `network-analyzer` - Analyze network topology
- `performance-baseline` - Establish performance baseline
- `licensing-analyzer` - Analyze software licenses

### Assessment Phase (5 agents)
- `dependency-mapper` - Map dependencies
- `compliance-checker` - Check compliance
- `cost-estimator` - Estimate migration costs
- `risk-assessment` - Assess migration risks
- `capacity-planner` - Plan capacity requirements

### Execution Phase (6 agents)
- `infrastructure-provisioner` - Provision infrastructure
- `data-migration` - Migrate data
- `application-migration` - Migrate applications
- `configuration` - Configure resources
- `testing` - Test migrated systems
- `rollback` - Rollback if needed

### Optimization Phase (5 agents)
- `performance-optimizer` - Optimize performance
- `cost-optimizer` - Optimize costs
- `security-hardening` - Harden security
- `monitoring-setup` - Setup monitoring
- `documentation` - Generate documentation

## Direct Lambda Invocation

You can also invoke Lambda functions directly:

```bash
aws lambda invoke \
  --function-name nagarro-agentic-dev-infrastructure-scanner \
  --payload '{"agent_name": "infrastructure-scanner", "payload": {"project_id": "test"}}' \
  response.json
```

## EventBridge Integration

Lambda functions can be triggered via EventBridge events:

```bash
aws events put-events \
  --entries '[{
    "Source": "agentic.platform",
    "DetailType": "AgentExecution",
    "Detail": "{\"agent_name\":\"infrastructure-scanner\",\"payload\":{\"project_id\":\"test\"}}",
    "EventBusName": "nagarro-agentic-dev"
  }]'
```

## Environment Variables

Each Lambda function is configured with:

- `DISCOVERY_BUCKET` - S3 bucket for discovery data
- `ARTIFACTS_BUCKET` - S3 bucket for artifacts
- `AGENT_STATES_TABLE` - DynamoDB table for agent states
- `WORKFLOW_HISTORY_TABLE` - DynamoDB table for workflow history
- `PROJECT_METADATA_TABLE` - DynamoDB table for project metadata
- `EVENT_BUS_NAME` - EventBridge event bus name
- `BEDROCK_MODEL_ID` - AWS Bedrock model ID for AI
- `AWS_REGION` - AWS region

## Monitoring

### CloudWatch Logs

Logs are available in CloudWatch:
- Log group: `/aws/lambda/nagarro-agentic-{env}-{agent-name}`
- Retention: 7 days (configurable)

### CloudWatch Alarms

API Gateway alarms monitor:
- 4XX error rate (client errors)
- 5XX error rate (server errors)
- Integration latency

### Dead Letter Queue

Failed Lambda invocations are sent to SQS DLQ:
- Queue: `nagarro-agentic-{env}-lambda-dlq`
- Retention: 14 days

## Cost Optimization

- Lambda functions use 1024 MB memory (configurable)
- 5-minute timeout (configurable)
- No VPC by default (reduces cold start time and cost)
- Lambda layer shared across all functions
- API Gateway uses HTTP API (cheaper than REST API)

## Security

- Lambda execution role with least-privilege permissions
- Secrets managed via AWS Secrets Manager (not environment variables)
- API Gateway supports JWT and AWS IAM authorization
- CORS configured for web application integration
- API keys optional for additional security

## Troubleshooting

### Build fails
```bash
# Ensure pip is up to date
pip install --upgrade pip

# Try building with verbose output
cd infrastructure/lambda
bash -x build.sh
```

### Lambda timeout
- Increase `lambda_timeout` in terraform.tfvars
- Default is 300 seconds (5 minutes)

### Lambda out of memory
- Increase `lambda_memory_size` in terraform.tfvars
- Default is 1024 MB

### Cold start issues
- Consider enabling Lambda SnapStart (Python 3.11+)
- Or use provisioned concurrency for critical agents

## Development

### Testing Handler Locally

```python
import json
from handler import lambda_handler

# Test health check
event = {"httpMethod": "GET", "path": "/health"}
result = lambda_handler(event, None)
print(json.dumps(result, indent=2))

# Test agent execution
event = {
    "agent_name": "infrastructure-scanner",
    "payload": {
        "project_id": "test",
        "environment": "production"
    }
}
result = lambda_handler(event, None)
print(json.dumps(result, indent=2))
```

### Adding New Agents

1. Create agent class in `src/agentic_services/agents/`
2. Add import to `handler.py`
3. Add to `AGENT_REGISTRY` dict
4. Create handler function (e.g., `my_agent_handler`)
5. Update `terraform/lambda.tf` locals with new agent name
6. Rebuild packages: `./build.sh`
7. Deploy: `terraform apply`

## References

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
