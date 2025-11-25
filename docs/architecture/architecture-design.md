# Nagarro Agentic Services Platform
## Architecture Design Document

### Document Information
- **Version:** 1.0
- **Date:** 2024-11-01
- **Status:** Draft
- **Authors:** Nagarro Architecture Team
- **Reviewers:** AWS Solutions Architecture Team

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [System Context](#2-system-context)
3. [Architecture Decisions](#3-architecture-decisions)
4. [Component Design](#4-component-design)
5. [Data Architecture](#5-data-architecture)
6. [Security Design](#6-security-design)
7. [Integration Design](#7-integration-design)
8. [Deployment Architecture](#8-deployment-architecture)

---

## 1. Introduction

### 1.1 Purpose
This document describes the detailed architecture design for the Nagarro Agentic Services Platform, including component specifications, interfaces, data models, and design decisions.

### 1.2 Scope
The platform provides AI-powered cloud migration planning and execution capabilities for enterprise customers migrating to AWS.

**Deployment Details:**
- **Primary Region:** eu-central-1 (Frankfurt)
- **VPC CIDR:** 10.0.0.0/16
- **Availability Zones:** 2 AZs (eu-central-1a, eu-central-1b)
- **AI Agents:** 6 specialized agents for complete migration lifecycle

### 1.3 Audience
- Solution Architects
- Software Engineers
- DevOps Engineers
- Security Engineers
- AWS Solutions Architects

### 1.4 References
- AWS Well-Architected Framework
- AWS FTR Guidelines
- ISO 27001 Standards
- GDPR Compliance Requirements

---

## 2. System Context

### 2.1 System Context Diagram

```
                    ┌─────────────────────────────────┐
                    │                                 │
                    │   Enterprise Customer           │
                    │   (On-Premises Infrastructure)  │
                    │                                 │
                    └────────────┬────────────────────┘
                                 │
                    ┏━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━━┓
                    ┃   VPN / Direct Connect          ┃
                    ┗━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━┛
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
    ┌────▼─────┐          ┌─────▼──────┐         ┌─────▼──────┐
    │ vCenter  │          │   CMDB     │         │  Network   │
    │  API     │          │   APIs     │         │  Discovery │
    └────┬─────┘          └─────┬──────┘         └─────┬──────┘
         │                      │                       │
         └──────────────────────┼───────────────────────┘
                                │
                    ┏━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━━━━━━━━┓
                    ┃  Nagarro Agentic Services           ┃
                    ┃  Platform (AWS eu-central-1)        ┃
                    ┃  VPC: 10.0.0.0/16                   ┃
                    ┃                                     ┃
                    ┃  ┌───────────────────────────────┐ ┃
                    ┃  │  AI Agent Orchestrator        │ ┃
                    ┃  │  (6 Specialized Agents)       │ ┃
                    ┃  └───────────────────────────────┘ ┃
                    ┃                                     ┃
                    ┃  ┌───────────────────────────────┐ ┃
                    ┃  │  AWS Bedrock (Claude 3)       │ ┃
                    ┃  └───────────────────────────────┘ ┃
                    ┃                                     ┃
                    ┗━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━━━━┛
                                │
                    ┌───────────┴───────────┐
                    │                       │
              ┌─────▼──────┐         ┌─────▼──────┐
              │ Web Console│         │   CLI      │
              │  (React)   │         │   Tools    │
              └────────────┘         └────────────┘
```

### 2.2 User Roles

**Platform Administrators**
- System configuration and management
- User access control
- Monitoring and troubleshooting

**Migration Architects**
- Configure discovery scans
- Review dependency mappings
- Approve migration waves
- Generate artifacts

**Business Stakeholders**
- View executive dashboards
- Review cost projections
- Track migration progress

**Developers/Engineers**
- API integration
- Custom script development
- Automated workflows

---

## 3. Architecture Decisions

### 3.1 ADR-001: Use AWS Bedrock for AI Capabilities

**Status:** Accepted

**Context:**
Need to integrate advanced AI capabilities for analysis, planning, and artifact generation.

**Decision:**
Use AWS Bedrock with Anthropic Claude models.

**Rationale:**
- Native AWS integration
- No infrastructure management
- Enterprise-grade security and compliance
- Pay-per-use pricing
- Multi-modal capabilities
- Regular model updates

**Consequences:**
- Positive: Faster time to market, lower operational overhead
- Negative: Vendor lock-in, limited model customization

### 3.2 ADR-002: Use DynamoDB for Metadata Storage

**Status:** Accepted

**Context:**
Need scalable, low-latency storage for operational metadata.

**Decision:**
Use DynamoDB with on-demand capacity mode.

**Rationale:**
- Serverless and fully managed
- Single-digit millisecond latency
- Automatic scaling
- Global tables for multi-region
- Native AWS service integration

**Consequences:**
- Positive: High performance, no capacity planning
- Negative: Query limitations, eventual consistency

### 3.3 ADR-003: Use ECS Fargate for Agent Hosting

**Status:** Accepted

**Context:**
Need to run long-running agent processes with isolation and scalability.

**Decision:**
Use ECS Fargate with containerized agents.

**Rationale:**
- No server management
- Container isolation
- Auto-scaling capabilities
- Integration with AWS services
- Cost-effective for variable workloads

**Consequences:**
- Positive: Operational simplicity, automatic scaling
- Negative: Cold start times, higher cost than EC2 for steady workloads

### 3.4 ADR-004: Event-Driven Architecture with EventBridge

**Status:** Accepted

**Context:**
Need loose coupling between components and asynchronous processing.

**Decision:**
Use EventBridge as the central event bus.

**Rationale:**
- Decoupled architecture
- Easy to add new consumers
- Built-in retry and error handling
- Integration with 90+ AWS services
- Schema registry

**Consequences:**
- Positive: Flexibility, scalability, maintainability
- Negative: Debugging complexity, eventual consistency

### 3.5 ADR-005: Multi-Tenant Architecture

**Status:** Accepted

**Context:**
Need to support multiple customers on the same platform.

**Decision:**
Use a pool model with tenant isolation at the application layer.

**Rationale:**
- Cost-effective resource sharing
- Simplified operations
- Faster onboarding
- Resource optimization

**Consequences:**
- Positive: Lower cost per tenant, easier updates
- Negative: Noisy neighbor risk, complex isolation logic

---

## 4. Component Design

### 4.1 API Gateway Layer

#### 4.1.1 REST API Design

**Base URL:** `https://api.nagarro-agentic.com/v1`

**Authentication:** API Key + IAM Signature (SigV4)

**Key Endpoints:**

```
POST   /projects                      # Create new project
GET    /projects/{id}                 # Get project details
GET    /projects/{id}/assets          # List assets
POST   /projects/{id}/discovery       # Start discovery
GET    /projects/{id}/dependencies    # Get dependency graph
POST   /projects/{id}/analyze         # Start analysis
GET    /projects/{id}/waves           # Get migration waves
POST   /projects/{id}/artifacts       # Generate artifact
GET    /artifacts/{id}                # Download artifact
```

**Request/Response Format:**

```json
// POST /projects
Request:
{
  "name": "Acme Corp Migration",
  "description": "Q1 2025 AWS Migration",
  "environment": {
    "type": "on-premises",
    "discovery_methods": ["vcenter", "cmdb"]
  }
}

Response:
{
  "project_id": "proj_abc123",
  "name": "Acme Corp Migration",
  "status": "active",
  "created_at": "2024-11-01T12:00:00Z",
  "discovery_endpoints": {
    "vcenter": "https://discovery.nagarro-agentic.com/vcenter"
  }
}
```

#### 4.1.2 WebSocket API Design

**Purpose:** Real-time updates for discovery progress, analysis status

**Endpoint:** `wss://ws.nagarro-agentic.com`

**Message Format:**

```json
{
  "event_type": "discovery.progress",
  "project_id": "proj_abc123",
  "timestamp": "2024-11-01T12:00:00Z",
  "data": {
    "servers_discovered": 45,
    "total_estimated": 150,
    "progress_percentage": 30
  }
}
```

### 4.2 Agent Architecture

#### 4.2.1 Base Agent Class

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import boto3

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.dynamodb = boto3.resource('dynamodb')
        self.s3 = boto3.client('s3')
        self.bedrock = boto3.client('bedrock-runtime')
        self.events = boto3.client('events')
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task"""
        pass
    
    async def save_state(self, state: Dict[str, Any]):
        """Persist agent state to DynamoDB"""
        table = self.dynamodb.Table('AgentStates')
        table.put_item(Item={
            'agent_id': self.agent_id,
            'state': state,
            'updated_at': datetime.utcnow().isoformat()
        })
    
    async def emit_event(self, event_type: str, detail: Dict[str, Any]):
        """Emit event to EventBridge"""
        self.events.put_events(
            Entries=[{
                'Source': f'agent.{self.__class__.__name__}',
                'DetailType': event_type,
                'Detail': json.dumps(detail)
            }]
        )
```

#### 4.2.2 Discovery Agent

```python
class DiscoveryAgent(BaseAgent):
    """Agent for infrastructure discovery"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        project_id = task['project_id']
        discovery_config = task['config']
        
        # Connect to customer infrastructure
        discovered_assets = await self.discover_infrastructure(
            discovery_config
        )
        
        # Store raw data in S3
        await self.store_discovery_data(project_id, discovered_assets)
        
        # Store metadata in DynamoDB
        await self.store_asset_metadata(project_id, discovered_assets)
        
        # Emit completion event
        await self.emit_event('discovery.completed', {
            'project_id': project_id,
            'asset_count': len(discovered_assets)
        })
        
        return {
            'status': 'success',
            'assets_discovered': len(discovered_assets)
        }
    
    async def discover_infrastructure(
        self, 
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Discover infrastructure based on config"""
        # Implementation for vCenter, AWS, CMDB, etc.
        pass
```

#### 4.2.3 Analysis Agent

```python
class AnalysisAgent(BaseAgent):
    """Agent for dependency analysis and risk assessment"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        project_id = task['project_id']
        
        # Retrieve discovery data
        assets = await self.get_project_assets(project_id)
        
        # Analyze with Claude
        analysis_results = await self.analyze_with_bedrock(assets)
        
        # Build dependency graph
        dependency_graph = await self.build_dependency_graph(
            analysis_results
        )
        
        # Calculate risk scores
        risk_scores = await self.calculate_risk_scores(
            assets, 
            dependency_graph
        )
        
        # Store results
        await self.store_analysis_results(
            project_id, 
            analysis_results,
            dependency_graph,
            risk_scores
        )
        
        # Emit event
        await self.emit_event('analysis.completed', {
            'project_id': project_id
        })
        
        return {'status': 'success'}
    
    async def analyze_with_bedrock(
        self, 
        assets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use Claude for intelligent analysis"""
        prompt = self.build_analysis_prompt(assets)
        
        response = self.bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 10000,
                'messages': [{
                    'role': 'user',
                    'content': prompt
                }]
            })
        )
        
        return json.loads(response['body'].read())
```

#### 4.2.4 Planning Agent

```python
class PlanningAgent(BaseAgent):
    """Agent for migration wave planning"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        project_id = task['project_id']
        
        # Get analysis results
        analysis = await self.get_analysis_results(project_id)
        
        # Generate wave plan with Claude
        wave_plan = await self.generate_wave_plan(analysis)
        
        # Optimize wave plan
        optimized_plan = await self.optimize_waves(wave_plan)
        
        # Store wave plan
        await self.store_wave_plan(project_id, optimized_plan)
        
        # Emit event
        await self.emit_event('planning.completed', {
            'project_id': project_id,
            'wave_count': len(optimized_plan['waves'])
        })
        
        return {'status': 'success'}
```

#### 4.2.5 Artifact Generation Agent

```python
class ArtifactGenerationAgent(BaseAgent):
    """Agent for generating migration artifacts"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        artifact_type = task['artifact_type']
        project_id = task['project_id']
        
        # Get project data
        project_data = await self.get_project_data(project_id)
        
        # Generate artifact based on type
        if artifact_type == 'executive_summary':
            artifact = await self.generate_executive_summary(
                project_data
            )
        elif artifact_type == 'technical_design':
            artifact = await self.generate_technical_design(
                project_data
            )
        elif artifact_type == 'wave_plan':
            artifact = await self.generate_wave_plan_doc(
                project_data
            )
        
        # Store artifact in S3
        artifact_url = await self.store_artifact(
            project_id, 
            artifact_type, 
            artifact
        )
        
        return {
            'status': 'success',
            'artifact_url': artifact_url
        }
```

#### 4.2.6 Architecture Agent

```python
class ArchitectureAgent(BaseAgent):
    """Agent for target architecture design"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        project_id = task['project_id']
        
        # Get analysis and planning results
        analysis = await self.get_analysis_results(project_id)
        wave_plan = await self.get_wave_plan(project_id)
        
        # Design target architecture with Claude
        target_architecture = await self.design_target_architecture(
            analysis, 
            wave_plan
        )
        
        # Validate against Well-Architected Framework
        wa_validation = await self.validate_well_architected(
            target_architecture
        )
        
        # Generate service sizing recommendations
        sizing = await self.calculate_service_sizing(analysis)
        
        # Design network topology
        network_design = await self.design_network_topology(
            target_architecture
        )
        
        # Store architecture design
        await self.store_architecture_design(
            project_id,
            target_architecture,
            wa_validation,
            sizing,
            network_design
        )
        
        # Emit event
        await self.emit_event('architecture.completed', {
            'project_id': project_id
        })
        
        return {'status': 'success'}
    
    async def design_target_architecture(
        self,
        analysis: Dict[str, Any],
        wave_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use Claude to design target architecture"""
        prompt = f"""
        Based on the following analysis and wave plan, design an optimal 
        AWS target architecture following Well-Architected Framework:
        
        Analysis: {json.dumps(analysis, indent=2)}
        Wave Plan: {json.dumps(wave_plan, indent=2)}
        
        Provide:
        1. AWS service recommendations
        2. Architecture patterns
        3. Security design
        4. Network topology
        5. Data flow diagrams
        """
        
        response = self.bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 15000,
                'messages': [{
                    'role': 'user',
                    'content': prompt
                }]
            })
        )
        
        return json.loads(response['body'].read())
```

#### 4.2.7 Testing Agent

```python
class TestingAgent(BaseAgent):
    """Agent for automated testing and validation"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        project_id = task['project_id']
        test_type = task['test_type']  # pre-migration, post-migration, rollback
        
        # Get target architecture and assets
        architecture = await self.get_architecture_design(project_id)
        assets = await self.get_project_assets(project_id)
        
        test_results = {}
        
        if test_type == 'pre-migration':
            test_results = await self.run_pre_migration_tests(
                assets, 
                architecture
            )
        elif test_type == 'post-migration':
            test_results = await self.run_post_migration_tests(
                assets,
                architecture
            )
        elif test_type == 'rollback':
            test_results = await self.run_rollback_tests(
                assets,
                architecture
            )
        
        # Store test results
        await self.store_test_results(
            project_id,
            test_type,
            test_results
        )
        
        # Emit event
        await self.emit_event('testing.completed', {
            'project_id': project_id,
            'test_type': test_type,
            'success_rate': test_results['success_rate']
        })
        
        return {
            'status': 'success',
            'test_results': test_results
        }
    
    async def run_pre_migration_tests(
        self,
        assets: List[Dict[str, Any]],
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run pre-migration validation tests"""
        tests = [
            self.validate_connectivity(),
            self.check_resource_availability(),
            self.validate_permissions(),
            self.check_compliance_requirements(),
            self.verify_backup_status(),
        ]
        
        results = await asyncio.gather(*tests)
        
        return {
            'total_tests': len(tests),
            'passed': sum(1 for r in results if r['status'] == 'pass'),
            'failed': sum(1 for r in results if r['status'] == 'fail'),
            'success_rate': sum(1 for r in results if r['status'] == 'pass') / len(tests),
            'details': results
        }
    
    async def run_post_migration_tests(
        self,
        assets: List[Dict[str, Any]],
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run post-migration validation and performance tests"""
        tests = [
            self.verify_application_functionality(),
            self.run_performance_benchmarks(),
            self.validate_data_integrity(),
            self.check_security_configuration(),
            self.verify_monitoring_setup(),
        ]
        
        results = await asyncio.gather(*tests)
        
        return {
            'total_tests': len(tests),
            'passed': sum(1 for r in results if r['status'] == 'pass'),
            'failed': sum(1 for r in results if r['status'] == 'fail'),
            'success_rate': sum(1 for r in results if r['status'] == 'pass') / len(tests),
            'details': results
        }
```

### 4.3 Agent Orchestrator

```python
class AgentOrchestrator:
    """Orchestrates agent execution"""
    
    def __init__(self):
        self.ecs = boto3.client('ecs')
        self.dynamodb = boto3.resource('dynamodb')
        self.agents = {
            'discovery': DiscoveryAgent,
            'analysis': AnalysisAgent,
            'planning': PlanningAgent,
            'artifact': ArtifactGenerationAgent,
            'architecture': ArchitectureAgent,
            'testing': TestingAgent
        }
    
    async def dispatch_task(
        self, 
        agent_type: str, 
        task: Dict[str, Any]
    ) -> str:
        """Dispatch task to appropriate agent"""
        
        # Create task record
        task_id = str(uuid.uuid4())
        await self.create_task_record(task_id, agent_type, task)
        
        # Launch agent container
        await self.launch_agent_container(agent_type, task_id, task)
        
        return task_id
    
    async def launch_agent_container(
        self, 
        agent_type: str, 
        task_id: str,
        task: Dict[str, Any]
    ):
        """Launch ECS Fargate task for agent"""
        
        response = self.ecs.run_task(
            cluster='agentic-services-cluster',
            launchType='FARGATE',
            taskDefinition=f'agent-{agent_type}',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': ['subnet-xxx'],
                    'securityGroups': ['sg-xxx'],
                    'assignPublicIp': 'DISABLED'
                }
            },
            overrides={
                'containerOverrides': [{
                    'name': f'{agent_type}-agent',
                    'environment': [
                        {'name': 'TASK_ID', 'value': task_id},
                        {'name': 'TASK_DATA', 'value': json.dumps(task)}
                    ]
                }]
            }
        )
        
        return response['tasks'][0]['taskArn']
```

---

## 5. Data Architecture

### 5.1 DynamoDB Schema

#### 5.1.1 Projects Table

```
Table: Projects
Partition Key: project_id (String)

Attributes:
- project_id: String (UUID)
- name: String
- description: String
- customer_id: String (GSI partition key)
- status: String (active|completed|archived)
- created_at: String (ISO 8601)
- updated_at: String (ISO 8601)
- config: Map
- metadata: Map

GSI: CustomerIndex
- Partition Key: customer_id
- Sort Key: created_at
```

#### 5.1.2 Assets Table

```
Table: Assets
Partition Key: project_id (String)
Sort Key: asset_id (String)

Attributes:
- project_id: String
- asset_id: String (UUID)
- asset_type: String (server|database|application|network)
- name: String
- properties: Map
- discovered_at: String
- risk_score: Number
- migration_wave: Number

GSI: AssetTypeIndex
- Partition Key: project_id
- Sort Key: asset_type
```

#### 5.1.3 Dependencies Table

```
Table: Dependencies
Partition Key: project_id (String)
Sort Key: dependency_id (String)

Attributes:
- project_id: String
- dependency_id: String (UUID)
- source_asset_id: String
- target_asset_id: String
- dependency_type: String (network|application|data)
- confidence_score: Number
- discovered_method: String
```

#### 5.1.4 MigrationWaves Table

```
Table: MigrationWaves
Partition Key: project_id (String)
Sort Key: wave_number (Number)

Attributes:
- project_id: String
- wave_number: Number
- name: String
- description: String
- asset_ids: List<String>
- start_date: String
- end_date: String
- status: String
- dependencies: List<String>
```

### 5.2 S3 Bucket Structure

```
s3://nagarro-agentic-discovery-{env}/
  ├── {project_id}/
  │   ├── raw/
  │   │   ├── vcenter_export_{timestamp}.json
  │   │   ├── cmdb_export_{timestamp}.json
  │   │   └── network_scan_{timestamp}.json
  │   └── processed/
  │       ├── assets_{timestamp}.parquet
  │       └── dependencies_{timestamp}.parquet

s3://nagarro-agentic-artifacts-{env}/
  ├── {project_id}/
  │   ├── executive-summary/
  │   │   └── executive_summary_{version}.pptx
  │   ├── technical-design/
  │   │   └── technical_design_{version}.pdf
  │   └── wave-plans/
  │       └── wave_plan_{version}.xlsx

s3://nagarro-agentic-logs-{env}/
  ├── application-logs/
  │   └── {yyyy}/{mm}/{dd}/
  ├── agent-logs/
  │   └── {agent_type}/{task_id}/
  └── audit-logs/
      └── {yyyy}/{mm}/{dd}/
```

### 5.3 RDS Schema (Analytics Database)

```sql
-- Projects fact table
CREATE TABLE fact_projects (
    project_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    total_assets INT,
    total_dependencies INT,
    estimated_cost DECIMAL(15,2),
    actual_cost DECIMAL(15,2),
    status VARCHAR(50)
);

-- Assets dimension
CREATE TABLE dim_assets (
    asset_id UUID PRIMARY KEY,
    project_id UUID REFERENCES fact_projects(project_id),
    asset_type VARCHAR(50),
    name VARCHAR(255),
    risk_score DECIMAL(5,2),
    migration_wave INT,
    migrated_at TIMESTAMP
);

-- Time dimension
CREATE TABLE dim_time (
    date_id INT PRIMARY KEY,
    date DATE,
    year INT,
    quarter INT,
    month INT,
    week INT,
    day_of_week INT
);

-- Customer dimension
CREATE TABLE dim_customer (
    customer_id UUID PRIMARY KEY,
    name VARCHAR(255),
    industry VARCHAR(100),
    region VARCHAR(100),
    tier VARCHAR(50)
);
```

---

## 6. Security Design

### 6.1 Network Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                ┌───────▼────────┐
                │  Route 53      │
                │  CloudFront    │
                │  WAF           │
                └───────┬────────┘
                        │
            ┌───────────▼────────────┐
            │   ALB (Public Subnet)  │
            └───────────┬────────────┘
                        │
        ┌───────────────┴────────────────┐
        │                                 │
┌───────▼────────┐              ┌────────▼────────┐
│ ECS Fargate    │              │ API Gateway     │
│ (Private)      │              │ (Private VPC    │
│                │              │  Endpoint)      │
└───────┬────────┘              └────────┬────────┘
        │                                 │
        └─────────────┬───────────────────┘
                      │
          ┌───────────▼──────────────┐
          │  DynamoDB VPC Endpoint   │
          │  S3 VPC Endpoint         │
          │  Secrets Manager         │
          └───────────┬──────────────┘
                      │
              ┌───────▼────────┐
              │ RDS (Isolated  │
              │  Subnet)       │
              └────────────────┘
```

### 6.2 IAM Roles and Policies

#### 6.2.1 Agent Execution Role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:UpdateItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/Projects",
        "arn:aws:dynamodb:*:*:table/Assets",
        "arn:aws:dynamodb:*:*:table/Dependencies"
      ],
      "Condition": {
        "StringEquals": {
          "dynamodb:LeadingKeys": ["${aws:PrincipalTag/project_id}"]
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::nagarro-agentic-discovery-*/${project_id}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "events:PutEvents"
      ],
      "Resource": [
        "arn:aws:events:*:*:event-bus/agentic-services-event-bus"
      ]
    }
  ]
}
```

### 6.3 Data Encryption

**At Rest:**
- DynamoDB: AWS-managed KMS key
- S3: SSE-KMS with customer-managed key
- RDS: Encryption with customer-managed KMS key
- EBS volumes: Encrypted with customer-managed key

**In Transit:**
- TLS 1.3 for all HTTPS communications
- VPC endpoints for AWS service traffic
- VPN/Direct Connect with IPsec encryption

### 6.4 Secrets Management

```python
import boto3
from botocore.exceptions import ClientError

class SecretsManager:
    """Centralized secrets management"""
    
    def __init__(self):
        self.client = boto3.client('secretsmanager')
        self.cache = {}
    
    def get_secret(self, secret_name: str) -> dict:
        """Retrieve secret with caching"""
        
        if secret_name in self.cache:
            return self.cache[secret_name]
        
        try:
            response = self.client.get_secret_value(
                SecretId=secret_name
            )
            secret = json.loads(response['SecretString'])
            self.cache[secret_name] = secret
            return secret
        except ClientError as e:
            raise Exception(f"Failed to retrieve secret: {e}")
```

---

## 7. Integration Design

### 7.1 Customer Infrastructure Integration

#### 7.1.1 vCenter Integration

```python
from pyVim.connect import SmartConnect
import ssl

class VCenterDiscovery:
    """VMware vCenter discovery integration"""
    
    def __init__(self, host: str, credentials: dict):
        self.host = host
        self.credentials = credentials
        self.connection = None
    
    async def connect(self):
        """Establish connection to vCenter"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_REQUIRED
        
        self.connection = SmartConnect(
            host=self.host,
            user=self.credentials['username'],
            pwd=self.credentials['password'],
            sslContext=context
        )
    
    async def discover_vms(self) -> List[Dict]:
        """Discover all VMs"""
        content = self.connection.RetrieveContent()
        container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.VirtualMachine], True
        )
        
        vms = []
        for vm in container.view:
            vm_data = {
                'name': vm.name,
                'cpu': vm.config.hardware.numCPU,
                'memory_mb': vm.config.hardware.memoryMB,
                'os': vm.config.guestFullName,
                'power_state': vm.runtime.powerState,
                'ip_addresses': [
                    ip.ipAddress for ip in vm.guest.net 
                    if hasattr(ip, 'ipAddress')
                ]
            }
            vms.append(vm_data)
        
        return vms
```

#### 7.1.2 CMDB Integration

```python
import requests

class CMDBIntegration:
    """Generic CMDB integration (ServiceNow, BMC, etc.)"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    async def get_configuration_items(
        self, 
        ci_class: str = 'cmdb_ci_server'
    ) -> List[Dict]:
        """Retrieve configuration items"""
        
        url = f'{self.base_url}/api/now/table/{ci_class}'
        params = {
            'sysparm_limit': 1000,
            'sysparm_fields': 'name,ip_address,os,cpu_count,ram'
        }
        
        response = requests.get(
            url, 
            headers=self.headers, 
            params=params
        )
        response.raise_for_status()
        
        return response.json()['result']
```

### 7.2 Bedrock Integration

```python
import boto3
import json

class BedrockClient:
    """AWS Bedrock integration wrapper"""
    
    def __init__(self):
        self.client = boto3.client('bedrock-runtime')
        self.model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
    
    async def analyze_dependencies(
        self, 
        assets: List[Dict]
    ) -> Dict:
        """Analyze asset dependencies using Claude"""
        
        prompt = self._build_dependency_prompt(assets)
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 10000,
                'messages': [{
                    'role': 'user',
                    'content': prompt
                }],
                'temperature': 0.3,
                'top_p': 0.9
            })
        )
        
        result = json.loads(response['body'].read())
        return self._parse_dependency_response(
            result['content'][0]['text']
        )
    
    def _build_dependency_prompt(
        self, 
        assets: List[Dict]
    ) -> str:
        """Build prompt for dependency analysis"""
        return f"""
        Analyze the following infrastructure assets and identify 
        dependencies between them. Consider:
        - Network connectivity patterns
        - Application communication flows
        - Database relationships
        - Shared services
        
        Assets:
        {json.dumps(assets, indent=2)}
        
        Respond with a JSON structure containing dependencies.
        """
```

---

## 8. Deployment Architecture

### 8.1 Multi-Region Architecture

```
Primary Region (us-east-1)           DR Region (eu-west-1)
┌──────────────────────────┐        ┌──────────────────────────┐
│                          │        │                          │
│  Application Tier        │        │  Application Tier        │
│  (ECS Fargate)           │◄──────►│  (ECS Fargate)           │
│                          │        │  (Standby)               │
└────────────┬─────────────┘        └────────────┬─────────────┘
             │                                    │
┌────────────▼─────────────┐        ┌────────────▼─────────────┐
│  DynamoDB Global Table   │◄──────►│  DynamoDB Global Table   │
│  (Active-Active)         │        │  (Active-Active)         │
└──────────────────────────┘        └──────────────────────────┘
             │                                    │
┌────────────▼─────────────┐        ┌────────────▼─────────────┐
│  S3 with CRR            │─────────►│  S3 Replica              │
│  (Cross-Region          │         │                          │
│   Replication)          │         │                          │
└──────────────────────────┘        └──────────────────────────┘
             │                                    │
┌────────────▼─────────────┐        ┌────────────▼─────────────┐
│  RDS Aurora Global       │◄──────►│  RDS Aurora Global       │
│  (Primary)               │        │  (Read Replica)          │
└──────────────────────────┘        └──────────────────────────┘
```

### 8.2 CI/CD Pipeline

```
GitHub Repository
       │
       ▼
┌─────────────────┐
│  GitHub Actions │
│  - Lint         │
│  - Test         │
│  - Build        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ECR            │
│  (Container     │
│   Registry)     │
└────────┬────────┘
         │
         ├───────────────┬──────────────┐
         │               │              │
         ▼               ▼              ▼
┌────────────┐   ┌──────────────┐  ┌─────────┐
│   Dev      │   │   Staging    │  │  Prod   │
│   (Auto)   │   │   (Auto)     │  │ (Manual)│
└────────────┘   └──────────────┘  └─────────┘
```

### 8.3 Terraform Structure

```
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       └── terraform.tfvars
├── modules/
│   ├── vpc/
│   ├── ecs-cluster/
│   ├── dynamodb/
│   ├── s3/
│   ├── rds/
│   ├── api-gateway/
│   └── monitoring/
└── shared/
    ├── iam-roles.tf
    ├── kms-keys.tf
    └── security-groups.tf
```

---

## 9. Appendices

### 9.1 Glossary

- **Agent:** Autonomous software component that performs specific tasks
- **Artifact:** Generated documentation or report
- **Dependency:** Relationship between infrastructure components
- **Discovery:** Process of scanning and cataloging infrastructure
- **Wave:** Group of applications migrated together

### 9.2 References

- AWS Well-Architected Framework: https://aws.amazon.com/architecture/well-architected/
- AWS Bedrock Documentation: https://docs.aws.amazon.com/bedrock/
- Claude AI Documentation: https://docs.anthropic.com/

---

**Document History:**

| Version | Date       | Author              | Changes           |
|---------|------------|---------------------|-------------------|
| 1.0     | 2025-11-01 | Architecture Team   | Initial draft     |

**Approval:**

| Role                 | Name | Date | Signature |
|----------------------|------|------|-----------|
| Lead Architect       |      |      |           |
| Security Architect   |      |      |           |
| AWS Solutions Arch   |      |      |           |
