# Nagarro Agentic Services Platform - Architecture Overview
## Technical Architecture v2.0

**Last Updated**: 2025-01-15  
**Version**: 2.0 (Updated with Serverless Architecture)  
**Status**: Production-Ready  

---

## Executive Summary

The Nagarro Agentic Services Platform is a **serverless, AI-powered cloud migration and modernization platform** built on AWS. It deploys **24 specialized AI agents** to automate the entire migration lifecycle, from discovery to optimization.

### Key Differentiators
- **Serverless-First**: 100% serverless architecture (Lambda, API Gateway, DynamoDB)
- **AI-Native**: AWS Bedrock (Claude 3) powers all 24 agents
- **Event-Driven**: EventBridge orchestrates multi-agent workflows
- **Cost-Optimized**: Pay-per-use model, no idle infrastructure costs
- **Fully Automated**: End-to-end migration automation (60-80% time savings)

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │  Streamlit  │  │   API Keys   │  │  CloudWatch  │  │    CLI       ││
│  │  Dashboard  │  │   (Future)   │  │  Dashboards  │  │    Tools     ││
│  └─────────────┘  └──────────────┘  └──────────────┘  └──────────────┘│
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                         API GATEWAY LAYER                                │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  HTTP API Gateway (Cost-Optimized)                                │ │
│  │  • 48+ Routes (2 per agent: execute + status)                     │ │
│  │  • Health Check, List Agents, Utility Endpoints                   │ │
│  │  • CORS, Throttling (100 burst, 50/sec rate)                      │ │
│  │  • Optional: JWT Auth, Custom Domain, API Keys                    │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                         COMPUTE LAYER (SERVERLESS)                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  24 Lambda Functions (Python 3.11)                              │   │
│  │  ┌────────────┬────────────┬────────────┬────────────────────┐ │   │
│  │  │ Discovery  │ Assessment │ Execution  │   Optimization     │ │   │
│  │  │ Phase (8)  │ Phase (5)  │ Phase (6)  │   Phase (5)        │ │   │
│  │  └────────────┴────────────┴────────────┴────────────────────┘ │   │
│  │  • Shared Dependency Layer (boto3, anthropic, pydantic)        │   │
│  │  • Dead Letter Queue (SQS) for failures                        │   │
│  │  • CloudWatch Logs (7-day retention)                           │   │
│  │  • 1GB memory, 300s timeout, 2 retries                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                         AI & ORCHESTRATION LAYER                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │  AWS Bedrock     │  │  EventBridge     │  │  Step Functions  │     │
│  │  Claude 3 Sonnet │  │  Event Bus       │  │  (Future)        │     │
│  │  • All 24 agents │  │  • Agent coord   │  │  • Workflows     │     │
│  │  • Structured    │  │  • Event routing │  │  • Orchestration │     │
│  │    output        │  │  • Async comms   │  │                  │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                         DATA & STORAGE LAYER                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │  DynamoDB        │  │  S3 Buckets (3)  │  │  CloudWatch      │     │
│  │  (On-Demand)     │  │                  │  │  Logs            │     │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤     │
│  │ • Agent State    │  │ • Discovery Data │  │ • Lambda Logs    │     │
│  │ • Workflow Data  │  │ • Artifacts      │  │ • API Logs       │     │
│  │ • Metadata       │  │ • System Logs    │  │ • Bedrock Logs   │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                    MONITORING & SECURITY LAYER                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │  CloudWatch      │  │  IAM Roles       │  │  Secrets Manager │     │
│  │  Alarms & SNS    │  │  & Policies      │  │  (Future)        │     │
│  │  • 4XX/5XX errors│  │  • Lambda role   │  │  • API keys      │     │
│  │  • Cost alerts   │  │  • Bedrock perm  │  │  • Credentials   │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘

