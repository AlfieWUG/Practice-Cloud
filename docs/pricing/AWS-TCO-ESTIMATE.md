# AWS Total Cost of Ownership (TCO) - Agentic Services Platform

## Executive Summary

**Project**: Agentic Services Platform (20 AI Agents for Cloud Migration)  
**Primary Region**: eu-central-1 (Frankfurt)  
**Architecture**: Serverless + Container-based

### Cost Summary by Environment

| Environment | Monthly Cost | Annual Cost | Notes |
|-------------|--------------|-------------|-------|
| **DEV** | $6 - $20 | $72 - $240 | Low usage, mock testing |
| **STAGING** | $50 - $150 | $600 - $1,800 | Medium usage, client demos |
| **PRODUCTION** | $500 - $2,000 | $6,000 - $24,000 | Per client, usage-based |

---

## 1. AWS Services Required

### 1.1 Core Compute & AI

#### Amazon Bedrock (AI/LLM Service)
- **Purpose**: 20 AI agents powered by Claude 3
- **Models Used**:
  - Primary: `anthropic.claude-3-5-sonnet-20241022-v2:0`
  - Fallback: `anthropic.claude-3-haiku-20240307-v1:0` (20x cheaper)
  - Future: `anthropic.claude-3-7-sonnet-20250219-v1:0`

**Pricing**:
- Claude 3.5 Sonnet: $0.003/1K input tokens, $0.015/1K output tokens
- Claude 3 Haiku: $0.00025/1K input, $0.00125/1K output
- No base fees, pay-per-use only

#### AWS App Runner / ECS Fargate
- **Purpose**: Host Streamlit dashboard and API
- **Options**:
  - **App Runner** (Recommended): $0.064/vCPU-hour, $0.007/GB-hour
  - **ECS Fargate**: Similar pricing, more control

**Configuration**:
- DEV: 0.25 vCPU, 0.5 GB RAM (always-on)
- PROD: 1 vCPU, 2 GB RAM with auto-scaling (2-10 instances)

---

### 1.2 Storage & Databases

#### Amazon S3
- **Purpose**: Store artifacts, migration plans, discovery data
- **Buckets**:
  - `agentic-services-artifacts-{env}`
  - `agentic-services-state-{env}`
  - `agentic-services-terraform-state`

**Pricing**:
- First 50 TB: $0.023/GB/month (eu-central-1)
- PUT/POST: $0.005 per 1,000 requests
- GET: $0.0004 per 1,000 requests

#### Amazon DynamoDB
- **Purpose**: Store agent state, workflow status, project metadata
- **Tables**:
  - `agent_state` - Agent execution state
  - `project_data` - Project information
  - `workflow_status` - Orchestration state

**Pricing**:
- On-Demand: $1.25/million write, $0.25/million read
- Storage: $0.25/GB/month
- First 25 GB/month free

---

### 1.3 Integration & Orchestration

#### Amazon EventBridge
- **Purpose**: Event-driven agent orchestration
- **Usage**: Agent completion triggers, workflow events

**Pricing**:
- $1.00 per million events
- Effectively free for typical usage (<10K events/month in DEV)

#### AWS Lambda (Optional)
- **Purpose**: Lightweight triggers, data transformations
- **Usage**: Event handlers, cleanup jobs

**Pricing**:
- $0.20 per 1M requests
- $0.0000166667/GB-second
- 1M requests + 400,000 GB-seconds free tier/month

---

### 1.4 Networking & Security

#### Amazon VPC
- **Purpose**: Network isolation, multi-AZ deployment
- **Configuration**:
  - CIDR: 10.0.0.0/16
  - Public Subnets: 2 (eu-central-1a, eu-central-1b)
  - Private Subnets: 2 (eu-central-1a, eu-central-1b)
  - NAT Gateways: 2 (high availability)

**Pricing**:
- VPC: Free
- NAT Gateway: $0.045/hour + $0.045/GB processed (~$35/month per gateway)

#### AWS Secrets Manager
- **Purpose**: Store API keys, credentials
- **Secrets**: ~5-10 secrets per environment

**Pricing**:
- $0.40/secret/month
- $0.05 per 10,000 API calls

---

