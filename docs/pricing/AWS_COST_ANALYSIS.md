# AWS Cost Analysis - Nagarro Agentic Services Platform

**Last Updated:** 2025-01-11  
**Region:** eu-central-1 (Frankfurt)  
**Currency:** USD

---

## 💰 Executive Summary

| Environment | Monthly Cost | Annual Cost | Purpose |
|-------------|-------------|-------------|---------|
| **Development** | $200-300 | $2,400-3,600 | Testing & development |
| **Staging** | $300-500 | $3,600-6,000 | Pre-production validation |
| **Production** | $800-1,200 | $9,600-14,400 | Live customer usage |
| **Total (All Envs)** | **$1,300-2,000** | **$15,600-24,000** | Full platform |

---

## 📊 Detailed Cost Breakdown by Service

### 1. AWS Bedrock (Claude AI) - **Primary Cost Driver**

**Model:** Claude 3 Sonnet (anthropic.claude-3-sonnet-20240229-v1:0)

| Pricing Tier | Input Tokens | Output Tokens |
|--------------|--------------|---------------|
| Standard | $0.003 per 1K | $0.015 per 1K |

**Usage Estimates per Project:**
- Discovery Agent: ~50K tokens (input + output)
- Analysis Agent: ~80K tokens
- Planning Agent: ~100K tokens  
- Artifact Generation: ~150K tokens
- **Total per project:** ~380K tokens

**Cost per Project:** ~$3-5

**Monthly Volume Estimates:**

| Environment | Projects/Month | Bedrock Cost |
|-------------|----------------|--------------|
| Development | 50 test runs | $150-250 |
| Staging | 20 validation runs | $60-100 |
| Production | 100 customer projects | $300-500 |

**Optimization Tips:**
- Use caching for repeated queries (30-40% savings)
- Implement token limits per agent
- Use Claude Haiku for simple tasks ($0.00025 per 1K tokens)

---

### 2. Amazon ECS Fargate - **Compute**

**Configuration per Environment:**

#### Development
```
Tasks: 2 (UI + Agent Runner)
vCPU: 0.5 vCPU per task
Memory: 1 GB per task
Running: 8 hours/day, 5 days/week
```
**Cost:** $20-30/month

#### Staging
```
Tasks: 2 (UI + Agent Runner)
vCPU: 1 vCPU per task
Memory: 2 GB per task
Running: 12 hours/day, 7 days/week
```
**Cost:** $50-70/month

#### Production
```
Tasks: 4 (2 UI + 2 Agent Runners)
vCPU: 2 vCPU per task
Memory: 4 GB per task
Running: 24/7 with auto-scaling
```
**Cost:** $200-300/month

**Fargate Pricing (eu-central-1):**
- vCPU: $0.04656 per vCPU-hour
- Memory: $0.00511 per GB-hour

---

### 3. Amazon S3 - **Storage**

**Buckets:**
- Discovery data bucket
- Artifacts bucket
- Logs bucket

**Storage Estimates:**

| Environment | Storage/Month | Requests | Cost |
|-------------|---------------|----------|------|
| Development | 10 GB | 50K PUT/GET | $5-10 |
| Staging | 25 GB | 100K PUT/GET | $10-15 |
| Production | 200 GB | 500K PUT/GET | $30-50 |

**Pricing:**
- Storage: $0.023 per GB/month (S3 Standard)
- PUT requests: $0.005 per 1,000 requests
- GET requests: $0.0004 per 1,000 requests

**Cost Optimization:**
- Lifecycle policies: Move to S3 Glacier after 90 days (90% cheaper)
- Enable S3 Intelligent-Tiering for automatic cost optimization
- Delete incomplete multipart uploads after 7 days

---

### 4. Amazon DynamoDB - **Database**

**Tables:**
- AgentStates (project state management)
- WorkflowHistory (execution logs)
- ProjectMetadata (project information)

**Capacity Mode:** On-Demand (pay-per-request)

| Environment | Read/Write Capacity | Requests/Month | Cost |
|-------------|---------------------|----------------|------|
| Development | Minimal | 100K reads, 50K writes | $5-10 |
| Staging | Light | 250K reads, 100K writes | $10-20 |
| Production | Standard | 2M reads, 500K writes | $50-80 |