Region: AWS eu-central-1 (Frankfurt)
Deployment: 100% Serverless (No VPC, No EC2, No ECS in current version)
```

---

## 2. Component Details

### 2.1 Presentation Layer

#### Streamlit Dashboard
- **Technology**: Python Streamlit 1.32.0
- **Hosting**: Local/Cloud Run (containerized)
- **Features**:
  - Agent overview (3-column grid layout)
  - 3 focus areas (Migration & Modernization, FinOps, AIOps)
  - Real-time agent status
  - Project management
  - Results visualization

#### API Consumers
- **Dashboard**: Streamlit UI calls API Gateway
- **CLI Tools**: Python CLI for automation
- **External Systems**: Webhook integrations (future)
- **Monitoring**: CloudWatch dashboards

---

### 2.2 API Gateway Layer

#### HTTP API Gateway
- **Type**: HTTP API (70% cheaper than REST API)
- **Cost**: ~$1 per million requests
- **Features**:
  - CORS enabled for web clients
  - Throttling: 100 burst, 50/sec rate
  - CloudWatch logging
  - Optional JWT/IAM authorization
  - Optional custom domain

#### API Endpoints

**Agent Execution (24 endpoints)**:
```
POST /agents/{agent-name}
Body: { "project_id": "...", "parameters": {...} }
Response: { "status": "success", "task_id": "...", "result": {...} }
```

**Agent Status (24 endpoints)**:
```
GET /agents/{agent-name}/status?task_id={id}
Response: { "status": "running|completed|failed", "progress": "...", "result": {...} }
```

**Utility Endpoints**:
```
GET /health              → Health check
GET /agents              → List all 24 agents
GET /agents/{name}/info  → Agent capabilities
```

---

### 2.3 Compute Layer - 24 Lambda Functions

#### Lambda Configuration
- **Runtime**: Python 3.11
- **Memory**: 1024 MB (1 GB)
- **Timeout**: 300 seconds (5 minutes)
- **Retry**: 2 attempts
- **DLQ**: SQS queue for failures
- **Layer**: Shared dependencies (~50-100 MB)
- **VPC**: Disabled (cost optimization, faster cold starts)

#### Agent Organization

**Discovery Phase (8 Agents)**
1. **infrastructure-scanner** - Infrastructure inventory and discovery
2. **application-profiler** - Application analysis and profiling
3. **data-discovery** - Data classification and PII detection
4. **integration-mapper** - Integration point identification
5. **security-auditor** - Security posture assessment
6. **network-analyzer** - Network topology and security scanning
7. **performance-baseline** - Performance metrics collection
8. **licensing-analyzer** - License compliance checking

**Assessment Phase (5 Agents)**
9. **dependency-mapper** - Dependency analysis and mapping
10. **compliance-checker** - Regulatory compliance validation (GDPR, HIPAA, PCI-DSS)
11. **cost-estimator** - Migration cost estimation and TCO
12. **risk-assessment** - Risk identification and scoring
13. **capacity-planner** - Resource capacity planning

**Execution Phase (6 Agents)**
14. **infrastructure-provisioner** - AWS infrastructure deployment (Terraform/CDK)
15. **data-migration** - Database and data migration
16. **application-migration** - Application deployment and cutover
17. **configuration** - Configuration management
18. **testing** - Testing orchestration and validation
19. **rollback** - Rollback and recovery automation

**Optimization Phase (5 Agents)**
20. **performance-optimizer** - Performance tuning recommendations
21. **cost-optimizer** - Cost optimization recommendations
22. **security-hardening** - Security configuration hardening
23. **monitoring-setup** - Monitoring and alerting setup
24. **documentation** - Documentation generation

---

### 2.4 AI & Orchestration Layer

#### AWS Bedrock (Claude 3 Sonnet)
- **Model**: anthropic.claude-3-sonnet-20240229-v1:0
- **Cost**: ~$3 per million input tokens, ~$15 per million output tokens
- **Features**:
  - 200K token context window
  - Structured JSON output
  - System prompts per agent
  - Tool use capability (future)
- **Integration**: All 24 agents invoke Bedrock

#### EventBridge Event Bus
- **Purpose**: Agent coordination and workflow orchestration
- **Events**:
  - `agent.started` - Agent execution started
  - `agent.completed` - Agent execution completed
  - `agent.failed` - Agent execution failed
  - `workflow.phase_completed` - Migration phase completed
- **Rules**: Route events to downstream agents
- **Cost**: First 1M events/month free, $1 per million after

#### Step Functions (Future)
- **Purpose**: Complex multi-agent workflows
- **Use Cases**:
  - Parallel agent execution
  - Conditional branching
  - Error handling and retries
  - Long-running workflows

---

### 2.5 Data & Storage Layer

#### DynamoDB (3 Tables)
**1. Agent State Table**
- **Purpose**: Track agent execution state
- **Partition Key**: `task_id`
- **Attributes**: status, result, timestamp, metadata
- **Pricing**: On-demand, ~$1.25 per million writes

**2. Workflow State Table**
- **Purpose**: Track multi-agent workflow state
- **Partition Key**: `project_id`
- **Sort Key**: `workflow_id`
- **Attributes**: phase, agents_completed, current_agent
- **Features**: DynamoDB Streams for real-time updates

**3. Project Metadata Table**
- **Purpose**: Store project details and configuration
- **Partition Key**: `project_id`
- **Attributes**: name, customer, requirements, constraints
- **Features**: TTL for automatic cleanup

#### S3 Buckets (3)
**1. Discovery Data Bucket**
- **Purpose**: Raw discovery data, scan results
- **Lifecycle**: 90-day transition to IA, 365-day deletion
- **Encryption**: SSE-S3 (AES-256)
- **Cost**: ~$0.023/GB/month

**2. Artifacts Bucket**
- **Purpose**: Generated artifacts (docs, diagrams, reports)
- **Lifecycle**: 180-day transition to IA
- **Versioning**: Enabled
- **Cost**: ~$0.023/GB/month

**3. Logs Bucket**
- **Purpose**: System logs, audit trails
- **Lifecycle**: 30-day retention, then delete
- **Encryption**: SSE-S3
- **Cost**: ~$0.023/GB/month

---

### 2.6 Monitoring & Security Layer

#### CloudWatch
- **Logs**: All Lambda functions, API Gateway
- **Retention**: 7 days (dev), 30 days (prod)
- **Alarms**:
  - API Gateway 4XX errors > threshold
  - API Gateway 5XX errors > threshold
  - Lambda errors > threshold
  - Lambda duration > 250s
  - DynamoDB throttling
- **SNS Topics**: Alert notifications

#### IAM Roles & Policies
**Lambda Execution Role**:
- Bedrock: `InvokeModel` on Claude models
- S3: Read/Write to all 3 buckets
- DynamoDB: Read/Write to all 3 tables
- EventBridge: `PutEvents` for coordination
- CloudWatch: `CreateLogGroup`, `CreateLogStream`, `PutLogEvents`
- SQS: `SendMessage` to DLQ

**API Gateway Role**:
- Lambda: `InvokeFunction` on all 24 functions
- CloudWatch: Logging permissions

#### Security Features
- **Encryption at Rest**: S3 (SSE-S3), DynamoDB (AWS-owned keys)
- **Encryption in Transit**: TLS 1.3 for all API calls
- **IAM**: Role-based access control
- **Secrets Manager**: API keys, credentials (future)
- **VPC**: Optional VPC deployment (disabled for cost optimization)

---

## 3. Data Flow

### 3.1 Single Agent Execution Flow

```
1. User/Dashboard → API Gateway
   POST /agents/infrastructure-scanner
   { "project_id": "proj-123", "parameters": {...} }

