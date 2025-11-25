# AWS Free Tier Analysis - Nagarro Agentic Services Platform

**Last Updated:** 2025-01-11  
**Purpose:** Maximize free tier usage for initial development and POC  
**Target:** $0-50/month for first 12 months

---

## 🎁 Executive Summary

### Cost Comparison: Free Tier vs Standard

| Phase | Standard Cost | Free Tier Cost | Savings | Duration |
|-------|---------------|----------------|---------|----------|
| **POC/Development (Months 1-3)** | $200-300/month | **$0-30/month** | **90%** | 3 months |
| **Extended Development (Months 4-12)** | $200-300/month | **$30-80/month** | **60-75%** | 9 months |
| **Post Free Tier (Month 13+)** | $200-300/month | $200-300/month | 0% | Ongoing |

### **First Year Savings with Free Tier: $1,800-2,400**

---

## 🆓 AWS Free Tier Overview

AWS offers **two types** of free tier:

### 1. **12-Month Free Tier** (New AWS Accounts Only)
- Starts from account creation date
- Expires after 12 months
- Most generous limits

### 2. **Always Free Tier**
- Never expires
- Available to all accounts (new and existing)
- More limited but permanent

---

## 📊 Service-by-Service Free Tier Breakdown

### ✅ 1. AWS Bedrock (Claude AI)

**Free Tier:** ❌ **NO FREE TIER**

**Impact:** This is your biggest cost driver (~75% of budget)

**Workarounds for Development:**
1. **Use Claude API directly** (Anthropic offers $5 free credits)
2. **Mock responses** during development (save 100%)
3. **Batch testing** instead of continuous testing
4. **Limit test runs** to 10-20 per month

**Development Strategy:**
```python
# Use demo mode with cached responses
DEMO_MODE = True  # No Bedrock calls
BEDROCK_CALLS_LIMIT = 20  # per month
```

**Estimated Cost with Limits:**
- 20 test projects/month × $4 = **$80/month**
- With mocking: **$0-20/month**

---

### ✅ 2. Amazon ECS Fargate

**Free Tier:** ❌ **NO FREE TIER** for Fargate

**Alternative: EC2 (12-Month Free Tier)**
```
t2.micro instance:
- 750 hours/month (enough for 1 instance 24/7)
- 1 vCPU, 1 GB RAM
- FREE for first 12 months
```

**Development Strategy:**
- Use **EC2 t2.micro** instead of Fargate
- Run Docker containers on EC2
- Sufficient for development workload

**Cost Comparison:**

| Option | Month 1-12 | Month 13+ |
|--------|------------|-----------|
| ECS Fargate | $20-30 | $20-30 |
| EC2 t2.micro | **$0** | $8-10 |

**Savings:** $20-30/month for first year

---

### ✅ 3. Amazon S3

**Free Tier (12 months):**
- ✅ 5 GB standard storage
- ✅ 20,000 GET requests
- ✅ 2,000 PUT requests
- ✅ 100 GB data transfer out

**Development Usage:**
- Discovery data: ~2 GB
- Artifacts: ~2 GB
- Logs: ~1 GB
- **Total: ~5 GB** ✅ Fits perfectly!

**Cost with Free Tier:**
- Months 1-12: **$0**
- Month 13+: $5-10 (once you exceed free tier)

**Always Free Tier:**
- None (switches to pay-as-you-go after 12 months)

---

### ✅ 4. Amazon DynamoDB

**Free Tier (Always Free):**
- ✅ 25 GB storage
- ✅ 25 read capacity units (RCU)
- ✅ 25 write capacity units (WCU)
- ✅ 2.5M stream reads/month (DynamoDB Streams)

**Capacity Translation:**
- 25 RCU = ~200M reads/month
- 25 WCU = ~2.5M writes/month

**Development Usage:**
- Estimated: 100K reads, 50K writes/month
- **Well within free tier!** ✅

**Cost:**
- **Always $0** (development workload fits in free tier)
- Only pay if you exceed 25 GB storage or need provisioned capacity

**Strategy:**
- Use on-demand pricing (stays in free tier)
- Monitor usage with CloudWatch
- Will likely stay free forever for dev

---

### ✅ 5. Amazon EventBridge

**Free Tier (Always Free):**
- ✅ First 1 million events/month: **FREE**

**Development Usage:**
- Estimated: 50K events/month
- **Always free!** ✅

**Cost:**
- **Always $0** for development

---

### ✅ 6. Amazon VPC

**Free Tier:**
- ✅ VPC itself: **Always Free**
- ✅ Subnets: **Always Free**
- ✅ Security Groups: **Always Free**
- ✅ Internet Gateway: **Always Free**

