# Deployment & IP Protection Strategy
## Agentic Services Platform

**Version**: 1.0  
**Last Updated**: November 2025  
**Classification**: Confidential - Internal Use Only

---

## 🎯 Executive Summary

The Agentic Services Platform contains proprietary AI agent implementations, orchestration logic, and optimization algorithms that represent significant competitive advantage. This document outlines our strategy for deploying to client environments while protecting intellectual property.

**Key Principles**:
1. **Never share source code** - Deploy as compiled/containerized services only
2. **SaaS-first delivery** - Client accesses via API, we retain control
3. **Managed service option** - We operate infrastructure, client pays subscription
4. **Strict licensing** - Legal agreements before any deployment

---

## 🔐 IP Protection Layers

### Layer 1: Legal Protection

#### Non-Disclosure Agreements (NDAs)
- **Mutual NDA** signed before any technical discussions
- **Unilateral NDA** for client-side personnel accessing dashboard
- **Survival clause**: 5 years post-engagement
- **Covers**: Architecture, algorithms, AI prompts, orchestration logic

#### Master Service Agreement (MSA)
```
Key Clauses:
- IP Ownership: All code, algorithms, and AI models remain Nagarro property
- Usage Rights: Client receives limited license to USE, not OWN
- No Reverse Engineering: Explicitly prohibited
- No Competitive Use: Client cannot build competing services
- Audit Rights: Nagarro can audit client's usage
- Termination: All access revoked upon contract end
```

#### License Agreement
- **Subscription-based**: Annual renewal required
- **Scope-limited**: Specific to client's agreed workloads
- **Non-transferable**: Cannot be sold or assigned
- **Revocable**: Immediate termination on breach

### Layer 2: Technical Protection

#### Code Obfuscation & Compilation
```bash
# Python bytecode compilation (basic)
python -m compileall src/

# Advanced obfuscation (using pyarmor)
pyarmor obfuscate --recursive src/agentic_services/

# Result: .pyc files only, no source code
```

#### Container-Based Deployment
```dockerfile
# Multi-stage build - source never leaves build stage
FROM python:3.11-slim AS builder
COPY src/ /build/src/
RUN python -m compileall /build/src/ && \
    pyarmor obfuscate --recursive /build/src/

FROM python:3.11-slim
COPY --from=builder /build/dist/ /app/
# Source code never in final image
```

#### Encrypted Environment Variables
```bash
# Sensitive configuration encrypted
AWS_BEDROCK_MODEL="<encrypted>"
ORCHESTRATION_SECRET="<encrypted>"
AGENT_CONFIG="<base64-encrypted-json>"
```

#### No Debug Symbols
```python
# Production builds strip all debugging info
PYTHON_OPTIMIZE=2  # Remove docstrings and assertions
DEBUG=False
LOG_LEVEL=WARNING  # No verbose debug logs
```

### Layer 3: Deployment Architecture

#### Option A: SaaS Platform (Recommended)

**Architecture**:
```
┌─────────────────────────────────────────────────┐
│  CLIENT ENVIRONMENT                             │
│  ┌───────────────────────────────────────┐     │
│  │  Streamlit Dashboard (Read-Only)      │     │
│  │  - View migration progress            │     │
│  │  - Review recommendations             │     │
│  │  - Approve/reject actions             │     │
│  └───────────────────────────────────────┘     │
│                    ↓ HTTPS/API                  │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  NAGARRO-CONTROLLED AWS ACCOUNT                 │
│  ┌───────────────────────────────────────┐     │
│  │  API Gateway (Authentication)         │     │
│  └───────────────────────────────────────┘     │
│  ┌───────────────────────────────────────┐     │
│  │  20 AI Agents (Closed Source)         │     │
│  │  - All orchestration logic            │     │
│  │  - All AI prompts                     │     │
│  │  - All optimization algorithms        │     │
│  └───────────────────────────────────────┘     │
│  ┌───────────────────────────────────────┐     │
│  │  AWS Bedrock (Claude 3)               │     │
│  └───────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  CLIENT INFRASTRUCTURE (Read-Only Access)       │
│  - Discovery agents scan via API               │
│  - No code deployed to client environment      │
└─────────────────────────────────────────────────┘
```

**Advantages**:
- ✅ **Maximum IP protection** - No code in client environment
- ✅ **Easy updates** - Deploy once, all clients benefit
- ✅ **Usage tracking** - Monitor and bill accurately
- ✅ **Quick termination** - Revoke API keys instantly
- ✅ **Multi-tenant** - Shared infrastructure, lower costs

**Client Access**:
- API keys with rate limiting
- Dashboard URL with SSO integration
- Read-only access to their project data
- No access to platform internals