**Pricing:**
- Write request: $1.25 per million requests
- Read request: $0.25 per million requests
- Storage: $0.25 per GB/month

**Cost Optimization:**
- Enable Point-in-Time Recovery only for production
- Use DynamoDB Streams only when needed
- Consider Provisioned Capacity for predictable workloads (50-70% savings)

---

### 5. Amazon EventBridge - **Event Bus**

**Usage:**
- Agent completion events
- Workflow state changes
- Error notifications

| Environment | Events/Month | Cost |
|-------------|--------------|------|
| Development | 50K | Free (under 1M) |
| Staging | 100K | Free (under 1M) |
| Production | 500K | Free (under 1M) |

**Pricing:**
- First 1 million events: **FREE**
- Additional events: $1.00 per million

**Typical Cost:** $0-5/month (unless >1M events)

---

### 6. Amazon VPC - **Network**

**Components:**
- VPC (10.0.0.0/16)
- 2 Public Subnets (across 2 AZs)
- 2 Private Subnets (across 2 AZs)
- NAT Gateway (1 per AZ)
- Application Load Balancer

| Component | Quantity | Cost/Month |
|-----------|----------|------------|
| VPC | 1 | Free |
| Subnets | 4 | Free |
| NAT Gateway | 2 | $65/each = $130 |
| ALB | 1 | $23 base + data processing |
| Data Transfer | Varies | $0.09 per GB |

**Network Cost per Environment:**

| Environment | NAT + ALB + Data Transfer | Total |
|-------------|---------------------------|-------|
| Development | Minimal usage | $30-40 |
| Staging | Moderate usage | $60-80 |
| Production | High usage | $150-200 |

**Cost Optimization:**
- Use single NAT Gateway for dev/staging (not recommended for prod)
- Enable VPC Flow Logs only for troubleshooting
- Use VPC Endpoints for S3/DynamoDB (avoid NAT charges)

---

### 7. AWS Secrets Manager - **Secrets**

**Secrets:**
- API keys
- Database credentials
- Third-party service tokens

**Pricing:**
- $0.40 per secret per month
- $0.05 per 10,000 API calls

| Environment | Secrets | API Calls | Cost |
|-------------|---------|-----------|------|
| Development | 3 | 10K/month | $2 |
| Staging | 5 | 20K/month | $2-3 |
| Production | 8 | 100K/month | $3-5 |

**Cost Optimization:**
- Use Parameter Store (free tier) for non-sensitive configs
- Rotate secrets quarterly instead of monthly

---

### 8. Amazon CloudWatch - **Monitoring**

**Components:**
- Log storage and ingestion
- Custom metrics
- Alarms
- Dashboards

| Environment | Logs (GB) | Metrics | Alarms | Cost |
|-------------|-----------|---------|--------|------|
| Development | 5 GB | 20 | 10 | $10-15 |
| Staging | 10 GB | 40 | 20 | $20-30 |
| Production | 50 GB | 100 | 50 | $80-120 |

**Pricing:**
- Log ingestion: $0.57 per GB
- Log storage: $0.032 per GB/month
- Custom metrics: $0.30 per metric/month
- Alarms: $0.10 per alarm/month
- Dashboards: $3.00 per dashboard/month

**Cost Optimization:**
- Reduce log retention to 7 days for dev, 30 days for prod
- Use log filtering to reduce ingestion
- Aggregate metrics before publishing

---

### 9. Amazon ECR - **Container Registry**

**Usage:**
- Docker images for ECS tasks
- Typical image size: 1-2 GB

**Pricing:**
- Storage: $0.10 per GB/month
- Data transfer out: $0.09 per GB

| Environment | Storage | Transfer | Cost |
|-------------|---------|----------|------|
| All Environments | 10 GB total | 5 GB/month | $2-3 |

**Cost Optimization:**
- Use lifecycle policies (keep last 10 images)
- Enable image scanning only for production

---

### 10. AWS X-Ray - **Distributed Tracing**

**Usage:**
- Request tracing for debugging
- Performance analysis