2. API Gateway → Lambda (infrastructure-scanner)
   Invokes Lambda function

3. Lambda Handler:
   a. Validate input
   b. Create task_id
   c. Save initial state to DynamoDB
   d. Emit "agent.started" event to EventBridge

4. Agent Execution:
   a. Load project data from S3/DynamoDB
   b. Invoke AWS Bedrock (Claude) with system prompt
   c. Process AI response
   d. Store results to S3
   e. Update state in DynamoDB
   f. Emit "agent.completed" event

5. Lambda → API Gateway → User
   Return: { "status": "completed", "task_id": "...", "result": {...} }
```

### 3.2 Multi-Agent Workflow Flow

```
1. Discovery Phase (8 agents run sequentially or parallel)
   └─> infrastructure-scanner
   └─> application-profiler
   └─> data-discovery
   └─> integration-mapper
   └─> security-auditor
   └─> network-analyzer
   └─> performance-baseline
   └─> licensing-analyzer
   
   EventBridge emits: workflow.phase_completed (discovery)

2. Assessment Phase (5 agents)
   └─> dependency-mapper (uses discovery data)
   └─> compliance-checker
   └─> cost-estimator
   └─> risk-assessment
   └─> capacity-planner
   
   EventBridge emits: workflow.phase_completed (assessment)

3. Execution Phase (6 agents)
   └─> infrastructure-provisioner (creates AWS resources)
   └─> data-migration (migrates databases)
   └─> application-migration (deploys applications)
   └─> configuration (applies configs)
   └─> testing (validates migration)
   └─> rollback (if testing fails)
   
   EventBridge emits: workflow.phase_completed (execution)