### 1.5 Monitoring & Operations

#### Amazon CloudWatch
- **Purpose**: Logs, metrics, alarms
- **Components**:
  - Logs for all services
  - Custom metrics (agent performance)
  - Alarms (cost, errors, latency)

**Pricing**:
- Logs Ingestion: $0.50/GB
- Logs Storage: $0.03/GB/month
- Metrics: $0.30 per custom metric/month
- Alarms: $0.10 per alarm/month

#### AWS X-Ray (Optional)
- **Purpose**: Distributed tracing for debugging
- **Pricing**: $5 per 1M traces recorded

---

### 1.6 CI/CD & Infrastructure

#### Amazon ECR (Container Registry)
- **Purpose**: Store Docker images
- **Storage**: ~2-5 GB total

**Pricing**:
- $0.10/GB/month

#### Terraform State Backend
- **S3 Bucket**: Terraform state storage
- **DynamoDB Table**: State locking
- **Cost**: <$1/month

---

## 2. Data Usage Estimates

### 2.1 Storage Breakdown

#### S3 Storage (per client project)

| Data Type | Size Range | Retention | Notes |
|-----------|------------|-----------|-------|
| Discovery data | 100-500 MB | 1 year | Network scans, app profiles |
| Analysis results | 50-200 MB | 1 year | Dependencies, risks |
| Migration plans | 20-100 MB | 2 years | Step-by-step plans |
| Generated artifacts | 200 MB - 2 GB | 2 years | Terraform, scripts, docs |
| Logs & metrics | 1-5 GB/month | 90 days | CloudWatch exports |

**Total per client**: 500 MB - 3 GB (active), 10-50 GB (over 2 years)

#### DynamoDB Storage

| Table | Items | Size per Item | Total Size |
|-------|-------|---------------|------------|
| agent_state | 20 agents × 10 runs | ~50 KB | 10 MB |
| project_data | 50 projects | ~100 KB | 5 MB |
| workflow_status | 500 workflows | ~20 KB | 10 MB |

**Total**: ~25 MB (well within 25 GB free tier)

---

### 2.2 Compute Usage Estimates

#### Bedrock Token Usage (per migration project)

| Phase | Agent Count | Avg Tokens/Agent | Total Tokens |
|-------|-------------|------------------|--------------|
| Discovery | 6 agents | 50K input, 30K output | 480K tokens |
| Planning | 6 agents | 60K input, 40K output | 600K tokens |
| Execution | 8 agents | 40K input, 25K output | 520K tokens |

**Total per project**: ~1.6M tokens (~$6-10 in AI costs using Sonnet)

**Annual estimate (50 projects)**: 80M tokens (~$300-500)

#### Container Runtime

| Environment | vCPU-hours/month | GB-hours/month | Cost |
|-------------|------------------|----------------|------|
| DEV (always-on) | 180 | 360 | ~$14 |
| STAGING (12h/day) | 180 | 360 | ~$14 |
| PROD (24/7, avg 3 instances) | 2,160 | 4,320 | ~$168 |

---

### 2.3 Network Traffic

| Type | Volume | Cost/GB | Monthly Cost |
|------|--------|---------|--------------|
| S3 → Internet (artifacts download) | 10-50 GB | $0.09 | $0.90 - $4.50 |
| NAT Gateway (private subnet egress) | 20-100 GB | $0.045 | $0.90 - $4.50 |
| CloudFront (optional CDN) | 0-500 GB | $0.085 | $0 - $42.50 |

---

## 3. Detailed Cost Breakdown

### 3.1 Development Environment (Low Usage)

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **Bedrock** | 1M tokens/month (testing) | $1 - $3 |
| **App Runner** | 0.25 vCPU, 0.5 GB, 24/7 | $13 - $15 |
| **S3** | 5 GB storage, 10K requests | $0.50 |
| **DynamoDB** | On-demand, <25 GB | $0 (free tier) |
| **EventBridge** | 5K events/month | $0.01 |
| **CloudWatch** | 2 GB logs, 10 metrics | $1.50 |
| **Secrets Manager** | 5 secrets | $2.00 |
| **ECR** | 2 GB images | $0.20 |
| **NAT Gateway** | 1 gateway, 10 GB | $35 - $40 |