**Pricing:**
- First 100,000 traces/month: **FREE**
- Additional: $5.00 per million traces

| Environment | Traces/Month | Cost |
|-------------|--------------|------|
| Development | 20K | Free |
| Staging | 50K | Free |
| Production | 200K | $1-2 |

**Typical Cost:** $0-5/month

---

### 11. AWS CloudTrail - **Audit Logging**

**Purpose:**
- API call logging
- Security audit trail
- Compliance

**Pricing:**
- First trail: **FREE** (management events)
- Additional trails: $2.00 per 100,000 events

| Environment | Events/Month | Cost |
|-------------|--------------|------|
| All Environments | 500K total | $10-15 |

---

### 12. AWS Backup - **Automated Backups**

**Resources:**
- DynamoDB tables
- EBS volumes (if any)

**Pricing:**
- Storage: $0.05 per GB/month
- Restore: $0.02 per GB

| Environment | Backup Size | Cost |
|-------------|-------------|------|
| Development | Not needed | $0 |
| Staging | 10 GB | $1 |
| Production | 100 GB | $5-10 |

---

## 💡 Cost Optimization Strategies

### Immediate Savings (30-40%)

1. **Right-Size ECS Tasks**
   - Start with 0.5 vCPU / 1 GB RAM
   - Scale up based on actual usage
   - **Savings:** $100-150/month

2. **Use Reserved Capacity for Production**
   - 1-year commitment: 30% discount
   - 3-year commitment: 50% discount
   - **Savings:** $200-400/month (production)

3. **Enable S3 Lifecycle Policies**
   - Move to Glacier after 90 days
   - Delete after 2 years
   - **Savings:** $50-100/month

4. **Use Single NAT Gateway for Dev/Staging**
   - Shared NAT Gateway
   - **Savings:** $65/month

5. **Reduce CloudWatch Logs Retention**
   - Dev: 3 days (instead of 7)
   - Staging: 14 days (instead of 30)
   - **Savings:** $20-40/month

### Advanced Optimization (50-60% total savings)

6. **Implement Token Caching for Bedrock**
   - Cache repeated queries
   - **Savings:** $50-150/month

7. **Use Spot Instances for Batch Processing**
   - 70% cheaper than on-demand
   - **Savings:** Not applicable (using Fargate)

8. **DynamoDB Provisioned Capacity**
   - Switch from on-demand to provisioned
   - **Savings:** $30-50/month

9. **Compress Logs Before Storage**
   - Reduce CloudWatch ingestion
   - **Savings:** $20-30/month

10. **Use VPC Endpoints**
    - Avoid NAT Gateway charges for S3/DynamoDB
    - **Savings:** $30-50/month

---

## 📊 Monthly Cost Summary by Service

### Development Environment ($200-300/month)

| Service | Cost | Percentage |
|---------|------|------------|
| Bedrock (AI) | $150-250 | 75% |
| ECS Fargate | $20-30 | 10% |
| S3 Storage | $5-10 | 3% |
| DynamoDB | $5-10 | 3% |
| VPC/Networking | $30-40 | 12% |
| Other (Secrets, CloudWatch, etc.) | $20-30 | 8% |

**Key Driver:** Bedrock API calls (testing)

---

### Staging Environment ($300-500/month)

| Service | Cost | Percentage |
|---------|------|------------|
| Bedrock (AI) | $60-100 | 25% |
| ECS Fargate | $50-70 | 15% |
| S3 Storage | $10-15 | 3% |
| DynamoDB | $10-20 | 5% |
| VPC/Networking | $60-80 | 20% |
| CloudWatch | $20-30 | 7% |
| Other | $30-50 | 12% |

**Key Driver:** Networking and compute for pre-production

---

### Production Environment ($800-1,200/month)

| Service | Cost | Percentage |
|---------|------|------------|
| Bedrock (AI) | $300-500 | 42% |
| ECS Fargate | $200-300 | 25% |
| VPC/Networking | $150-200 | 15% |
| CloudWatch | $80-120 | 8% |
| DynamoDB | $50-80 | 5% |
| S3 Storage | $30-50 | 3% |
| Other (Backup, CloudTrail, etc.) | $40-60 | 4% |