4. Optimization Phase (5 agents)
   └─> performance-optimizer (tunes performance)
   └─> cost-optimizer (reduces costs)
   └─> security-hardening (enhances security)
   └─> monitoring-setup (configures monitoring)
   └─> documentation (generates docs)
   
   EventBridge emits: workflow.phase_completed (optimization)

5. Workflow Complete
   └─> Final report generated
   └─> Stakeholder notifications
   └─> Archive to S3
```

---

## 4. Technology Stack

### Backend
- **Language**: Python 3.11
- **Compute**: AWS Lambda (serverless)
- **API**: HTTP API Gateway
- **AI**: AWS Bedrock (Claude 3 Sonnet)
- **Orchestration**: EventBridge (+ Step Functions future)

### Data Storage
- **NoSQL**: DynamoDB (on-demand)
- **Object Storage**: S3 (Standard + IA)
- **Caching**: None currently (ElastiCache future)

### Infrastructure
- **IaC**: Terraform 1.5+
- **CI/CD**: GitHub Actions (3 workflows)
- **Monitoring**: CloudWatch Logs, Metrics, Alarms
- **Tracing**: X-Ray (future)

### Frontend
- **Framework**: Streamlit 1.32.0
- **Language**: Python 3.11
- **Hosting**: Local/Cloud Run
- **API Client**: requests library

---

## 5. Cost Analysis

### Development Environment (Monthly)
| Service | Usage | Cost |
|---------|-------|------|
| **Lambda** | 10K invocations @ 1GB, 30s avg | $5-10 |
| **API Gateway** | 10K requests | $0.10 |
| **DynamoDB** | Light usage, on-demand | $2-5 |
| **S3** | 10GB storage + requests | $0.25 |
| **CloudWatch** | 5GB logs, 7-day retention | $2.50 |
| **EventBridge** | 10K events | $0.10 |
| **Bedrock** | 100K tokens (~33K words) | $30-50 |
| **Total** | | **$40-70** |

### Production Environment (Monthly)
| Service | Usage | Cost |
|---------|-------|------|
| **Lambda** | 100K invocations @ 1GB, 30s | $50-100 |
| **API Gateway** | 100K requests | $1 |
| **DynamoDB** | Heavy usage | $20-50 |
| **S3** | 100GB storage | $2.30 |
| **CloudWatch** | 30-day retention | $10-20 |
| **Bedrock** | 1M tokens | $300-500 |
| **Total** | | **$383-673** |

### Cost Optimization Features
- HTTP API (70% cheaper than REST)
- Lambda outside VPC (no NAT Gateway costs)
- DynamoDB on-demand (pay per request)
- 7-day log retention (configurable)
- S3 lifecycle policies (IA transition)
- No idle compute costs (100% serverless)

---

## 6. Deployment Architecture

### Environments

**Development (dev)**
- Purpose: Feature development and testing
- Cost: $40-70/month
- Resources: All services deployed
- Access: Development team only

**Staging (staging)**
- Purpose: Pre-production testing
- Cost: $100-150/month
- Resources: Production-like setup
- Access: QA and select customers

**Production (prod)**
- Purpose: Customer-facing environment
- Cost: $383-673/month (usage-based)
- Resources: Full production setup
- Access: All customers
- SLA: 99.9% uptime

### Deployment Process

```
1. Code Commit → GitHub
2. GitHub Actions CI:
   - Run tests (pytest)
   - Lint code (ruff, black, isort)
   - Security scan (bandit, semgrep)
   - Type check (mypy)
3. GitHub Actions CD (on main branch):
   - Build Lambda packages
   - Upload to S3
   - Terraform apply
   - Deploy infrastructure
   - Run smoke tests