**TOTAL DEV**: **$53 - $62/month**

**Cost Optimization for DEV**:
- Remove NAT Gateway (use public subnets): **$6 - $20/month**
- Use mock services for testing: **$0** (current setup)

---

### 3.2 Staging Environment (Medium Usage)

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **Bedrock** | 5M tokens/month | $15 - $25 |
| **App Runner** | 0.5 vCPU, 1 GB, 12h/day | $13 - $15 |
| **S3** | 50 GB storage, 100K requests | $1.50 |
| **DynamoDB** | On-demand, moderate use | $2 - $5 |
| **EventBridge** | 50K events/month | $0.05 |
| **CloudWatch** | 10 GB logs, 20 metrics | $6 - $8 |
| **Secrets Manager** | 10 secrets | $4.00 |
| **NAT Gateway** | 1 gateway, 50 GB | $37 - $42 |

**TOTAL STAGING**: **$78 - $126/month**

---

### 3.3 Production Environment (Per Client)

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **Bedrock** | 20M tokens/month (4 projects) | $60 - $100 |
| **App Runner** | 1 vCPU, 2 GB, auto-scale 2-10 | $150 - $300 |
| **S3** | 500 GB storage, 500K requests | $13 - $15 |
| **DynamoDB** | On-demand, high usage | $20 - $50 |
| **EventBridge** | 200K events/month | $0.20 |
| **CloudWatch** | 100 GB logs, 50 metrics | $60 - $80 |
| **Secrets Manager** | 15 secrets | $6.00 |
| **NAT Gateway** | 2 gateways (HA), 200 GB | $81 - $90 |
| **ALB** (load balancer) | Optional for HA | $20 - $25 |

**TOTAL PRODUCTION**: **$410 - $710/month per client**

**Multi-client scaling**:
- 5 clients: $2,000 - $3,500/month
- 10 clients: $3,500 - $6,000/month (shared infrastructure)

---

## 4. Optimization Strategies

### 4.1 Immediate Cost Savings

1. **Use Claude 3 Haiku for non-critical agents** (20x cheaper)
   - Potential savings: 60-70% on Bedrock costs
   
2. **Remove NAT Gateways in DEV** ($70/month savings)
   - Use public subnets for non-production

3. **CloudWatch Logs retention**: 7 days (DEV), 30 days (PROD)
   - Potential savings: 50% on logs storage

4. **S3 Intelligent Tiering**: Auto-move old data to cheaper storage
   - Potential savings: 30-40% on S3 costs

5. **DynamoDB reserved capacity**: For predictable workloads
   - Potential savings: 50-70% vs on-demand

### 4.2 Long-term Optimization

1. **Savings Plans**: Commit to 1-3 year usage (30-40% discount)
2. **Spot Instances**: For non-critical batch processing (70% discount)
3. **Multi-region**: Only deploy to single region initially
4. **Monitoring**: Set up cost alarms and budgets

---

## 5. Required AWS Accounts & Structure

### Recommended Account Structure

```
Root Organization Account
├── Dev Account (billing: $60/month)
├── Staging Account (billing: $100/month)
└── Production Account (billing: $500-2000/month)
```

### Service Limits to Request

| Service | Default Limit | Requested Limit | Reason |
|---------|---------------|-----------------|--------|
| Bedrock Claude Sonnet | Need approval | Enabled | Primary AI model |
| App Runner services | 25 | 25 (default OK) | - |
| VPC per region | 5 | 3 | DEV, STAGING, PROD |
| NAT Gateways | 5 | 4 | 2 per PROD (HA) |

---

## 6. Implementation Phases & Costs

### Phase 1: MVP Development (Month 1-2)
- **Environment**: DEV only with mocks
- **Cost**: $0 (current setup, no AWS usage)
- **Goal**: Build all 20 agents, test infrastructure

### Phase 2: AWS Integration (Month 3)
- **Environment**: DEV with real AWS services
- **Cost**: $60/month
- **Goal**: Integrate Bedrock, test with real AI

### Phase 3: Staging & Client Demos (Month 4-5)
- **Environment**: DEV + STAGING
- **Cost**: $160/month
- **Goal**: Client demos, feedback collection