**Data Handling**:
- Client data stored in isolated S3 buckets
- DynamoDB tables partitioned by client
- Encryption at rest and in transit
- Data residency compliance (EU, US, etc.)

#### Option B: Managed Private Instance

**Architecture**:
```
┌─────────────────────────────────────────────────┐
│  CLIENT'S AWS ACCOUNT (Managed by Nagarro)      │
│  ┌───────────────────────────────────────┐     │
│  │  ECS Fargate (Containers Only)        │     │
│  │  - No SSH access                      │     │
│  │  - No shell access                    │     │
│  │  - No debug mode                      │     │
│  └───────────────────────────────────────┘     │
│  ┌───────────────────────────────────────┐     │
│  │  Container Registry (ECR)             │     │
│  │  - Nagarro-controlled                 │     │
│  │  - Pull-only access                   │     │
│  └───────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
         ↑
         │ CI/CD Pipeline (Nagarro GitLab)
         │
┌────────┴────────────────────────────────────────┐
│  NAGARRO INFRASTRUCTURE                         │
│  - Source code never leaves                     │
│  - Automated builds                             │
│  - Push to client ECR only                      │
└─────────────────────────────────────────────────┘
```

**Advantages**:
- ✅ **Client data stays in their AWS** - Compliance-friendly
- ✅ **Dedicated resources** - Performance guarantees
- ✅ **Still IP protected** - Containers only, no source

**Disadvantages**:
- ❌ **Higher cost** - Dedicated infrastructure per client
- ❌ **More complex updates** - Need to update each instance
- ❌ **Potential security gaps** - Client has AWS console access

**Protection Mechanisms**:
```yaml
# ECS Task Definition
containerDefinitions:
  - name: agentic-services
    image: <nagarro-ecr>/agentic-services:latest
    readonlyRootFilesystem: true  # No file writes
    privileged: false
    user: "1000"  # Non-root user
    entrypoint: ["/app/run.sh"]  # No shell access
    linuxParameters:
      capabilities:
        drop: ["ALL"]  # Drop all capabilities
```

#### Option C: On-Premise Appliance (Highest Risk)

**Only for**: Government, financial institutions with strict data residency

**Architecture**:
```
┌─────────────────────────────────────────────────┐
│  CLIENT DATA CENTER                             │
│  ┌───────────────────────────────────────┐     │
│  │  Sealed Appliance (Hardware TPM)      │     │
│  │  - Encrypted storage                  │     │
│  │  - Tamper detection                   │     │
│  │  - Remote kill switch                 │     │
│  │  - No root access                     │     │
│  └───────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
         ↑
         │ Encrypted VPN (for updates only)
         │
┌────────┴────────────────────────────────────────┐
│  NAGARRO SUPPORT INFRASTRUCTURE                 │
│  - License validation                           │
│  - Update deployment                            │
│  - Usage telemetry                              │
└─────────────────────────────────────────────────┘
```

**Protection Mechanisms**:
- Hardware TPM chip for encryption keys
- Secure boot with signed kernels
- Encrypted root filesystem
- No SSH access (console only for emergencies)
- License server phone-home (daily check)
- Remote wipe capability
- Audit logging to Nagarro SIEM

**License Enforcement**:
```python
# License check on every agent execution
def validate_license():
    if not license_server.check_license(client_id):
        raise LicenseViolation("Invalid or expired license")
    
    if usage_exceeds_limit(client_id):
        raise LicenseViolation("Usage limit exceeded")
    
    return True
```

---

## 🚀 Client Onboarding Process

### Phase 1: Pre-Sales (Week -4 to -1)

**Week -4: Initial Engagement**
- [ ] Execute Mutual NDA
- [ ] Technical discovery call
- [ ] Demo platform (our environment)
- [ ] Gather requirements
- [ ] Assess deployment model fit

**Week -3: Proposal**
- [ ] Architecture review
- [ ] Pricing proposal
- [ ] Deployment model recommendation
- [ ] Data residency discussion
- [ ] Compliance requirements (GDPR, HIPAA, etc.)

**Week -2: Legal**
- [ ] MSA negotiation
- [ ] License agreement review
- [ ] SLA definition
- [ ] Security questionnaire response
- [ ] Insurance verification

**Week -1: Pre-Deployment**
- [ ] MSA signed
- [ ] Invoice 1 (setup fee) sent
- [ ] AWS account setup (if managed instance)
- [ ] Network connectivity test
- [ ] SSO integration planning

### Phase 2: Technical Onboarding (Week 1-2)