4. Deployment Complete
```

---

## 7. Security Architecture

### Authentication & Authorization
- **API Keys**: Optional API key-based auth
- **JWT**: Optional JWT authorization
- **IAM**: Role-based access control
- **Cognito**: User pool (future)

### Data Protection
- **Encryption at Rest**: S3 (SSE-S3), DynamoDB (AWS-owned)
- **Encryption in Transit**: TLS 1.3 for all communications
- **Secrets**: Secrets Manager for credentials (future)
- **KMS**: Customer-managed keys (future)

### Network Security
- **No VPC**: Serverless architecture, no VPC required
- **WAF**: AWS WAF integration (future)
- **API Gateway**: Request throttling, CORS
- **DDoS**: AWS Shield Standard (included)

### Compliance
- **GDPR**: Data encryption, access control, audit logs
- **HIPAA**: Eligible services (Lambda, DynamoDB, S3)
- **SOC 2**: AWS infrastructure compliance
- **ISO 27001**: AWS infrastructure compliance

---

## 8. Monitoring & Observability

### Logging
- **Lambda Logs**: CloudWatch Logs (7-day retention)
- **API Logs**: API Gateway access logs
- **Bedrock Logs**: Model invocation logs (optional)
- **Audit Logs**: CloudTrail (future)

### Metrics
- **Lambda**: Invocations, errors, duration, throttles
- **API Gateway**: Request count, latency, errors
- **DynamoDB**: Read/write capacity, throttles
- **Bedrock**: Token usage, latency, errors

### Alarms
- **API 4XX Errors**: > 10 in 5 minutes
- **API 5XX Errors**: > 5 in 5 minutes
- **Lambda Errors**: > 10 in 5 minutes
- **Lambda Duration**: > 250 seconds
- **Cost Anomaly**: > $100 threshold

### Tracing (Future)
- **AWS X-Ray**: End-to-end request tracing
- **Service Map**: Visualize service dependencies
- **Latency Analysis**: Identify bottlenecks

---

## 9. Disaster Recovery

### Backup Strategy
- **DynamoDB**: Point-in-time recovery (35 days)
- **S3**: Versioning enabled, cross-region replication (future)
- **Lambda**: Code stored in S3 + version control

### Recovery Objectives
- **RTO**: 1 hour (redeployment time)
- **RPO**: 5 minutes (DynamoDB PITR)

### Recovery Procedures
1. Deploy infrastructure to new region (Terraform)
2. Restore DynamoDB from backup
3. Copy S3 data from backup region
4. Update DNS/API Gateway
5. Validate all 24 agents

---

## 10. Future Enhancements

### Short Term (Q1 2025)
- [ ] Step Functions for complex workflows
- [ ] X-Ray tracing integration
- [ ] Secrets Manager for credentials
- [ ] Custom domain for API Gateway
- [ ] Enhanced dashboard (React)

### Medium Term (Q2 2025)
- [ ] Multi-region deployment (DR)
- [ ] ElastiCache for caching
- [ ] RDS Aurora for analytics
- [ ] Cognito user pools
- [ ] API rate limiting per client

### Long Term (Q3-Q4 2025)
- [ ] Multi-cloud support (Azure, GCP)
- [ ] Mobile application
- [ ] Partner API marketplace
- [ ] White-label options
- [ ] Advanced AI model fine-tuning

---

## 11. Architecture Decision Records (ADRs)

### ADR-001: Serverless Architecture
**Decision**: Use 100% serverless (Lambda, API Gateway, DynamoDB)  
**Rationale**: Cost optimization, no idle costs, automatic scaling  
**Trade-offs**: Cold start latency, Lambda limits  
**Status**: Accepted

### ADR-002: HTTP API vs REST API
**Decision**: Use HTTP API Gateway (not REST)  
**Rationale**: 70% cost savings, sufficient features  
**Trade-offs**: Limited features (no usage plans)  
**Status**: Accepted

### ADR-003: Lambda Outside VPC
**Decision**: Deploy Lambda functions outside VPC  
**Rationale**: Faster cold starts, no NAT Gateway costs  
**Trade-offs**: No private network access  
**Status**: Accepted

### ADR-004: DynamoDB On-Demand
**Decision**: Use DynamoDB on-demand pricing  
**Rationale**: Variable workload, cost optimization  
**Trade-offs**: Slightly higher per-request cost  
**Status**: Accepted

### ADR-005: AWS Bedrock (Claude)
**Decision**: Use AWS Bedrock with Claude 3 Sonnet  
**Rationale**: Best-in-class AI, AWS integration, security  
**Trade-offs**: Vendor lock-in, cost  
**Status**: Accepted

---

## 12. References

### AWS Documentation
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [API Gateway HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
- [Bedrock User Guide](https://docs.aws.amazon.com/bedrock/)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)

### Internal Documentation
- [PROJECT_STATUS.md](../PROJECT_STATUS.md) - Current project status
- [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) - Deployment instructions
- [WARP.md](../../WARP.md) - Development guide

---

**Document Owner**: Nagarro Cloud Engineering Team  
**Last Review**: 2025-01-15  
**Next Review**: 2025-02-15  
**Version**: 2.0
