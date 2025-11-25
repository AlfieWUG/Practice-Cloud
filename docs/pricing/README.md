# AWS Pricing Documentation

This folder contains comprehensive cost analysis and pricing information for the Nagarro Agentic Services Platform.

---

## 📄 Documents in This Folder

### 1. **AWS_COST_ANALYSIS.md**
**Complete AWS cost breakdown for production deployment**

**Contents:**
- Monthly and annual cost projections for all environments (dev, staging, production)
- Service-by-service pricing breakdown (12 AWS services)
- Cost optimization strategies (30-60% savings)
- ROI analysis (99.9% savings vs traditional consulting)
- 3-year cost projection
- Budget recommendations and alerts

**Key Findings:**
- Development: $200-300/month
- Staging: $300-500/month
- Production: $800-1,200/month
- **Total: $1,300-2,000/month**
- Annual: $15,600-24,000

**Break-even:** 1-2 customer projects per month pays for entire platform

---

### 2. **AWS_FREE_TIER_ANALYSIS.md**
**How to build and test using AWS Free Tier**

**Contents:**
- Service-by-service free tier eligibility
- Cost comparison: Free Tier vs Standard
- 12-month development strategy
- Implementation checklist
- Cost control scripts
- Common gotchas to avoid

**Key Findings:**
- Months 1-3 (POC): $0-30/month (90% savings)
- Months 4-12 (Dev): $30-90/month (75% savings)
- **First year savings: $2,295 (77% reduction)**

**Free Forever:**
- DynamoDB (25 GB)
- EventBridge (1M events/month)
- CloudWatch (10 alarms, 5 GB logs)
- Parameter Store (unlimited secrets)

**Free for 12 Months:**
- EC2 t2.micro (750 hours/month)
- S3 (5 GB storage)

---

## 💰 Quick Comparison

| Scenario | Monthly Cost | Annual Cost | Best For |
|----------|--------------|-------------|----------|
| **Free Tier Optimized** | $20-90 | $705 | POC & Development (Year 1) |
| **Standard Development** | $200-300 | $2,400-3,600 | Active Development |
| **Production** | $800-1,200 | $9,600-14,400 | Live Customer Usage |
| **All Environments** | $1,300-2,000 | $15,600-24,000 | Full Platform |

---

## 🎯 Which Document Should I Read?

### For POC/Development Phase:
👉 **Read:** `AWS_FREE_TIER_ANALYSIS.md`
- You want to minimize costs
- You're in months 1-12 of development
- You have a new AWS account

### For Production Planning:
👉 **Read:** `AWS_COST_ANALYSIS.md`
- You're planning production deployment
- You need to budget for operational costs
- You're past the 12-month free tier

### For Complete Picture:
👉 **Read Both:**
- Start with Free Tier strategy for initial deployment
- Reference Cost Analysis for production planning

---

## 📊 Cost Drivers by Service

### Primary Costs (75-85% of budget):
1. **AWS Bedrock (Claude AI)** - 40-75% of total
   - $3-5 per project
   - Production: $300-500/month

2. **ECS Fargate (Compute)** - 10-25%
   - Production: $200-300/month

3. **VPC/Networking** - 10-20%
   - NAT Gateways: $130/month
   - Load Balancer: $23/month

### Secondary Costs (15-25% of budget):
4. S3 Storage - $5-50/month
5. DynamoDB - $5-80/month
6. CloudWatch - $10-120/month
7. Other services - $20-50/month

---

## 💡 Key Optimization Strategies

### Immediate Savings (30-40%):
1. Right-size ECS tasks → Save $100-150/month
2. S3 lifecycle policies → Save $50-100/month
3. Single NAT for dev/staging → Save $65/month
4. Token caching for Bedrock → Save $50-150/month
5. Reduce CloudWatch retention → Save $20-40/month

### Long-term Savings (50-60%):
6. Reserved Instances (1-3 year) → Save 30-50%
7. DynamoDB provisioned capacity → Save $30-50/month
8. VPC Endpoints → Save $30-50/month
9. Compress logs → Save $20-30/month

---

## 🔗 Related Documentation

- **FTR Readiness:** `../AWS_FTR_READINESS.md` - Infrastructure requirements
- **Architecture:** `../architecture/` - Technical design
- **Agent Implementation:** `../AGENT_IMPLEMENTATION_UPDATE.md` - Development status

---

## 📝 Cost Tracking

### Recommended Tools:
- **AWS Cost Explorer** - Daily cost monitoring
- **AWS Budgets** - Automated alerts
- **AWS Trusted Advisor** - Optimization recommendations
- **Cost Allocation Tags** - Detailed breakdowns

### Budget Alerts:
```
Development:   $300/month   (Alert at 80% = $240)
Staging:       $500/month   (Alert at 80% = $400)  
Production:    $1,200/month (Alert at 80% = $960)
```

---

## 🎓 Cost Estimation Examples

### Example 1: Small Team (10-20 projects/month)
- Development: $150-200/month
- Staging: $200-300/month
- Production: $400-600/month
- **Total: $750-1,100/month**

### Example 2: Medium Team (50-100 projects/month)
- Development: $200-250/month
- Staging: $300-400/month
- Production: $800-1,000/month
- **Total: $1,300-1,650/month**

### Example 3: Large Team (200+ projects/month)
- Development: $250-300/month
- Staging: $400-500/month
- Production: $1,200-1,800/month
- **Total: $1,850-2,600/month**

---

## 💸 ROI Calculation

### Traditional Consulting:
- $1,500/day × 40 days = **$58,500 per project**

### Agentic Platform:
- Platform cost: $1,500/month (all environments)
- Cost per project: $5-10
- **100 projects = $1,000 vs $5,850,000**

### Savings: 99.9% per project

**Break-even:** Platform pays for itself after just 1-2 customer projects!

---

## ✅ Cost Optimization Checklist

- [ ] Enable S3 lifecycle policies
- [ ] Configure CloudWatch log retention (7 days dev, 30 days prod)
- [ ] Implement Bedrock token caching
- [ ] Right-size ECS tasks (start small, scale up)
- [ ] Use VPC Endpoints for S3/DynamoDB
- [ ] Set up AWS Budgets with alerts
- [ ] Enable Cost Allocation Tags
- [ ] Review Trusted Advisor monthly
- [ ] Consider Reserved Instances after 6 months
- [ ] Compress CloudWatch logs
- [ ] Delete old ECR images
- [ ] Use single NAT Gateway for dev/staging

---

## 📞 Questions?

For cost-related questions:
- Review AWS Cost Explorer
- Check AWS Trusted Advisor
- Contact: aaldert.oosthuizen@nagarro.com

---

**Last Updated:** 2025-01-11  
**Next Review:** Monthly  
**Owner:** Platform Engineering Team
