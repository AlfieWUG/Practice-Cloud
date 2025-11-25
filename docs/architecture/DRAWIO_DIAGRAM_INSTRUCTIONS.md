# Draw.io Architecture Diagram - Update Instructions

**File**: `nagarro-agentic-platform-architecture.drawio`  
**Last Updated**: 2025-01-15  
**Purpose**: Visual architecture diagram for customer presentations  

---

## Overview

Create a comprehensive, professional architecture diagram showing the serverless, AI-powered Nagarro Agentic Services Platform with all 24 agents.

---

## Diagram Structure

### Layout: 6 Horizontal Layers (Top to Bottom)

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: PRESENTATION LAYER                                     │
├─────────────────────────────────────────────────────────────────┤
│ Layer 2: API GATEWAY LAYER                                      │
├─────────────────────────────────────────────────────────────────┤
│ Layer 3: COMPUTE LAYER (24 Lambda Functions)                    │
├─────────────────────────────────────────────────────────────────┤
│ Layer 4: AI & ORCHESTRATION LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│ Layer 5: DATA & STORAGE LAYER                                   │
├─────────────────────────────────────────────────────────────────┤
│ Layer 6: MONITORING & SECURITY LAYER                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: PRESENTATION LAYER

**Background Color**: Light Blue (#E8F4F8)  
**Components** (4 boxes, horizontal):

1. **Streamlit Dashboard**
   - Icon: 🖥️
   - Text: "Streamlit Dashboard\n3 Focus Areas\nAgent Overview"
   - Color: White box with blue border

2. **API Keys (Future)**
   - Icon: 🔑
   - Text: "API Key Management\n(Future Enhancement)"
   - Color: Light gray (future state)

3. **CloudWatch Dashboards**
   - Icon: 📊
   - Text: "CloudWatch Dashboards\nMetrics & Logs"
   - Color: Orange (AWS branding)

4. **CLI Tools**
   - Icon: ⌨️
   - Text: "Python CLI\nAutomation Scripts"
   - Color: White box with blue border

**Connections**: All 4 components connect down to API Gateway

---

## Layer 2: API GATEWAY LAYER

**Background Color**: Light Green (#E8F8F0)  
**Single Large Component**:

**HTTP API Gateway**
- Shape: Wide rectangle (spans full width)
- Icon: AWS API Gateway logo
- Text:
  ```
  HTTP API Gateway (Cost-Optimized)
  • 48+ Routes (2 per agent: POST execute, GET status)
  • Health: /health, List: /agents
  • CORS, Throttling (100 burst, 50/sec)
  • Optional: JWT Auth, Custom Domain, API Keys
  ```
- Color: AWS Green (#00A3A6)
- Label position: Top-left

**Connections**: 
- Input from Layer 1 (4 arrows down)
- Output to Layer 3 (fan out to 24 Lambda functions)

---

## Layer 3: COMPUTE LAYER (24 Lambda Functions)

**Background Color**: Light Purple (#F3E8F8)  
**Title**: "COMPUTE LAYER - 24 Lambda Functions (Python 3.11)"

**Organization**: 4 columns representing 4 phases

### Column 1: Discovery Phase (8 agents)
**Color**: Teal (#60c8b1)

1. infrastructure-scanner
2. application-profiler
3. data-discovery
4. integration-mapper
5. security-auditor
6. network-analyzer
7. performance-baseline
8. licensing-analyzer

### Column 2: Assessment Phase (5 agents)
**Color**: Blue (#3498db)

9. dependency-mapper
10. compliance-checker
11. cost-estimator
12. risk-assessment
13. capacity-planner

### Column 3: Execution Phase (6 agents)
**Color**: Green (#2ecc71)

14. infrastructure-provisioner
15. data-migration
16. application-migration
17. configuration
18. testing
19. rollback

### Column 4: Optimization Phase (5 agents)
**Color**: Red (#e74c3c)

20. performance-optimizer
21. cost-optimizer
22. security-hardening
23. monitoring-setup
24. documentation

**Each Agent Box**:
- Icon: λ (Lambda symbol)
- Shape: Rounded rectangle
- Size: Uniform (small, can fit 8 in column)
- Text: Agent name (one line)

**Below agents, show shared infrastructure**:
- "Shared Dependency Layer (boto3, anthropic, pydantic)"
- "Dead Letter Queue (SQS) for failures"
- "CloudWatch Logs (7-day retention)"
- "1GB memory, 300s timeout, 2 retries"

**Connections**: All 24 agents connect down to Layer 4

---

## Layer 4: AI & ORCHESTRATION LAYER

**Background Color**: Light Yellow (#FFF9E6)  
**Components** (3 boxes, horizontal):

1. **AWS Bedrock (Claude 3)**
   - Icon: AWS Bedrock logo + 🤖
   - Shape: Large rectangle (left side)
   - Text:
     ```
     AWS Bedrock
     Claude 3 Sonnet
     • All 24 agents powered by AI
     • 200K token context
     • Structured JSON output
     • System prompts per agent
     ```
   - Color: AWS Purple

2. **EventBridge Event Bus**
   - Icon: AWS EventBridge logo
   - Shape: Medium rectangle (center)
   - Text:
     ```
     EventBridge Event Bus
     • Agent coordination
     • Event routing
     • Async communication
     • Workflow orchestration
     ```
   - Color: AWS Purple

3. **Step Functions (Future)**
   - Icon: AWS Step Functions logo
   - Shape: Medium rectangle (right side)
   - Text:
     ```
     Step Functions (Future)
     • Complex workflows
     • Parallel execution
     • Error handling
     • Long-running processes
     ```
   - Color: Light gray (future state)

**Connections**: All 3 components connect down to Layer 5

---

## Layer 5: DATA & STORAGE LAYER

**Background Color**: Light Gray (#F5F5F5)  
**Components** (3 boxes, horizontal):

1. **DynamoDB (On-Demand)**
   - Icon: AWS DynamoDB logo
   - Shape: Large rectangle (left side)
   - Text:
     ```
     DynamoDB (3 Tables)
     • Agent State
     • Workflow State
     • Project Metadata
     • On-demand pricing
     • Point-in-time recovery
     ```
   - Color: AWS Blue

2. **S3 Buckets**
   - Icon: AWS S3 logo
   - Shape: Large rectangle (center)
   - Text:
     ```
     S3 Buckets (3)
     • Discovery Data
     • Generated Artifacts
     • System Logs
     • SSE-S3 encryption
     • Lifecycle policies
     ```
   - Color: AWS Orange

3. **CloudWatch Logs**
   - Icon: AWS CloudWatch logo
   - Shape: Medium rectangle (right side)
   - Text:
     ```
     CloudWatch Logs
     • Lambda execution logs
     • API Gateway logs
     • Bedrock invocation logs
     • 7-day retention (dev)
     ```
   - Color: AWS Orange

**Connections**: All 3 components connect down to Layer 6

---

## Layer 6: MONITORING & SECURITY LAYER

**Background Color**: Light Red (#FFE6E6)  
**Components** (3 boxes, horizontal):

1. **CloudWatch Alarms & SNS**
   - Icon: 🔔
   - Shape: Rectangle (left side)
   - Text:
     ```
     CloudWatch Alarms & SNS
     • 4XX/5XX error alerts
     • Lambda error alerts
     • Cost anomaly detection
     • SNS topic notifications
     ```
   - Color: AWS Orange

2. **IAM Roles & Policies**
   - Icon: 🔒
   - Shape: Rectangle (center)
   - Text:
     ```
     IAM Roles & Policies
     • Lambda execution role
     • Bedrock permissions
     • S3/DynamoDB access
     • Least privilege principle
     ```
   - Color: AWS Red

3. **Secrets Manager (Future)**
   - Icon: 🔐
   - Shape: Rectangle (right side)
   - Text:
     ```
     Secrets Manager (Future)
     • API keys
     • Database credentials
     • Third-party tokens
     • Automatic rotation
     ```
   - Color: Light gray (future state)

---

## Additional Elements

### Region Label
- **Position**: Top-right corner
- **Text**: "AWS Region: eu-central-1 (Frankfurt)"
- **Style**: Badge/label

### Deployment Model
- **Position**: Bottom-left corner
- **Text**: "100% Serverless Architecture\nNo VPC • No EC2 • No ECS"
- **Style**: Info box

### Key Statistics
- **Position**: Bottom-right corner
- **Text**:
  ```
  Platform Stats:
  • 24 AI Agents
  • 48+ API Endpoints
  • 3 DynamoDB Tables
  • 3 S3 Buckets
  • $40-70/month (dev)
  ```
- **Style**: Info box

### Connection Lines
- **API Gateway → Lambdas**: Fan-out with multiple arrows
- **Lambdas → Bedrock**: All 24 connect (can group visually)
- **Lambdas → EventBridge**: Event emissions
- **All layers**: Vertical flow top-to-bottom
- **Style**: Solid arrows, color-coded by layer

---

## Color Scheme

### Background Colors (by layer)
1. Presentation: Light Blue (#E8F4F8)
2. API Gateway: Light Green (#E8F8F0)
3. Compute: Light Purple (#F3E8F8)
4. AI/Orchestration: Light Yellow (#FFF9E6)
5. Data/Storage: Light Gray (#F5F5F5)
6. Monitoring/Security: Light Red (#FFE6E6)

### Component Colors
- **AWS Services**: Official AWS colors (orange, blue, purple, green)
- **Discovery Agents**: Teal (#60c8b1)
- **Assessment Agents**: Blue (#3498db)
- **Execution Agents**: Green (#2ecc71)
- **Optimization Agents**: Red (#e74c3c)
- **Future Features**: Light Gray (#D3D3D3)

### Text
- **Headers**: Bold, 16pt, Dark Gray (#333333)
- **Body Text**: Regular, 11pt, Dark Gray (#666666)
- **Labels**: Bold, 10pt, respective component color

---

## Draw.io Specific Tips

1. **Use AWS Architecture Icons**:
   - File → Import → Search "AWS" to import AWS icon library
   - Use official AWS service icons where possible

2. **Layering**:
   - Group related components per layer
   - Use containers/swimlanes for each layer background

3. **Alignment**:
   - Use Draw.io's alignment tools (Arrange → Align)
   - Ensure consistent spacing between components
   - All agent boxes should be same size

4. **Connection Routing**:
   - Use orthogonal connectors (right-angle lines)
   - Avoid line crossings where possible
   - Use connection points on boxes

5. **Export Options**:
   - Save as .drawio (editable format)
   - Export as PNG (high resolution, 300 DPI) for presentations
   - Export as SVG for scalable web use
   - Export as PDF for documents

---

## File Naming

- **Source File**: `nagarro-agentic-platform-architecture-v2.drawio`
- **PNG Export**: `nagarro-agentic-platform-architecture-v2.png`
- **SVG Export**: `nagarro-agentic-platform-architecture-v2.svg`
- **PDF Export**: `nagarro-agentic-platform-architecture-v2.pdf`

---

## Usage

### For Customer Presentations
- Use PNG export (high resolution)
- Include in PowerPoint/Google Slides
- Add animation to show layer-by-layer if needed

### For Documentation
- Use SVG export (scales well)
- Embed in markdown/HTML docs
- Link from README.md

### For Technical Reviews
- Share .drawio file
- Allow stakeholders to comment
- Version control in Git

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-15 | Initial instructions for v2 architecture (serverless) |

---

## Next Steps

1. Open `nagarro-agentic-platform-architecture.drawio` in Draw.io
2. Follow layer-by-layer instructions above
3. Use color scheme and AWS icons
4. Ensure all 24 agents are represented
5. Export to PNG, SVG, PDF
6. Update presentation materials

---

**Note**: The existing .drawio file may have an older architecture (ECS-based). Create new file as `nagarro-agentic-platform-architecture-v2.drawio` with the serverless architecture described above.