**NOT Free:**
- ❌ NAT Gateway: $0.048/hour ($35/month)
- ❌ Application Load Balancer: $0.025/hour ($18/month)

**Cost Optimization for Development:**

| Component | Standard | Free Tier Alternative | Savings |
|-----------|----------|----------------------|---------|
| NAT Gateway | $65/month | Use NAT Instance (t2.micro free) | $65 |
| Load Balancer | $23/month | Direct EC2 access (no ALB) | $23 |

**Development Strategy:**
1. **Use NAT Instance** instead of NAT Gateway
   - Run on t2.micro (free tier)
   - Saves $65/month
   
2. **Skip Load Balancer** for development
   - Access EC2 directly via public IP
   - Add ALB later for production
   - Saves $23/month

**Cost with Free Tier:**
- Months 1-12: **$0** (using free tier alternatives)
- Month 13+: $10-15 (NAT instance on t2.micro)

---

### ✅ 7. AWS Secrets Manager

**Free Tier:** ❌ **NO FREE TIER**

**Alternative: Systems Manager Parameter Store**

**Parameter Store (Always Free):**
- ✅ 10,000 parameters (standard)
- ✅ 1,000 API calls/month
- ✅ **Completely Free**

**Cost Comparison:**

| Service | Month 1-12 | Month 13+ |
|---------|------------|-----------|
| Secrets Manager | $2-5 | $2-5 |
| Parameter Store | **$0** | **$0** |

**Development Strategy:**
- Use Parameter Store for all secrets
- Migrate to Secrets Manager only if needed (auto-rotation)

---

### ✅ 8. Amazon CloudWatch

**Free Tier (Always Free):**
- ✅ 10 custom metrics
- ✅ 10 alarms
- ✅ 5 GB log ingestion
- ✅ 5 GB log storage
- ✅ 3 dashboards (up to 50 metrics each)
- ✅ 1 million API requests

**Development Usage:**
- Logs: ~3 GB/month
- Metrics: 15 custom metrics
- Alarms: 10 alarms
- 1 dashboard

**Cost with Free Tier:**
- Months 1-12: **$0-5** (mostly free)
- Month 13+: $10-15

**Optimization:**
- Keep logs under 5 GB (use 7-day retention)
- Stay within 10 alarms
- Archive old logs to S3

---

### ✅ 9. Amazon ECR

**Free Tier:**
- ✅ 500 MB storage/month (always free)

**Development Usage:**
- Docker images: 2-3 images × 1 GB = 3 GB total
- Exceeds free tier by 2.5 GB

**Cost:**
- Storage: 2.5 GB × $0.10 = **$0.25/month**
- Data transfer: Minimal = **$0-1/month**

**Total: ~$1/month**

---

### ✅ 10. AWS X-Ray

**Free Tier (Always Free):**
- ✅ 100,000 traces/month
- ✅ 1 million trace retrievals/month

**Development Usage:**
- 20K traces/month
- **Always free!** ✅

**Cost: $0**

---

### ✅ 11. AWS CloudTrail

**Free Tier:**
- ✅ First trail with management events: **FREE**
- ✅ 90-day event history

**Development Usage:**
- Single trail for audit logging
- **Always free!** ✅

**Cost: $0**

---

### ✅ 12. AWS Backup

**Free Tier:** ❌ Limited (only warm/cold storage)

**Development Strategy:**
- **Skip automated backups** in development
- Use DynamoDB point-in-time recovery (PITR) if needed
- Manual snapshots for critical data

**Cost: $0** (no backups in dev)

---

## 💰 Total Cost Breakdown: Free Tier vs Standard

### Development Environment (First 12 Months)

| Service | Standard Cost | Free Tier | Savings |
|---------|---------------|-----------|---------|
| **Bedrock (AI)** | $150-250 | $20-80* | $70-230 |
| **Compute** | $20-30 | $0 (EC2 t2.micro) | $20-30 |
| **S3 Storage** | $5-10 | $0 | $5-10 |
| **DynamoDB** | $5-10 | $0 | $5-10 |
| **EventBridge** | $0-5 | $0 | $0-5 |
| **VPC/Network** | $30-40 | $0 (free alternatives) | $30-40 |
| **Secrets** | $2-5 | $0 (Parameter Store) | $2-5 |
| **CloudWatch** | $10-15 | $0-5 | $5-10 |
| **ECR** | $2-3 | $1 | $1-2 |
| **X-Ray** | $0-5 | $0 | $0-5 |
| **CloudTrail** | $10-15 | $0 | $10-15 |
| **Backup** | $0-5 | $0 | $0-5 |
| **TOTAL** | **$234-393** | **$21-86** | **$148-332** |

*With demo mode and limited Bedrock calls

### **Monthly Savings: 70-90%**

---