**Key Driver:** Bedrock API calls (customer usage)

---

## 🎯 Cost by Usage Scenario

### Low Usage (10-20 projects/month)
- **Development:** $150-200/month
- **Staging:** $200-300/month
- **Production:** $400-600/month
- **Total:** $750-1,100/month

### Medium Usage (50-100 projects/month)
- **Development:** $200-250/month
- **Staging:** $300-400/month
- **Production:** $800-1,000/month
- **Total:** $1,300-1,650/month

### High Usage (200+ projects/month)
- **Development:** $250-300/month
- **Staging:** $400-500/month
- **Production:** $1,200-1,800/month
- **Total:** $1,850-2,600/month

---

## 💵 Cost Control Measures

### AWS Budgets & Alerts

**Recommended Budgets:**
```
Development:   $300/month   (Alert at 80% = $240)
Staging:       $500/month   (Alert at 80% = $400)
Production:    $1,200/month (Alert at 80% = $960)
```

**Alert Actions:**
- Email notification to team
- Slack webhook notification
- SNS topic for automation

### Cost Allocation Tags

**Required Tags:**
```
Environment:  dev | staging | production
Project:      agentic-services
CostCenter:   cloud-migration
Owner:        platform-team
```

### Monthly Cost Review

**Process:**
1. Review AWS Cost Explorer
2. Identify cost anomalies
3. Check Trusted Advisor recommendations
4. Update cost forecast
5. Implement optimizations

---

## 📈 ROI Analysis

### Traditional Consulting Costs (Manual Approach)

| Activity | Consultant Days | Rate | Cost |
|----------|----------------|------|------|
| Discovery | 10 days | $1,500/day | $15,000 |
| Analysis | 15 days | $1,500/day | $22,500 |
| Planning | 10 days | $1,500/day | $15,000 |
| Documentation | 5 days | $1,200/day | $6,000 |
| **Total per project** | **40 days** | | **$58,500** |

### Agentic Platform Costs (Automated)

| Item | Cost |
|------|------|
| Platform runtime | $10/month allocated |
| Bedrock API calls | $3-5 per project |
| **Total per project** | **~$5-10** |

### **Cost Savings: 99.9% per project**

### **Break-Even Analysis**

**Monthly platform cost:** $1,300-2,000  
**Cost per project:** $5-10  
**Traditional cost per project:** $58,500

**Break-even:** 1-2 projects/month  
**Projects to cover annual cost:** 2-3 projects/year

---

## 🔮 Cost Projection (3-Year)

| Year | Projects/Month | Monthly Cost | Annual Cost |
|------|----------------|--------------|-------------|
| Year 1 | 50-100 | $1,300-1,650 | $15,600-19,800 |
| Year 2 | 150-200 | $1,850-2,200 | $22,200-26,400 |
| Year 3 | 300-400 | $2,500-3,500 | $30,000-42,000 |

**3-Year Total:** $67,800-88,200

**With Reserved Instances (30% discount):**  
**3-Year Total:** $47,500-61,700

---

## ✅ Cost Optimization Checklist

- [ ] Enable S3 Lifecycle policies
- [ ] Configure CloudWatch log retention
- [ ] Implement token caching for Bedrock
- [ ] Right-size ECS tasks
- [ ] Use VPC Endpoints for S3/DynamoDB
- [ ] Set up AWS Budgets with alerts
- [ ] Enable Cost Allocation Tags
- [ ] Review Trusted Advisor recommendations monthly
- [ ] Consider Reserved Instances after 6 months
- [ ] Implement DynamoDB auto-scaling
- [ ] Compress CloudWatch logs
- [ ] Delete old ECR images
- [ ] Use single NAT for dev/staging

---

## 📞 Support

For questions about AWS costs:
- **AWS Cost Explorer:** Review detailed costs
- **AWS Trusted Advisor:** Free optimization recommendations
- **AWS Cost Optimization Team:** cost-optimization@nagarro.com

---

**Last Updated:** 2025-01-11  
**Next Review:** Monthly  
**Owner:** Platform Engineering Team
