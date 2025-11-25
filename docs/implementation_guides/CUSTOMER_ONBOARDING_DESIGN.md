# Customer Onboarding & Deployment System Design

**Document Version**: 1.0  
**Created**: 2025-01-15  
**Status**: Design Proposal  

---

## Executive Summary

Complete design for customer onboarding, deployment, and execution of the Agentic Services Platform. This system enables customers to self-service deploy the platform to their AWS accounts and manage migration projects through a web-based UI.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Deployment Models](#2-deployment-models)
3. [Onboarding Workflow](#3-onboarding-workflow)
4. [Customer UI Design](#4-customer-ui-design)
5. [Technical Implementation](#5-technical-implementation)
6. [Security & Compliance](#6-security--compliance)
7. [Implementation Roadmap](#7-implementation-roadmap)

---

## 1. Architecture Overview

### 1.1 Three-Tier Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│ TIER 1: Nagarro Control Plane (nagarro-agentic-services.com)    │
├──────────────────────────────────────────────────────────────────┤
│  • Onboarding Portal (React SPA)                                 │
│  • Customer Management API (FastAPI)                             │
│  • License & Billing System                                      │
│  • Deployment Orchestrator (AWS CDK)                             │
│  • Multi-Tenant Admin Dashboard                                  │
│  • Usage Analytics & Monitoring                                  │
│                                                                   │
│  Database: PostgreSQL RDS (customer metadata)                    │
│  Auth: Cognito + SSO (SAML, OAuth)                              │
│  Domain: app.nagarro-agentic.com                                 │
└──────────────────────────────────────────────────────────────────┘
                              ↓
                    Cross-Account IAM Role
                    (Customer grants Nagarro)
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ TIER 2: Customer AWS Account (Tenant Isolation)                 │
├──────────────────────────────────────────────────────────────────┤
│  • 24 Lambda Functions (deployed via StackSet)                   │
│  • API Gateway (customer-specific endpoint)                      │
│  • DynamoDB (customer's project data)                            │
│  • S3 (customer's discovery data & artifacts)                    │
│  • Bedrock (Claude - customer's quota)                           │
│  • CloudWatch (customer's logs)                                  │
│                                                                   │
│  Network: Optional VPC, Security Groups                          │
│  Tagging: customer_id, environment, cost_center                  │
│  Region: Customer choice (default eu-central-1)                  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
                    API Gateway Endpoints
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ TIER 3: Customer Portal (Subdomain per customer)                │
├──────────────────────────────────────────────────────────────────┤
│  • Project Dashboard (React + TypeScript)                        │
│  • Agent Execution UI (real-time status)                         │
│  • Results Viewer (artifacts, reports, diagrams)                 │
│  • User & Team Management                                        │
│  • Cost Tracking Dashboard                                       │
│                                                                   │
│  Domain: acme-corp.nagarro-agentic.com                          │
│  Auth: SSO integration (customer's IdP)                          │
│  Mobile: Responsive design, PWA support                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Deployment Models

### Model A: **SaaS Multi-Tenant** (Recommended for SMB)

**What**: All customers share Nagarro's AWS infrastructure

```
Nagarro AWS Account:
├─ 24 Lambda functions (shared)
├─ API Gateway (shared, tenant ID in path)
├─ DynamoDB (shared tables, tenant ID partition key)
└─ S3 (separate bucket per customer)

Pros:
✅ Fastest onboarding (< 5 minutes)
✅ No AWS account required from customer
✅ Lowest cost (shared infrastructure)
✅ Easiest to manage & update

Cons:
❌ Data residency concerns
❌ Shared resource limits
❌ Less customization
```

**Pricing**: Subscription-based ($2K-5K/month)

---

### Model B: **Single-Tenant Deployment** (Recommended for Enterprise)

**What**: Deploy full stack to customer's AWS account

```
Customer AWS Account:
├─ 24 Lambda functions (dedicated)
├─ API Gateway (dedicated)
├─ DynamoDB (dedicated tables)
├─ S3 (customer's buckets)
└─ VPC (optional, customer's network)

Pros:
✅ Full data control (stays in customer account)
✅ Custom configurations
✅ Dedicated resources
✅ Meet compliance requirements (HIPAA, PCI-DSS)

Cons:
❌ Longer onboarding (30-60 minutes)
❌ Requires AWS account & permissions
❌ Higher cost (customer pays AWS costs)
```

**Pricing**: License + AWS costs ($350K-525K project + $40-70/month platform)

---

### Model C: **Hybrid** (Best of Both)

**What**: Control plane in Nagarro account, execution in customer account

```
Nagarro Account:
├─ Customer portal UI
├─ License management
└─ Deployment orchestrator

Customer Account:
├─ 24 Lambda agents (execution)
└─ Customer data (storage)

Pros:
✅ UI managed by Nagarro (always latest)
✅ Customer data stays isolated
✅ Balance of control & convenience

Cons:
❌ More complex architecture
❌ Cross-account IAM setup
```

**Pricing**: Hybrid ($10K-20K setup + $1K-3K/month managed service)

---

## 3. Onboarding Workflow

### 3.1 Self-Service Onboarding (15-60 minutes)

```
Step 1: Account Creation (2 min)
├─ Customer visits: https://app.nagarro-agentic.com/signup
├─ Enter: Company name, email, phone
├─ Choose: Deployment model (SaaS vs Single-Tenant)
└─ Create account → Email verification

Step 2: Deployment Model Selection (1 min)
├─ SaaS Multi-Tenant: Click "Quick Start" → Done
└─ Single-Tenant: Proceed to AWS setup →

Step 3: AWS Account Configuration (10-15 min)
├─ Option A: Automated CloudFormation
│   ├─ Download StackSet template
│   ├─ Deploy to AWS account (1-click)
│   └─ Grant Nagarro cross-account role
│
└─ Option B: Manual Terraform
    ├─ Download Terraform config
    ├─ terraform init && terraform apply
    └─ Provide API endpoint back to portal

Step 4: Platform Configuration (5 min)
├─ Set AWS region preference
├─ Configure Bedrock model access
├─ Set up cost alerts & budgets
├─ Invite team members
└─ Configure SSO (optional)

Step 5: Validation & Testing (5 min)
├─ Run health checks (all 24 agents)
├─ Execute sample discovery agent
├─ Verify API connectivity
└─ Test report generation

Step 6: First Project Setup (5 min)
├─ Create first migration project
├─ Upload requirements document
├─ Run discovery agents
└─ View results

✅ ONBOARDING COMPLETE
Time: SaaS (5 min), Single-Tenant (30-60 min)
```

---

### 3.2 Onboarding UI (React Components)

**File Structure**:
```
src/onboarding/
├── components/
│   ├── StepIndicator.tsx          # Progress bar (6 steps)
│   ├── DeploymentModelSelector.tsx # SaaS vs Single-Tenant
│   ├── AWSAccountSetup.tsx        # CloudFormation wizard
│   ├── ConfigurationForm.tsx      # Platform settings
│   ├── ValidationChecklist.tsx    # Health checks
│   └── FirstProjectWizard.tsx     # Initial project
│
├── pages/
│   ├── SignupPage.tsx             # Step 1
│   ├── DeploymentPage.tsx         # Step 2-3
│   ├── ConfigurationPage.tsx      # Step 4
│   ├── ValidationPage.tsx         # Step 5
│   └── FirstProjectPage.tsx       # Step 6
│
└── hooks/
    ├── useOnboarding.ts           # Onboarding state machine
    ├── useAWSDeployment.ts        # Deploy to customer AWS
    └── useHealthCheck.ts          # Validate deployment
```

**Key Features**:
- **Auto-save progress**: Resume anytime
- **Real-time validation**: Immediate feedback
- **Help tooltips**: Contextual guidance
- **Video tutorials**: Embedded walkthrough
- **Live chat support**: Human help if stuck

---

## 4. Customer UI Design

### 4.1 Main Dashboard (Homepage After Login)

```
┌────────────────────────────────────────────────────────────────┐
│ Nagarro Agentic Services                  [User ▼] [Settings] │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Welcome back, John Doe (Acme Corp)               🔔 3 Alerts  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Active Projects (3)                            [+ New]    │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ 📊 E-Commerce Migration         Status: ⚙️ In Progress   │ │
│  │    Phase: Execution (Wave 3/6)   Progress: ████░░ 65%    │ │
│  │    Next: Deploy Wave 4 (Jan 20)  Cost: $45K / $520K      │ │
│  │    [View] [Execute] [Reports]                             │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ 📊 CRM System Upgrade           Status: ✅ Completed     │ │
│  │    Completed: Jan 10             Savings: 28% ($12K/mo)  │ │
│  │    [View Results] [Download]                              │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ 📊 Data Center Exit             Status: 📋 Planning      │ │
│  │    Phase: Assessment             Progress: ██░░░░ 35%    │ │
│  │    [Continue Setup]                                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │ Agent Activity (24) │  │ Cost This Month  │  │ Savings   │ │
│  ├─────────────────────┤  ├──────────────────┤  ├───────────┤ │
│  │ 🟢 Running: 3       │  │ $2,340           │  │ $18,500   │ │
│  │ ⏸️  Idle: 21        │  │ Budget: $5,000   │  │ vs Trad.  │ │
│  │ ⚠️  Issues: 0       │  │ ████░░░░ 47%     │  │ +28%      │ │
│  └─────────────────────┘  └──────────────────┘  └───────────┘ │
│                                                                 │
│  Quick Actions:                                                │
│  [🚀 Start New Migration] [📊 Run Discovery] [📈 View Analytics]│
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

### 4.2 Agent Execution Page (THE KEY UI)

```
┌────────────────────────────────────────────────────────────────┐
│ ← Back to Dashboard          E-Commerce Migration Project      │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔵 Discovery Phase (8 Agents)                    [Expand All] │
│  ├─ ✅ Infrastructure Scanner        Completed 2 hours ago     │
│  │   Results: 287 VMs, 52 databases                            │
│  │   [View Report] [Download JSON]                             │
│  ├─ ✅ Application Profiler          Completed 2 hours ago     │
│  ├─ ✅ Data Discovery                Completed 1 hour ago      │
│  ├─ ✅ Integration Mapper            Completed 1 hour ago      │
│  ├─ ✅ Security Auditor              Completed 1 hour ago      │
│  ├─ ✅ Network Analyzer              Completed 45 min ago      │
│  ├─ ✅ Performance Baseline          Completed 30 min ago      │
│  └─ ✅ Licensing Analyzer            Completed 20 min ago      │
│                                                                 │
│  🔵 Assessment Phase (5 Agents)       [▶️ Run All] [Run Each] │
│  ├─ 🟡 Dependency Mapper             Running... 35% ████░░░   │
│  │   Analyzing 287 applications...                             │
│  │   ETA: 15 minutes                 [View Live Log]           │
│  ├─ ⏸️ Compliance Checker            Queued (waiting)          │
│  ├─ ⏸️ Cost Estimator                Queued                    │
│  ├─ ⏸️ Risk Assessment               Queued                    │
│  └─ ⏸️ Capacity Planner              Queued                    │
│                                                                 │
│  ⚪ Execution Phase (6 Agents)        Not started              │
│  ⚪ Optimization Phase (5 Agents)     Not started              │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Agent Execution Controls                                │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │ [▶️ Run Next Phase] [⏸️ Pause All] [🔄 Retry Failed]   │   │
│  │ [📋 View Logs] [⚙️ Configure] [📥 Export Results]      │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Key Features**:
- **Real-time status**: WebSocket updates (agent progress)
- **One-click execution**: "Run All" or individual agents
- **Dependency awareness**: Auto-run dependent agents
- **Live logs**: Stream CloudWatch logs to UI
- **Error handling**: Retry, skip, or manual intervention

---

### 4.3 Agent Configuration Modal

```
┌─────────────────────────────────────────────────────────────┐
│ ⚙️ Configure: Infrastructure Scanner Agent                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Data Sources:                                                │
│ ☑ VMware vCenter                                            │
│   Server: vcenter.acme.com                                  │
│   Credentials: [Select from Vault ▼]                        │
│                                                              │
│ ☑ AWS Account (Cross-Account)                              │
│   Account ID: 123456789012                                  │
│   Role ARN: [Auto-detected ✅]                              │
│                                                              │
│ ☑ Azure Subscription                                        │
│   Subscription ID: abc-123-xyz                              │
│   [Connect Azure ▼]                                         │
│                                                              │
│ ☐ CMDB (ServiceNow, BMC)                                    │
│                                                              │
│ Scan Options:                                                │
│ ├─ Depth: ◉ Full  ○ Quick  ○ Custom                        │
│ ├─ Include: [✓] VMs [✓] Databases [✓] Storage              │
│ └─ Exclude: Tags matching: test-*, dev-*                    │
│                                                              │
│ Advanced:                                                    │
│ ├─ Timeout: 300 seconds [___]                               │
│ ├─ Retry Attempts: 2 [___]                                  │
│ └─ Parallel Scans: 5 [___]                                  │
│                                                              │
│          [Cancel]  [Save & Run Later]  [Save & Run Now]    │
└─────────────────────────────────────────────────────────────┘
```

---

### 4.4 Results Viewer

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Infrastructure Scanner Results                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Summary:                                                     │
│ ├─ VMs Discovered: 287                                      │
│ ├─ Databases: 52 (MySQL: 30, PostgreSQL: 15, Oracle: 7)    │
│ ├─ Storage: 45 TB                                           │
│ └─ Networks: 8 VLANs, 120 security groups                   │
│                                                              │
│ Visualizations:                                              │
│ [Tab: Overview] [Tab: Topology] [Tab: Dependencies]         │
│                                                              │
│ ┌───────────────────────────────────────────────────────┐  │
│ │   [Interactive Network Topology Diagram]              │  │
│ │   • Click nodes to see details                        │  │
│ │   • Zoom, pan, filter                                 │  │
│ │   • Export to PNG, SVG                                │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                              │
│ Generated Artifacts:                                         │
│ ├─ 📄 Infrastructure Inventory (Excel)    [Download]        │
│ ├─ 📄 Network Topology Diagram (Draw.io)  [Download]        │
│ ├─ 📄 Discovery Report (PDF)              [Download]        │
│ └─ 📄 Raw Data (JSON)                     [Download]        │
│                                                              │
│ AI Insights:                                                 │
│ 💡 "Found 12 Windows Server 2012 instances (EOL risk)"      │
│ 💡 "3 databases are over-provisioned (cost savings: $3K/mo)"│
│ 💡 "Network has 15 unused security groups (cleanup needed)" │
│                                                              │
│                          [Close]  [Share]  [Export All]     │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Technical Implementation

### 5.1 Backend Architecture (FastAPI)

**File Structure**:
```
backend/
├── main.py                        # FastAPI app
├── routers/
│   ├── onboarding.py              # POST /onboarding/start
│   ├── deployment.py              # POST /deployment/aws
│   ├── projects.py                # CRUD /projects
│   ├── agents.py                  # POST /agents/{name}/execute
│   └── results.py                 # GET /results/{task_id}
│
├── services/
│   ├── aws_deployer.py            # Deploy to customer AWS
│   ├── agent_executor.py          # Execute agent via API Gateway
│   ├── license_manager.py         # License validation
│   └── billing_service.py         # Usage tracking
│
├── models/
│   ├── customer.py                # Customer DB model
│   ├── project.py                 # Project DB model
│   └── agent_task.py              # Task execution tracking
│
└── integrations/
    ├── aws_stackset.py            # CloudFormation StackSet
    ├── terraform_wrapper.py       # Terraform execution
    └── cognito_sso.py             # Auth integration
```

**Key APIs**:
```python
# Onboarding
POST /api/v1/onboarding/start
{
  "company_name": "Acme Corp",
  "email": "john@acme.com",
  "deployment_model": "single_tenant"
}
→ Returns: { "customer_id": "uuid", "onboarding_token": "..." }

# Deploy to Customer AWS
POST /api/v1/deployment/aws
{
  "customer_id": "uuid",
  "aws_account_id": "123456789012",
  "region": "eu-central-1",
  "iam_role_arn": "arn:aws:iam::..."
}
→ Returns: { "deployment_id": "uuid", "status": "in_progress" }

# Create Project
POST /api/v1/projects
{
  "name": "E-Commerce Migration",
  "requirements": "Migrate 287 VMs...",
  "target_cloud": "aws"
}
→ Returns: { "project_id": "uuid" }

# Execute Agent
POST /api/v1/agents/infrastructure-scanner/execute
{
  "project_id": "uuid",
  "config": {
    "data_sources": ["vmware", "aws"],
    "scan_depth": "full"
  }
}
→ Returns: { "task_id": "uuid", "status": "running" }

# Get Results
GET /api/v1/results/{task_id}
→ Returns: { "status": "completed", "result": {...}, "artifacts": [...] }
```

---

### 5.2 Frontend Architecture (React + TypeScript)

**Tech Stack**:
- **Framework**: React 18 + TypeScript
- **UI Library**: Material-UI (MUI) or Ant Design
- **State**: Redux Toolkit + RTK Query
- **Routing**: React Router v6
- **Real-time**: Socket.IO (agent status updates)
- **Charts**: Recharts or Victory
- **Diagrams**: React Flow (topology visualizations)

**File Structure**:
```
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx          # Main dashboard
│   │   ├── ProjectDetail.tsx      # Agent execution page
│   │   ├── Onboarding.tsx         # Onboarding wizard
│   │   └── Results.tsx            # Results viewer
│   │
│   ├── components/
│   │   ├── AgentCard.tsx          # Agent status card
│   │   ├── PhaseAccordion.tsx     # Collapsible phase section
│   │   ├── ExecutionControls.tsx  # Play, pause, retry buttons
│   │   ├── LiveLog.tsx            # Real-time log viewer
│   │   └── ResultsViewer.tsx      # Artifact viewer
│   │
│   ├── hooks/
│   │   ├── useAgentExecution.ts   # Execute agent
│   │   ├── useRealtimeStatus.ts   # WebSocket status
│   │   └── useProjectState.ts     # Project state management
│   │
│   ├── services/
│   │   ├── api.ts                 # API client (axios)
│   │   └── websocket.ts           # WebSocket client
│   │
│   └── store/
│       ├── projectSlice.ts        # Redux slice for projects
│       └── agentSlice.ts          # Redux slice for agents
```

---

### 5.3 AWS Deployment Automation (Customer Account)

**CloudFormation StackSet Template**:
```yaml
# infrastructure/customer-deployment-stackset.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Nagarro Agentic Services Platform - Customer Deployment'

Parameters:
  CustomerID:
    Type: String
    Description: Unique customer identifier
  Environment:
    Type: String
    Default: production
    AllowedValues: [development, staging, production]

Resources:
  # Lambda Functions (24)
  InfrastructureScannerFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub 'agentic-infrastructure-scanner-${CustomerID}'
      Runtime: python3.11
      Handler: handler.infrastructure_scanner_handler
      Code:
        S3Bucket: nagarro-agentic-deployment
        S3Key: lambda/deployment.zip
      Environment:
        Variables:
          CUSTOMER_ID: !Ref CustomerID
          BEDROCK_MODEL: anthropic.claude-3-sonnet
      Tags:
        - Key: customer_id
          Value: !Ref CustomerID
  
  # API Gateway
  AgentsAPI:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: !Sub 'agentic-api-${CustomerID}'
      ProtocolType: HTTP
      CorsConfiguration:
        AllowOrigins: ['*']
  
  # DynamoDB Tables
  AgentStateTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub 'agentic-agent-state-${CustomerID}'
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: task_id
          AttributeType: S
      KeySchema:
        - AttributeName: task_id
          KeyType: HASH

Outputs:
  APIEndpoint:
    Value: !GetAtt AgentsAPI.ApiEndpoint
  CustomerID:
    Value: !Ref CustomerID
```

**Deployment Script** (in backend):
```python
# backend/services/aws_deployer.py
import boto3
from typing import Dict

class AWSDeployer:
    def __init__(self):
        self.cfn = boto3.client('cloudformation')
    
    def deploy_to_customer_account(
        self,
        customer_id: str,
        aws_account_id: str,
        iam_role_arn: str,
        region: str = 'eu-central-1'
    ) -> Dict:
        """Deploy platform to customer's AWS account"""
        
        # Assume role in customer account
        sts = boto3.client('sts')
        assumed_role = sts.assume_role(
            RoleArn=iam_role_arn,
            RoleSessionName=f'nagarro-agentic-deploy-{customer_id}'
        )
        
        # Create CloudFormation stack
        stack_name = f'nagarro-agentic-{customer_id}'
        response = self.cfn.create_stack(
            StackName=stack_name,
            TemplateURL='s3://nagarro-agentic-deployment/customer-stackset.yaml',
            Parameters=[
                {'ParameterKey': 'CustomerID', 'ParameterValue': customer_id},
                {'ParameterKey': 'Environment', 'ParameterValue': 'production'}
            ],
            Capabilities=['CAPABILITY_IAM'],
            Tags=[
                {'Key': 'customer_id', 'Value': customer_id},
                {'Key': 'managed_by', 'Value': 'nagarro'}
            ]
        )
        
        return {
            'deployment_id': response['StackId'],
            'status': 'in_progress',
            'estimated_time': '10-15 minutes'
        }
```

---

### 5.4 Real-Time Agent Status (WebSocket)

```python
# backend/websocket_handler.py
from fastapi import WebSocket
import asyncio

class AgentStatusStreamer:
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        self.active_connections.append((websocket, project_id))
    
    async def send_agent_status(self, project_id: str, agent_name: str, status: dict):
        """Stream agent status updates to connected clients"""
        for ws, pid in self.active_connections:
            if pid == project_id:
                await ws.send_json({
                    'type': 'agent_status',
                    'agent': agent_name,
                    'status': status['status'],
                    'progress': status.get('progress', 0),
                    'message': status.get('message', '')
                })

# Frontend hook
// hooks/useRealtimeStatus.ts
import { useEffect, useState } from 'react';
import io from 'socket.io-client';

export function useRealtimeStatus(projectId: string) {
  const [agentStatuses, setAgentStatuses] = useState({});
  
  useEffect(() => {
    const socket = io(`wss://api.nagarro-agentic.com/ws/${projectId}`);
    
    socket.on('agent_status', (data) => {
      setAgentStatuses(prev => ({
        ...prev,
        [data.agent]: data
      }));
    });
    
    return () => socket.disconnect();
  }, [projectId]);
  
  return agentStatuses;
}
```

---

## 6. Security & Compliance

### 6.1 Cross-Account IAM Role (Customer Setup)

**Customer creates this role** (via CloudFormation or Console):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::NAGARRO_ACCOUNT_ID:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "CUSTOMER_UNIQUE_ID"
        }
      }
    }
  ]
}
```

**Permissions** (least privilege):
- Lambda: CreateFunction, InvokeFunction, UpdateFunctionCode
- API Gateway: CreateApi, CreateRoute, CreateIntegration
- DynamoDB: CreateTable, Query, PutItem, GetItem
- S3: CreateBucket, PutObject, GetObject (customer's buckets)
- CloudWatch: CreateLogGroup, PutLogEvents

---

### 6.2 Data Isolation & Privacy

**Guarantees**:
1. ✅ Customer data never leaves customer's AWS account
2. ✅ Nagarro only accesses via API (no direct DB access)
3. ✅ All data encrypted at rest (AWS KMS)
4. ✅ All data encrypted in transit (TLS 1.3)
5. ✅ Customer can revoke access anytime (remove IAM role)

**Compliance**:
- GDPR: Data stays in customer-chosen region
- HIPAA: Customer uses BAA-eligible AWS services
- SOC 2: Nagarro's control plane audited
- ISO 27001: AWS infrastructure compliant

---

## 7. Implementation Roadmap

### Phase 1: MVP (4-6 weeks)

**Week 1-2: Backend API**
- [ ] FastAPI setup with auth (Cognito)
- [ ] Customer onboarding API
- [ ] Project CRUD API
- [ ] Agent execution API (proxy to customer API Gateway)

**Week 3-4: Frontend**
- [ ] React app scaffold
- [ ] Dashboard page
- [ ] Agent execution page
- [ ] Results viewer

**Week 5: Deployment Automation**
- [ ] CloudFormation StackSet template
- [ ] Deployment orchestrator
- [ ] Health check validation

**Week 6: Testing & Polish**
- [ ] End-to-end testing
- [ ] UI/UX refinement
- [ ] Documentation

**MVP Deliverables**:
- ✅ Working onboarding flow (SaaS model)
- ✅ Dashboard to view projects
- ✅ Execute agents from UI
- ✅ View results

---

### Phase 2: Enterprise Features (2-3 months)

- [ ] Single-tenant deployment (customer AWS)
- [ ] SSO integration (SAML, OAuth)
- [ ] Multi-user & RBAC
- [ ] Advanced results visualization
- [ ] Mobile-responsive design
- [ ] White-label support

---

### Phase 3: Advanced Capabilities (3-6 months)

- [ ] Multi-cloud support (Azure, GCP)
- [ ] Workflow orchestration (Step Functions UI)
- [ ] AI-powered recommendations
- [ ] Cost optimization dashboard
- [ ] Partner marketplace

---

## 8. Cost Estimate

### Development Costs

| Component | Effort | Cost |
|-----------|--------|------|
| Backend API | 3 weeks | $30K |
| Frontend UI | 4 weeks | $40K |
| Deployment Automation | 2 weeks | $20K |
| Testing & QA | 1 week | $10K |
| **Total MVP** | **10 weeks** | **$100K** |

### Ongoing Costs (Monthly)

| Item | Cost |
|------|------|
| Control Plane AWS (hosting portal) | $500 |
| RDS (customer metadata) | $200 |
| CloudFront + S3 (static site) | $100 |
| **Total** | **$800/month** |

---

## 9. Success Metrics

### Onboarding
- **Time to First Agent**: < 30 minutes (from signup)
- **Onboarding Completion Rate**: > 85%
- **Time to First Project**: < 1 hour

### Usage
- **Active Users**: Track daily/weekly active users
- **Agents Executed**: Per project, per customer
- **Results Downloaded**: Track artifact downloads

### Business
- **Customer Acquisition Cost (CAC)**: < $5K
- **Customer Lifetime Value (LTV)**: > $200K
- **LTV/CAC Ratio**: > 40:1

---

## 10. Next Steps

### Immediate (This Week)
1. Review & approve this design
2. Set up development environment
3. Create project in GitHub/GitLab
4. Assign development team

### Short Term (Next Month)
1. Build backend API (FastAPI)
2. Build frontend UI (React)
3. Develop deployment automation
4. Internal testing with sample project

### Medium Term (Months 2-3)
1. Beta testing with 2-3 pilot customers
2. Iterate based on feedback
3. Production deployment
4. Launch to market

---

**Status**: Awaiting approval to proceed  
**Owner**: Engineering Team  
**Stakeholders**: Product, Sales, Engineering, Security