## 🎯 Recommended Free Tier Strategy

### Phase 1: POC (Months 1-3) - Target: $0-30/month

**Maximize Free Tier:**
1. ✅ Use **EC2 t2.micro** instead of Fargate (FREE)
2. ✅ Use **demo mode** for agents (no Bedrock calls = FREE)
3. ✅ Use **NAT Instance** instead of NAT Gateway (FREE)
4. ✅ Skip Load Balancer (direct EC2 access = FREE)
5. ✅ Use **Parameter Store** instead of Secrets Manager (FREE)
6. ✅ Keep S3 under 5 GB (FREE)
7. ✅ Keep DynamoDB under 25 GB (FREE)
8. ✅ Keep CloudWatch under 5 GB logs (FREE)

**Only Pay For:**
- Limited Bedrock API testing: $20-30/month

**Total: $20-30/month (90% savings)**

---

### Phase 2: Active Development (Months 4-12) - Target: $30-80/month

**Still Using Free Tier:**
1. ✅ EC2 t2.micro (FREE)
2. ✅ S3 under 5 GB (FREE)
3. ✅ DynamoDB always free tier (FREE)
4. ✅ EventBridge (FREE)
5. ✅ Parameter Store (FREE)
6. ✅ Single CloudTrail (FREE)

**Start Paying:**
- Bedrock API calls (more testing): $50-80/month
- CloudWatch (exceeding 5 GB): $5-10/month
- NAT Instance on t2.micro: Still FREE

**Total: $55-90/month (70% savings)**

---

### Phase 3: Pre-Production (Month 13+)

**Free Tier Expires:**
- EC2 t2.micro: Now $8-10/month
- S3: Now $5-10/month
- Other services maintain always-free tier

**Transition Strategy:**
- Move to ECS Fargate ($20-30/month)
- Add NAT Gateway for reliability ($65/month)
- Add Load Balancer ($23/month)
- Scale up Bedrock usage

**Total: $200-300/month (standard costs)**

---

## 📋 Free Tier Implementation Checklist

### Setup (Week 1)
- [ ] Create new AWS account (for 12-month free tier)
- [ ] Set up billing alerts at $20, $50, $100
- [ ] Enable cost allocation tags
- [ ] Configure AWS Budgets

### Infrastructure (Week 2)
- [ ] Deploy EC2 t2.micro instead of Fargate
- [ ] Set up NAT Instance (t2.micro) instead of NAT Gateway
- [ ] Use direct EC2 access (skip ALB for now)
- [ ] Configure VPC with free components only

### Application (Week 3)
- [ ] Enable demo mode (DEMO_MODE=true)
- [ ] Use Parameter Store for secrets
- [ ] Configure S3 lifecycle policies (stay under 5 GB)
- [ ] Set CloudWatch log retention to 7 days
- [ ] Limit Bedrock API calls to 20/month

### Monitoring (Week 4)
- [ ] Set up CloudWatch alarms (stay under 10)
- [ ] Monitor DynamoDB usage (stay under 25 GB)
- [ ] Monitor S3 usage (stay under 5 GB)
- [ ] Review AWS Cost Explorer weekly

---

## 💡 Cost Control Scripts

### 1. Monitor Free Tier Usage

```bash
#!/bin/bash
# check_free_tier.sh

echo "=== AWS Free Tier Usage Report ==="
echo ""

# S3 Usage
echo "S3 Storage (Target: <5 GB):"
aws s3 ls | while read bucket; do
  size=$(aws s3 ls --summarize --recursive s3://$bucket | grep "Total Size" | awk '{print $3/1024/1024/1024}')
  echo "  $bucket: ${size} GB"
done

# DynamoDB Usage
echo ""
echo "DynamoDB Storage (Target: <25 GB):"
aws dynamodb list-tables | jq -r '.TableNames[]' | while read table; do
  size=$(aws dynamodb describe-table --table-name $table | jq -r '.Table.TableSizeBytes/1024/1024/1024')
  echo "  $table: ${size} GB"
done

# CloudWatch Logs
echo ""
echo "CloudWatch Logs (Target: <5 GB):"
aws logs describe-log-groups | jq -r '.logGroups[] | "\(.logGroupName): \(.storedBytes/1024/1024/1024) GB"'
```

### 2. Enable Demo Mode

```python
# config/settings.py

# Free Tier Development Mode
FREE_TIER_MODE = os.getenv("FREE_TIER_MODE", "true").lower() == "true"
DEMO_MODE = FREE_TIER_MODE  # Use cached responses

# Bedrock usage limits
BEDROCK_MONTHLY_LIMIT = int(os.getenv("BEDROCK_MONTHLY_LIMIT", "20"))
BEDROCK_CALL_COUNTER = 0

def check_bedrock_limit():
    if FREE_TIER_MODE and BEDROCK_CALL_COUNTER >= BEDROCK_MONTHLY_LIMIT:
        raise Exception(f"Bedrock monthly limit reached: {BEDROCK_MONTHLY_LIMIT}")
```

