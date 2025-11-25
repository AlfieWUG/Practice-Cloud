# AWS Environment - Quick Reference

## 💰 Cost Summary

| Environment | Monthly | Annual | Use Case |
|-------------|---------|--------|----------|
| **DEV** | $6-20 | $72-240 | Development, no NAT Gateway |
| **STAGING** | $80-130 | $960-1,560 | Client demos |
| **PROD** | $500-2,000 | $6K-24K | Per client |

---

## 🔧 Services Required

### Critical Services
- ✅ **Amazon Bedrock** - Claude 3 AI ($0.003/1K tokens)
- ✅ **AWS App Runner** - Dashboard hosting ($13-15/month DEV)
- ✅ **S3** - Artifact storage ($0.023/GB/month)
- ✅ **DynamoDB** - State management (25 GB free)
- ✅ **EventBridge** - Orchestration ($1/million events)

### Supporting Services
- **VPC** - Network (free + NAT Gateway $35/month)
- **CloudWatch** - Logging ($0.50/GB ingested)
- **Secrets Manager** - Credentials ($0.40/secret/month)
- **ECR** - Docker images ($0.10/GB/month)

---

## 📊 Data Estimates (per client)

| Data Type | Size | Retention |
|-----------|------|-----------|
| Discovery data | 100-500 MB | 1 year |
| Analysis results | 50-200 MB | 1 year |
| Migration plans | 20-100 MB | 2 years |
| Artifacts (Terraform, scripts) | 200MB-2GB | 2 years |
| **Total per client** | **0.5-3 GB** | - |

**AI Token Usage**: ~1.6M tokens/project = $6-10 in AI costs

---

## 🚀 Setup Checklist

### Week 1: Account Setup
- [ ] Create AWS account (1-2 days)
- [ ] Enable MFA on root account
- [ ] Request Bedrock model access (2-3 days)
- [ ] Setup billing alerts ($100/month threshold)

### Week 2: Infrastructure
- [ ] Create S3 bucket for Terraform state
- [ ] Create DynamoDB table for state locking
- [ ] Create ECR repository for Docker images
- [ ] Deploy Terraform infrastructure (1 day)

### Week 3: CI/CD
- [ ] Configure GitLab CI/CD variables:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_ACCOUNT_ID`
  - `AWS_DEFAULT_REGION` (eu-central-1)
- [ ] Push code to trigger pipeline

---

## 💡 Cost Optimization Tips

1. **Start with DEV only** ($6-20/month)
   - Remove NAT Gateway
   - Use mock services for testing (current setup = $0)

2. **Use Claude 3 Haiku for non-critical agents** (20x cheaper)
   - Sonnet: $0.015/1K output tokens
   - Haiku: $0.00125/1K output tokens

3. **Set CloudWatch log retention**
   - DEV: 7 days
   - PROD: 30 days
   - Saves 50% on storage costs

4. **Enable S3 Intelligent Tiering** (30-40% savings)

---

## 📈 Growth Projection

| Milestone | Timeline | AWS Cost/Month |
|-----------|----------|----------------|
| MVP Development | Month 1-2 | **$0** (mocks) |
| AWS Integration | Month 3 | **$60** |
| First Client Demo | Month 4-5 | **$160** |
| Production Launch | Month 6 | **$660** |
| 5 Clients | Year 2 | **$2,500** |
| 10 Clients | Year 3 | **$4,500** |

**3-Year TCO**: $73,200 (conservative) to $115,200 (aggressive)

---

## 🎯 Immediate Action Items

### For Finance Team
1. Approve $100/month budget for DEV environment
2. Provide AWS account or authorize new account creation
3. Assign corporate credit card for AWS billing

### For DevOps/Infra Team
1. Create AWS Organization (if doesn't exist)
2. Setup IAM roles for GitLab CI/CD
3. Enable Bedrock model access in Console
4. Configure AWS budgets and alarms

### For Development Team
1. Continue building agents with mock services ($0 cost)
2. Push code to GitLab to verify CI/CD
3. Prepare for AWS integration testing

---

## 📞 Questions?

**Technical Lead**: André Aldertoosthuizen  
**Email**: aaldertoosthuizen@nagarro.com  

**Full Details**: See `AWS-TCO-ESTIMATE.md`  
**Setup Guide**: See `CI-CD-SETUP.md`

---

**Timeline**: AWS environment ready in 2-3 weeks  
**Current Status**: CI/CD complete ✅, awaiting AWS account approval