**Day 1-2: Environment Provisioning**
```bash
# SaaS Option
./scripts/onboard-client.sh \
  --client-id "client-abc" \
  --tier "enterprise" \
  --region "eu-central-1"

# Managed Instance Option
./scripts/deploy-private.sh \
  --client-id "client-abc" \
  --aws-account "123456789012" \
  --region "us-east-1"
```

**Day 3-5: Integration**
- [ ] API keys generated
- [ ] Dashboard access configured
- [ ] SSO integration complete
- [ ] Network discovery agent configured
- [ ] Test scan on dev environment
- [ ] Security audit (pen test if required)

**Day 6-7: Training**
- [ ] Admin training (4 hours)
- [ ] User training (2 hours)
- [ ] Documentation handover
- [ ] Support channel setup (Slack/Teams)

**Day 8-10: Pilot Migration**
- [ ] Select 3-5 low-risk workloads
- [ ] Run discovery phase
- [ ] Review analysis and planning
- [ ] Execute migration (with approval gates)
- [ ] Validate success
- [ ] Document lessons learned

### Phase 3: Production Rollout (Week 3-4)

**Week 3: Scale-Up**
- [ ] Production migration plan approved
- [ ] Schedule communicated
- [ ] Runbooks documented
- [ ] Rollback procedures tested
- [ ] Support escalation defined

**Week 4: Go-Live**
- [ ] Production migrations executed
- [ ] 24/7 monitoring active
- [ ] Daily status reports
- [ ] Weekly stakeholder updates
- [ ] Post-migration validation

### Phase 4: Steady State (Month 2+)

**Monthly**:
- [ ] License compliance audit
- [ ] Usage report sent
- [ ] Invoice for usage
- [ ] Platform updates deployed
- [ ] Performance review

**Quarterly**:
- [ ] Business review with stakeholders
- [ ] Roadmap discussion
- [ ] Security audit
- [ ] Renewal discussion (if annual)

---

## 🛡️ Security Controls

### Access Control Matrix

| Role | Dashboard | API | Logs | Admin | Source Code |
|------|-----------|-----|------|-------|-------------|
| **Client User** | Read | No | Own projects | No | Never |
| **Client Admin** | Read/Write | Limited | Own projects | Project-level | Never |
| **Nagarro Support** | Read | Yes | All projects | Yes | Yes |
| **Nagarro Dev** | Admin | Yes | All projects | Full | Yes |

### Monitoring & Alerting

**Security Events Monitored**:
```yaml
alerts:
  - name: "Unusual API Activity"
    condition: "requests > 1000/min OR failures > 10%"
    action: "Alert + Rate limit"
  
  - name: "Unauthorized Access Attempt"
    condition: "Invalid API key OR expired license"
    action: "Alert + Block + Log"
  
  - name: "Data Exfiltration Attempt"
    condition: "Download > 10GB OR to unexpected IPs"
    action: "Alert + Block + Investigate"
  
  - name: "License Violation"
    condition: "Usage > license limit OR expired"
    action: "Alert + Graceful shutdown"
  
  - name: "Container Intrusion"
    condition: "Shell spawned OR file system modifications"
    action: "Alert + Kill container + Forensics"
```

### Audit Logging

**All Actions Logged**:
- API requests (who, what, when, from where)
- Agent executions (inputs, outputs, duration)
- Configuration changes
- User logins/logouts
- Data access (which files, by whom)
- Errors and exceptions

**Log Retention**:
- **Production**: 12 months
- **Compliance logs**: 7 years
- **Security events**: Indefinite

**Log Analysis**:
```python
# Automated anomaly detection
def detect_anomalies(client_id):
    baseline = get_usage_baseline(client_id, days=30)
    current = get_usage_current(client_id)
    
    if current.api_calls > baseline.api_calls * 2:
        alert("Unusual API activity", severity="high")
    
    if current.data_downloads > baseline.data_downloads * 3:
        alert("Potential data exfiltration", severity="critical")
```

---

## 💰 Pricing & Licensing Models

### Model 1: SaaS Subscription

**Tier 1: Starter** ($50K/year)
- Up to 50 workloads/year
- 3 concurrent migrations
- Email support (24-hour SLA)
- Standard SLA (99.5% uptime)

**Tier 2: Professional** ($150K/year)
- Up to 200 workloads/year
- 10 concurrent migrations
- Priority support (4-hour SLA)
- Enhanced SLA (99.9% uptime)
- Dedicated success manager

**Tier 3: Enterprise** ($500K/year)
- Unlimited workloads
- Unlimited concurrent migrations
- 24/7 phone support (1-hour SLA)
- Premium SLA (99.95% uptime)
- Dedicated technical account manager
- Custom integrations included
- Annual business reviews

### Model 2: Managed Private Instance