### Phase 4: Production Launch (Month 6+)
- **Environment**: DEV + STAGING + PROD
- **Cost**: $660/month (single client)
- **Goal**: First paying customer

---

## 7. Cost Monitoring & Governance

### Required Setup

1. **AWS Budgets**: Set up monthly budgets with alerts
   - DEV: $100/month threshold
   - STAGING: $200/month threshold
   - PROD: $3,000/month threshold

2. **Cost Explorer**: Enable for daily cost tracking

3. **CloudWatch Alarms**:
   - Bedrock token usage > 80% of budget
   - S3 storage > 80% of expected
   - Unexpected service usage

4. **Tagging Strategy**:
   ```
   Environment: dev|staging|prod
   Project: agentic-services
   Client: client-name
   CostCenter: engineering|operations
   Owner: team-name
   ```

---

## 8. Bill of Materials for Team

### Immediate Requirements (for DEV setup)

- [ ] AWS Account (root organization)
- [ ] IAM user with admin access (for Terraform)
- [ ] Enable Bedrock model access (Claude 3 Sonnet, Haiku)
- [ ] Create S3 bucket for Terraform state
- [ ] Create DynamoDB table for state locking
- [ ] Create ECR repository
- [ ] Configure GitLab CI/CD variables
- [ ] Set up AWS budgets & alarms

### Estimated Timeline
- **AWS account creation**: 1-2 days
- **Bedrock model approval**: 1-3 business days
- **Infrastructure setup**: 1 day (via Terraform)
- **CI/CD integration**: Already complete ✅

### Security Requirements
- [ ] MFA enabled on root account
- [ ] CloudTrail enabled (audit logging)
- [ ] GuardDuty enabled (threat detection)
- [ ] AWS Config enabled (compliance)
- [ ] VPC Flow Logs enabled

---

## 9. TCO Summary (3-Year Projection)

### Conservative Estimate (5 clients)

| Year | Development | Operations | Total | Notes |
|------|-------------|------------|-------|-------|
| **Year 1** | $1,200 (DEV) | $3,600 (first client) | **$4,800** | MVP + 1 client |
| **Year 2** | $1,200 | $24,000 (5 clients) | **$25,200** | Scale to 5 clients |
| **Year 3** | $1,200 | $42,000 (10 clients) | **$43,200** | Scale to 10 clients |

**3-Year Total**: **$73,200**

### Aggressive Estimate (20 clients by Year 3)

| Year | Development | Operations | Total |
|------|-------------|------------|-------|
| **Year 1** | $1,200 | $3,600 | **$4,800** |
| **Year 2** | $1,200 | $36,000 | **$37,200** |
| **Year 3** | $1,200 | $72,000 | **$73,200** |

**3-Year Total**: **$115,200**

---

## 10. Next Steps for Team

### Procurement Checklist

1. **Approve Budget**
   - Initial: $100/month (DEV)
   - 3-month: $200/month (DEV + STAGING)
   - 6-month: $800/month (+ first PROD client)

2. **Create AWS Account**
   - Organization: Nagarro / Your Company
   - Billing contact: Finance team
   - Technical contact: Your email

3. **Request Bedrock Access**
   - Submit via AWS Console → Bedrock → Model Access
   - Approval typically takes 24-48 hours

4. **Setup IAM Roles**
   - GitLab CI/CD deployment role
   - Developer read-only access
   - Admin access for 2-3 key people

5. **Enable Cost Controls**
   - Budgets with email alerts
   - Require approval for resources > $50/month

---

## Questions for Team Discussion

1. **Budget Approval**: Can we approve $100/month for DEV environment?
2. **AWS Account**: Do we have existing AWS organization or create new?
3. **Region**: Confirm eu-central-1 (Frankfurt) or prefer different region?
4. **Security**: Any specific compliance requirements (SOC2, ISO27001, etc.)?
5. **Billing**: Corporate credit card or invoice billing?
6. **Timeline**: When do you need AWS environment ready?

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-11  
**Prepared By**: Agentic Services Platform Team  
**Contact**: aaldertoosthuizen@nagarro.com

**Next Action**: Schedule 30-min call with finance/ops team to review and approve budget.