---

## 📊 Cost Comparison: 12-Month Projection

### Scenario A: Standard Deployment (No Free Tier Optimization)

| Month | Cost | Cumulative |
|-------|------|------------|
| 1-12 | $250 | $3,000 |
| **Total** | | **$3,000** |

### Scenario B: Free Tier Optimized

| Phase | Months | Monthly Cost | Cumulative |
|-------|--------|--------------|------------|
| POC | 1-3 | $25 | $75 |
| Development | 4-12 | $70 | $630 |
| **Total** | **1-12** | | **$705** |

### **First Year Savings: $2,295 (77% reduction)**

---

## 🚨 Free Tier Gotchas to Avoid

### Common Mistakes That Cost Money:

1. **NAT Gateway** ($65/month)
   - ❌ Using managed NAT Gateway
   - ✅ Use NAT Instance on t2.micro (FREE)

2. **Load Balancer** ($23/month)
   - ❌ Adding ALB for development
   - ✅ Use direct EC2 access

3. **ECS Fargate** ($20-30/month)
   - ❌ Using Fargate for compute
   - ✅ Use EC2 t2.micro (FREE for 12 months)

4. **Secrets Manager** ($0.40/secret)
   - ❌ Storing secrets in Secrets Manager
   - ✅ Use Parameter Store (FREE)

5. **RDS Database** (if added)
   - ❌ Using RDS
   - ✅ Stick with DynamoDB (FREE tier)

6. **Excessive Bedrock Calls** ($3-5 each)
   - ❌ Running all tests against real API
   - ✅ Use demo mode, limit to 20 calls/month

7. **S3 Over 5 GB** ($0.023/GB)
   - ❌ Storing everything forever
   - ✅ Lifecycle policies, delete test data

8. **CloudWatch Logs Over 5 GB** ($0.57/GB ingestion)
   - ❌ Verbose logging, long retention
   - ✅ 7-day retention, filter logs

---

## ✅ Free Tier Success Metrics

**Target Metrics (Months 1-3):**
- ✅ S3 usage: <5 GB
- ✅ DynamoDB: <25 GB
- ✅ CloudWatch logs: <5 GB
- ✅ Bedrock calls: <20/month
- ✅ EC2: 1 t2.micro instance
- ✅ Total cost: <$30/month

**Monitoring:**
- Check AWS Cost Explorer daily
- Set up billing alerts
- Review free tier usage weekly
- Monitor service quotas

---

## 🎓 Best Practices

### Development Workflow with Free Tier

1. **Week 1-4: Pure Local Development**
   - Cost: $0
   - No AWS resources yet
   - Use local Docker, mock data

2. **Week 5-8: Deploy to AWS (Free Tier)**
   - Cost: $0-20/month
   - Deploy infrastructure
   - Limited Bedrock testing

3. **Week 9-12: Active Development**
   - Cost: $20-50/month
   - More Bedrock calls
   - Still using free tier compute

4. **Month 4-12: Extended Development**
   - Cost: $50-90/month
   - Increased testing
   - Approaching free tier limits

5. **Month 13+: Production Ready**
   - Cost: $200-300/month
   - Full production infrastructure
   - No more free tier

---

## 📞 Resources

- **AWS Free Tier Homepage:** https://aws.amazon.com/free/
- **Free Tier FAQ:** https://aws.amazon.com/free/free-tier-faqs/
- **Billing Dashboard:** https://console.aws.amazon.com/billing/
- **Cost Explorer:** https://console.aws.amazon.com/cost-management/

---

## 🎯 Summary

### Can You Build With Free Tier? **YES! ✅**

**First 3 Months (POC):**
- Cost: $0-30/month (instead of $200-300)
- Savings: 90%
- What's Free: Compute, storage, database, networking (with alternatives)
- What Costs: Bedrock API calls (limit to 20/month)

**Months 4-12 (Development):**
- Cost: $30-90/month (instead of $200-300)
- Savings: 60-85%
- Still using free tier for most services
- Bedrock usage increases

**Year 1 Total:**
- Standard: $3,000
- Free Tier Optimized: $705
- **Savings: $2,295 (77%)**

### **Recommendation:**
✅ Start with free tier for POC (Months 1-3)  
✅ Extend with free tier for development (Months 4-12)  
✅ Transition to standard infrastructure only when ready for production

---

**Last Updated:** 2025-01-11  
**Next Review:** Monthly  
**Owner:** Platform Cost Optimization Team