**Base**: $100K/year + $30K setup
- Dedicated AWS infrastructure
- Up to 500 workloads/year
- All Enterprise features
- Client's AWS account
- Nagarro manages 24/7

**Add-ons**:
- High Availability: +$50K/year
- Disaster Recovery: +$30K/year
- Additional regions: +$40K/region/year

### Model 3: Usage-Based

**Pay-per-Migration**:
- Small (< 50 workloads): $150K - $300K
- Medium (50-200): $300K - $600K
- Large (200+): $600K - $1.5M

**Includes**:
- Platform access during migration
- All agents and features
- Support during migration window
- 90-day post-migration support

---

## 🔒 IP Protection Checklist

### Before Client Engagement
- [ ] Mutual NDA signed
- [ ] Legal team review complete
- [ ] MSA template updated
- [ ] License agreement prepared
- [ ] Security questionnaire ready

### Before Deployment
- [ ] MSA fully executed
- [ ] License keys generated
- [ ] Client environment audited
- [ ] Network security validated
- [ ] Backup and DR tested

### During Deployment
- [ ] Only compiled/containerized code deployed
- [ ] No source code leaves Nagarro infrastructure
- [ ] All access logged and monitored
- [ ] License validation active
- [ ] Kill switch tested

### Post-Deployment
- [ ] Monthly license compliance check
- [ ] Quarterly security audit
- [ ] Usage monitoring active
- [ ] Client satisfaction survey
- [ ] Renewal notice (90 days prior)

### Upon Termination
- [ ] API keys revoked immediately
- [ ] Access to dashboard disabled
- [ ] Client data archived (per agreement)
- [ ] Containers/appliances wiped
- [ ] Final invoice settled
- [ ] Post-termination NDA reminder

---

## 🚨 Breach Response Plan

### Suspected IP Theft

**Immediate Actions** (Within 1 hour):
1. Revoke all client API keys
2. Disable client's dashboard access
3. Capture forensic logs
4. Alert legal team
5. Document timeline

**Investigation** (Within 24 hours):
1. Analyze access logs
2. Check data download history
3. Interview support team
4. Review client communication
5. Gather evidence

**Legal Action** (Within 48 hours):
1. Send cease & desist letter
2. Demand return of all materials
3. File lawsuit if necessary
4. Seek injunction
5. Calculate damages

**Prevention** (Within 1 week):
1. Review and strengthen controls
2. Update MSA for future clients
3. Enhance monitoring
4. Train team on lessons learned
5. Implement additional protections

---

## 📋 Client Handoff Documentation

### What Clients Receive

**Documentation**:
- User guides (PDF/online)
- API documentation (Swagger)
- Architecture overview (high-level only)
- Troubleshooting guides
- FAQ

**Access**:
- Dashboard URLs
- API endpoints
- API keys (encrypted)
- Support channels
- Escalation contacts

**Training Materials**:
- Video tutorials
- Hands-on labs (in their environment)
- Best practices guide
- Migration playbooks

### What Clients DON'T Receive

**Never Shared**:
- Source code
- AI prompts
- Orchestration algorithms
- Internal architecture diagrams
- Database schemas
- Encryption keys
- Admin credentials to our infrastructure

---

## 🎓 Key Recommendations

### For Maximum IP Protection:
1. ✅ **Default to SaaS model** - Keep code in our environment
2. ✅ **Managed instance second choice** - Containers only
3. ✅ **Avoid on-premise** - Highest risk, lowest return
4. ✅ **Strong legal agreements** - Enforce with audits
5. ✅ **Continuous monitoring** - Detect and respond quickly
6. ✅ **License enforcement** - Technical + legal controls
7. ✅ **Regular audits** - Quarterly security reviews
8. ✅ **Incident response ready** - Practice breach scenarios

### For Successful Onboarding:
1. ✅ **Start small** - Pilot migration first
2. ✅ **Train thoroughly** - Reduce support burden
3. ✅ **Set expectations** - Clear SLAs and limits
4. ✅ **Measure success** - Track metrics religiously
5. ✅ **Regular communication** - Weekly updates minimum
6. ✅ **Document everything** - Audit trail essential
7. ✅ **Build relationships** - Long-term partnerships
8. ✅ **Continuous improvement** - Learn from each client

---

## 📞 Escalation Contacts

**Security Incident**: security-incident@nagarro.com (24/7)  
**Legal Issues**: legal@nagarro.com  
**License Violations**: license-compliance@nagarro.com  
**Technical Support**: agentic-support@nagarro.com  
**Sales/Renewals**: agentic-sales@nagarro.com  

---

**Document Owner**: André Aldertoosthuizen  
**Review Cycle**: Quarterly  
**Next Review**: February 2026  
**Classification**: Confidential - Do Not Distribute
