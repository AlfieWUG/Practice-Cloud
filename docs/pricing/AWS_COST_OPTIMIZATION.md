# AWS Deployment - Cost Optimization Guide

## Estimated Monthly Costs (Ultra-Optimized Configuration)

### Core Services (Always Running)
| Service | Configuration | Est. Monthly Cost |
|---------|--------------|-------------------|
| **ECS Fargate** | 256 CPU, 512 MB, 1 task | ~$5 |
| **Application Load Balancer** | 1 ALB | ~$16 |
| **NAT Gateway** | 1 instance (single AZ) | ~$32 |
| **S3 Storage** | Minimal usage, 1-day retention | ~$1 |
| **DynamoDB** | On-demand, light usage | ~$1 |
| **CloudWatch Logs** | 1-day retention | <$1 |
| **Data Transfer** | Minimal | ~$1-2 |

**TOTAL MONTHLY (Always On): ~$55-60/month**

---

## 💰 Cost Saving Strategies

### Strategy 1: Stop When Not Demoing (RECOMMENDED)
**Save ~$5/month on ECS**

Stop the Dashboard when not in use:
```bash
# Stop Dashboard
aws ecs update-service \
  --cluster nagarro-agentic-dev-cluster \
  --service nagarro-agentic-dev-service \
  --desired-count 0 \
  --region eu-central-1

# Start Dashboard (before demo)
aws ecs update-service \
  --cluster nagarro-agentic-dev-cluster \
  --service nagarro-agentic-dev-service \
  --desired-count 1 \
  --region eu-central-1
```

**Dashboard starts in ~2 minutes**

---

### Strategy 2: Destroy When Not Needed for Extended Period
**Save ~$55/month (everything)**

If not using for > 1 week:
```bash
cd infrastructure/terraform
terraform destroy
```

Redeploy anytime:
```bash
terraform apply
```

**Redeployment time: ~10 minutes**

---

### Strategy 3: Remove NAT Gateway Temporarily
**Save ~$32/month (biggest cost!)**

⚠️ **WARNING**: This requires infrastructure modification

If you don't need Lambda functions to access the internet:
1. Set `enable_nat_gateway = false` in `terraform.tfvars`
2. Run `terraform apply`

**Caveat**: ECS tasks in private subnets won't have internet access

---

## What We've Already Optimized

✅ **ECS**: Minimum CPU/Memory (256 CPU, 512 MB)
✅ **NAT**: Single NAT Gateway instead of 2 (saves $32/month)
✅ **DynamoDB**: On-demand pricing (no provisioned capacity)
✅ **CloudWatch**: 1-day log retention (vs 30+ days)
✅ **Monitoring**: Container Insights disabled (saves ~$5/month)
✅ **Encryption**: KMS disabled (saves ~$3/month)
✅ **Backups**: No automated backups
✅ **Logging**: Bedrock model logging disabled

---

## Free Tier Benefits (First 12 Months)

If this is a **new AWS account**, you get:
- ✅ **750 hours/month** of t2.micro EC2 (not used, but available)
- ✅ **5 GB** of S3 storage free
- ✅ **25 GB** of DynamoDB storage free
- ✅ **1 million Lambda requests** free

**This won't significantly reduce costs** because we're using Fargate (not in free tier), but S3 and DynamoDB will be effectively free.

---

## Cost Monitoring

### Set Up Billing Alerts (Recommended)
1. Go to AWS Console → Billing → Billing Preferences
2. Enable "Receive Billing Alerts"
3. Create CloudWatch Alarm:
   ```bash
   aws cloudwatch put-metric-alarm \
     --alarm-name "AWS-Cost-Alert" \
     --alarm-description "Alert when costs exceed $70" \
     --metric-name EstimatedCharges \
     --namespace AWS/Billing \
     --statistic Maximum \
     --period 21600 \
     --evaluation-periods 1 \
     --threshold 70 \
     --comparison-operator GreaterThanThreshold
   ```

### Check Current Costs
```bash
# View current month costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost
```

---

## Architecture Decisions for Cost

| Decision | Alternative | Cost Savings |
|----------|------------|--------------|
| Fargate vs EC2 | EC2 t3.micro | ~$0 (similar) |
| Single NAT | NAT per AZ | $32/month |
| No monitoring | Container Insights | $5/month |
| 1-day logs | 30-day logs | $3/month |
| No KMS | KMS encryption | $3/month |
| On-demand DDB | Provisioned | Varies |

---

## Monthly Cost Projection by Usage

| Usage Pattern | Monthly Cost |
|--------------|-------------|
| **Always On (24/7)** | ~$55-60 |
| **Weekdays only (8hrs/day)** | ~$35-40 |
| **Demo days only (4hrs/week)** | ~$25-30 |
| **Destroyed when not needed** | ~$0 (redeploy when needed) |

---

## Recommended for Your Use Case (Client Demos)

**Option A: Keep Infrastructure, Stop ECS When Not Demoing**
- Monthly: ~$50 (ALB + NAT always on)
- Start Dashboard 2 min before demo
- Best for: Frequent demos (weekly+)

**Option B: Destroy & Redeploy As Needed**
- Monthly: ~$0 (only pay when deployed)
- Redeploy takes 10 minutes
- Best for: Occasional demos (monthly)

**My Recommendation**: **Option A** - Keep infrastructure running, stop/start ECS as needed.

---

## Questions?

Run this anytime to see current costs:
```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '30 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```
