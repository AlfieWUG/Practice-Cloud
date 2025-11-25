# 📘 Customer Onboarding Guide - Field Explanations

## Overview

The onboarding flow helps new customers set up their cloud migration projects and execute AI agents to automate the migration process.

---

## 🚀 Page 1: Customer Onboarding (Project Creation)

### Purpose
Capture essential information about the customer's cloud migration project before AI agents begin analysis.

---

### **Field 1: Project Name*** (Required)

**What it is:**  
A unique, descriptive name for this migration project.

**Why we need it:**  
- Identifies the project across the platform
- Appears in project lists and reports
- Used in all communications and artifacts

**Examples:**
- ✅ "E-Commerce Platform Migration to AWS"
- ✅ "CRM Modernization - Oracle to Salesforce"
- ✅ "Legacy Mainframe to Cloud-Native"
- ❌ "Project 1" (too generic)

**Tips for customers:**
- Use clear, business-relevant names
- Include source/target if helpful
- Keep it under 50 characters

---

### **Field 2: Description**

**What it is:**  
A brief, high-level overview of the migration project.

**Why we need it:**  
- Provides context for stakeholders
- Helps agents understand business objectives
- Used in executive summaries

**Examples:**
```
Migrate our customer-facing e-commerce platform from 
on-premises infrastructure to AWS cloud, enabling 
global scalability and reducing operational costs by 40%.
```

**What to include:**
- Current state (what exists today)
- Target state (what you want to achieve)
- Business drivers (why now)
- Key success metrics

**Tips:**
- 2-4 sentences is ideal
- Focus on business value, not technical details
- Mention key stakeholders if relevant

---

### **Field 3: Requirements & Goals**

**What it is:**  
Detailed technical and business requirements that define success.

**Why we need it:**  
- AI agents use this to guide their analysis
- Becomes the baseline for planning and execution
- Used to measure project success

**Examples:**
```
Technical Requirements:
• Migrate 100+ microservices (Java, Node.js)
• 5TB of product and customer data (PostgreSQL)
• Zero-downtime migration (max 5min maintenance window)
• Maintain sub-200ms API response times

Business Requirements:
• Maintain PCI-DSS compliance throughout
• Complete migration before Q4 peak season
• Reduce infrastructure costs by 35%
• Enable auto-scaling for traffic spikes

Constraints:
• Must integrate with existing payment gateway
• Legacy COBOL system to remain on-prem initially
• Budget cap at $750K
```

**What to include:**
- Application landscape (languages, frameworks)
- Data volumes and types
- Performance requirements
- Compliance/regulatory needs
- Integration points
- Timeline constraints
- Budget constraints
- Risk tolerance

**Tips:**
- Be specific with numbers (VMs, databases, users, data size)
- Use bullet points for clarity
- Include both technical AND business requirements
- Mention what's NOT in scope

---

### **Field 4: Timeline**

**What it is:**  
Expected duration from project start to production cutover.

**Why we need it:**  
- Determines urgency and resource allocation
- Influences which migration strategy agents recommend
- Affects pricing and team sizing

**Options Explained:**

| Timeline | When to Choose | What It Means |
|----------|---------------|---------------|
| **1-3 months** | • Small, simple migrations<br>• Lift-and-shift only<br>• <10 applications<br>• Urgent business need | • Fast-track approach<br>• Limited optimization<br>• Higher resource intensity<br>• More risk |
| **3-6 months** | • Medium complexity<br>• 10-50 applications<br>• Some modernization<br>• Normal business cadence | • **Most common choice**<br>• Balanced approach<br>• Time for testing<br>• Reasonable optimization |
| **6-12 months** | • Large enterprise migration<br>• 50+ applications<br>• Significant modernization<br>• Complex integrations | • Phased approach<br>• Deep optimization<br>• Lower risk<br>• More cost-effective |
| **12+ months** | • Massive transformation<br>• 100s of applications<br>• Complete re-architecture<br>• Multi-cloud strategy | • Strategic program<br>• Wave-based migration<br>• Extensive optimization<br>• Organizational change |

**Examples:**
- **1-3 months**: "Migrate single CRM app before contract renewal"
- **3-6 months**: "Move e-commerce platform for holiday season"
- **6-12 months**: "Enterprise-wide cloud transformation"
- **12+ months**: "Re-platform 500 applications with containerization"

**Impacts:**
- **Short timelines**: Higher costs, more risk, less optimization
- **Longer timelines**: Lower costs, phased approach, better outcomes

---

### **Field 5: Priority**

**What it is:**  
Business importance and urgency relative to other initiatives.

**Why we need it:**  
- Determines resource allocation
- Affects response times and support level
- Influences escalation paths

**Options Explained:**

| Priority | When to Choose | What You Get |
|----------|---------------|-------------|
| **High** | • Revenue-impacting<br>• Regulatory deadline<br>• Contract expiration<br>• Security vulnerability<br>• Executive mandate | • Dedicated team<br>• Daily standups<br>• Senior architects<br>• Fast-track approvals<br>• Premium support |
| **Medium** | • Standard migration<br>• Planned initiative<br>• Cost optimization<br>• Technical debt reduction | • **Most common**<br>• Shared resources<br>• Weekly check-ins<br>• Standard support<br>• Normal SLAs |
| **Low** | • Exploratory/pilot<br>• Nice-to-have<br>• Long-term planning<br>• Cost-driven only | • Best-effort basis<br>• Monthly updates<br>• Self-service tools<br>• Standard SLAs |

**Examples:**
- **High**: "Data center lease ends in 90 days - must migrate"
- **Medium**: "Strategic cloud initiative - no hard deadline"
- **Low**: "Testing cloud for future projects"

**Tips:**
- Be honest about true priority
- Not everything can be "High"
- Priority affects cost and timelines

---

### **Field 6: Budget Range**

**What it is:**  
Estimated total budget for the migration project (professional services + AWS costs).

**Why we need it:**  
- Determines scope and approach
- Influences migration strategy (lift-and-shift vs. modernize)
- Sets expectations for what's achievable

**Options Explained:**

| Budget | Typical Scope | What It Covers |
|--------|--------------|----------------|
| **< $100K** | • 1-5 small apps<br>• Lift-and-shift only<br>• Minimal support<br>• POC/pilot projects | • Basic assessment<br>• Simple migration tools<br>• Limited consulting<br>• Self-service mostly |
| **$100K - $500K** | • 5-25 medium apps<br>• Some optimization<br>• Standard support<br>• **Most common** | • Full discovery<br>• Migration execution<br>• Testing support<br>• 3-6 months consulting<br>• Basic training |
| **$500K - $1M** | • 25-100 apps<br>• Significant modernization<br>• Premium support<br>• Enterprise scale | • Deep assessment<br>• Phased execution<br>• Architecture redesign<br>• 6-12 months consulting<br>• Comprehensive training |
| **$1M+** | • 100+ apps<br>• Complete transformation<br>• White-glove service<br>• Multi-cloud/hybrid | • Strategic planning<br>• Wave-based migration<br>• Custom tooling<br>• Dedicated team<br>• Change management<br>• Ongoing optimization |

**Budget Breakdown Example ($500K):**
```
Professional Services: $300K (60%)
- Discovery & Assessment: $50K
- Migration Planning: $50K
- Migration Execution: $150K
- Testing & Validation: $30K
- Training: $20K

AWS Costs (Year 1): $200K (40%)
- Compute: $100K
- Storage: $40K
- Network: $30K
- Services: $30K
```

**Tips:**
- Include BOTH professional services AND AWS costs
- Factor in 12 months of AWS run costs
- Add 20% contingency for unknowns
- Consider training and support costs

---

### **Field 7: Complexity**

**What it is:**  
Technical difficulty and risk level of the migration.

**Why we need it:**  
- Determines team expertise required
- Affects timeline and cost estimates
- Influences risk mitigation strategies

**Options Explained:**

| Complexity | Characteristics | Examples |
|-----------|----------------|----------|
| **Simple** | • Modern, well-documented apps<br>• Standard tech stack<br>• Minimal dependencies<br>• Clear architecture<br>• Good test coverage | • New SaaS app (< 2 years old)<br>• Containerized microservices<br>• Stateless web apps<br>• Standard LAMP stack |
| **Moderate** | • Some legacy components<br>• Common tech stack<br>• Documented dependencies<br>• Reasonable architecture<br>• **Most common** | • 5-10 year old Java/Node apps<br>• Monolithic but modular<br>• Well-maintained database<br>• Standard integrations |
| **Complex** | • Legacy technology<br>• Custom frameworks<br>• Many dependencies<br>• Outdated documentation<br>• Technical debt | • 10-20 year old systems<br>• Tightly coupled architecture<br>• Custom middleware<br>• Complex data relationships<br>• Multiple data centers |
| **Very Complex** | • Ancient technology<br>• Undocumented<br>• Critical business systems<br>• High risk<br>• Massive scale | • Mainframe/COBOL<br>• Home-grown platforms<br>• Payment/financial systems<br>• 1000+ dependencies<br>• 24/7 availability requirement |

**Complexity Factors:**

1. **Technology Age**
   - Simple: < 3 years old
   - Complex: > 15 years old

2. **Architecture**
   - Simple: Microservices, containers
   - Complex: Monolith, tightly coupled

3. **Dependencies**
   - Simple: < 10 external systems
   - Complex: > 50 integrations

4. **Data**
   - Simple: < 100GB, single database
   - Complex: > 10TB, multiple DBMS

5. **Compliance**
   - Simple: None/basic
   - Complex: PCI-DSS, HIPAA, SOX

6. **Availability**
   - Simple: 99% (7h downtime/month OK)
   - Complex: 99.99% (< 5min/month)

**Examples:**

**Simple:**
```
Modern React SPA + Node.js API + MongoDB
- Deployed with Docker
- Full test coverage
- 100GB data
- No compliance requirements
```

**Moderate:**
```
10-year-old Java Spring app + Oracle DB
- Some technical debt
- Reasonable documentation
- 2TB data
- Basic security requirements
```

**Complex:**
```
15-year-old .NET monolith + SQL Server + custom C++ components
- Limited documentation
- 50+ integrations
- 10TB data
- PCI-DSS compliant
- 99.9% uptime SLA
```

**Very Complex:**
```
25-year-old mainframe COBOL + custom middleware + multiple databases
- Original developers retired
- Business-critical (revenue system)
- 100TB data
- SOX/HIPAA/PCI-DSS
- 99.99% uptime
- Can't fail
```

---

## 📁 Page 2: Projects (Project Management)

### Purpose
View all migration projects, track progress, and manage the migration portfolio.

---

### **Features Explained**

#### **1. Search Bar**
- Search by project name or description
- Real-time filtering
- Use keywords like "CRM", "e-commerce", "AWS"

#### **2. Filter by Status**
- **Planning**: Project created, discovery not started
- **In Progress**: Agents currently executing
- **Completed**: All agents finished, migration done
- **Failed**: Errors occurred, needs attention

#### **3. Sort Options**
- **Created Date (Newest)**: Most recent projects first (default)
- **Created Date (Oldest)**: Earliest projects first
- **Progress**: Highest completion % first
- **Name**: Alphabetical order

#### **4. Project Cards**

Each card shows:

| Element | What It Means |
|---------|---------------|
| **Project Name** | Title from onboarding |
| **Priority Badge** | High (red), Medium (orange), Low (green) |
| **Description** | First 100 characters of description |
| **Status** | Current project state (color-coded) |
| **Phase** | Discovery → Assessment → Execution → Optimization |
| **Timeline** | Expected duration |
| **Progress Bar** | % of agents completed (0-100%) |

#### **5. Actions**
- **📋 Details**: View full project information
- **⚙️ Execute**: Go to agent execution page

---

### **Understanding Progress**

Progress is calculated as:
```
Progress = (Completed Agents / Total Agents) × 100%
         = (X / 24) × 100%
```

**Examples:**
- 0% = Project created, no agents run
- 33% = Discovery phase complete (8/24 agents)
- 54% = Discovery + Assessment complete (13/24 agents)
- 100% = All 24 agents complete

---

## ⚙️ Page 3: Agent Execution

### Purpose
Execute AI agents to automate discovery, assessment, planning, and migration execution.

---

### **The 4 Phases**

#### **Phase 1: Discovery (8 agents)**

**Goal**: Understand current environment

| Agent | What It Does | Output |
|-------|-------------|--------|
| **Discovery** | Scans infrastructure, identifies all resources | Infrastructure inventory |
| **Analysis** | Analyzes application dependencies and architecture | Dependency map |
| **Planning** | Creates migration roadmap and wave plan | Migration plan |
| **Artifact Generation** | Generates documentation and diagrams | Architecture docs |
| **Network Scanner** | Maps network topology and connectivity | Network diagram |
| **Application Profiler** | Profiles application performance and behavior | Performance baseline |
| **Performance Monitor** | Establishes performance baselines | Metrics dashboard |
| **Data Classifier** | Classifies data (sensitive, PII, etc.) | Data inventory |

**When to run**: First, immediately after project creation

**Duration**: ~12 seconds (demo mode) / 2-4 hours (real execution)

**Outputs**:
- Infrastructure inventory (VMs, databases, storage)
- Application dependency map
- Network topology diagram
- Data classification report
- Performance baselines

---

#### **Phase 2: Assessment (5 agents)**

**Goal**: Deep analysis and planning

| Agent | What It Does | Output |
|-------|-------------|--------|
| **Dependency Mapper** | Maps all dependencies between applications | Full dependency graph |
| **Compliance Checker** | Validates compliance requirements (PCI, HIPAA, etc.) | Compliance gap analysis |
| **Cost Estimator** | Estimates migration costs and TCO | Cost projection |
| **Risk Assessment** | Identifies migration risks and mitigation strategies | Risk register |
| **Capacity Planner** | Plans cloud capacity and sizing | Sizing recommendations |

**When to run**: After Discovery phase completes

**Duration**: ~8 seconds (demo) / 1-3 hours (real)

**Outputs**:
- Detailed dependency analysis
- Compliance gap report
- Cost breakdown (current vs. cloud)
- Risk mitigation plan
- AWS sizing recommendations

---

#### **Phase 3: Execution (6 agents)**

**Goal**: Perform the actual migration

| Agent | What It Does | Output |
|-------|-------------|--------|
| **Infrastructure Provisioner** | Creates AWS infrastructure (VPC, subnets, etc.) | Provisioned resources |
| **Data Migration** | Migrates databases and storage | Migrated data |
| **Application Migration** | Migrates application code and configurations | Deployed applications |
| **Configuration** | Configures applications, networking, security | Configured environment |
| **Testing** | Runs automated tests to validate migration | Test results |
| **Rollback** | Creates rollback procedures and snapshots | Rollback plan |

**When to run**: After Assessment phase, when ready to migrate

**Duration**: ~9 seconds (demo) / Hours to days (real, depending on size)

**Outputs**:
- Provisioned AWS infrastructure
- Migrated databases
- Deployed applications
- Test reports
- Rollback procedures

---

#### **Phase 4: Optimization (5 agents)**

**Goal**: Optimize the migrated environment

| Agent | What It Does | Output |
|-------|-------------|--------|
| **Performance Optimizer** | Tunes performance (auto-scaling, caching, etc.) | Performance improvements |
| **Cost Optimizer** | Reduces costs (right-sizing, reserved instances) | Cost savings |
| **Security Hardening** | Implements security best practices | Security posture |
| **Monitoring Setup** | Configures CloudWatch, alarms, dashboards | Monitoring solution |
| **Documentation** | Generates runbooks and operational docs | Documentation |

**When to run**: After successful migration and testing

**Duration**: ~8 seconds (demo) / 1-2 days (real)

**Outputs**:
- Optimized performance
- Cost reduction recommendations
- Security hardening report
- CloudWatch dashboards
- Operational runbooks

---

### **Agent Status Icons**

| Icon | Status | Meaning |
|------|--------|---------|
| ⏸️ | **Queued** | Agent hasn't run yet (gray) |
| 🟡 | **Running** | Agent currently executing (yellow, animated) |
| ✅ | **Completed** | Agent finished successfully (green) |
| ❌ | **Failed** | Agent encountered an error (red) |

---

### **How to Execute Agents**

#### **Option 1: Run All (Recommended)**
1. Click "▶️ Run All Discovery Agents" button
2. All 8 agents execute sequentially
3. Progress bar shows overall completion
4. Takes ~12 seconds (demo mode)

#### **Option 2: Individual Execution**
1. Click individual agent card
2. Click "Run [Agent Name]" button
3. That agent executes alone
4. Takes ~1.5 seconds per agent (demo)

---

### **Execution Summary**

Bottom of page shows:

| Metric | Meaning |
|--------|---------|
| **Total Agents** | 24 (always) |
| **Completed** | Number of agents finished successfully |
| **Running** | Number of agents currently executing |
| **Failed** | Number of agents that encountered errors |

When all 24 agents complete:
- Progress bar reaches 100%
- 🎉 Success message appears
- Balloons animation plays

---

## 🎯 Typical Customer Journey

### **Day 1: Onboarding**
1. Customer fills out onboarding form
2. Creates project: "E-Commerce Platform Migration"
3. Enters requirements, timeline (3-6 months), budget ($500K)
4. Clicks "Create Project"

### **Day 1-2: Discovery**
1. Navigates to Agent Execution page
2. Clicks "Run All Discovery Agents"
3. Waits for agents to complete (~2-4 hours)
4. Reviews generated artifacts:
   - Infrastructure inventory
   - Dependency maps
   - Performance baselines

### **Day 3-5: Assessment**
1. Runs Assessment phase agents
2. Reviews cost estimates and risks
3. Discusses findings with stakeholders
4. Approves migration plan

### **Week 2-12: Execution**
1. Runs Execution phase (in waves)
2. Migrates databases first
3. Then applications
4. Runs tests
5. Fixes issues
6. Repeats for each wave

### **Week 12-14: Optimization**
1. Runs Optimization phase
2. Tunes performance
3. Reduces costs
4. Hardens security
5. Completes documentation

### **Week 14+: Production**
1. Final cutover
2. Decommission old systems
3. Ongoing optimization

---

## 💡 Tips for Presenting to Customers

### **When showing Onboarding:**
- Focus on how it captures their business context
- Explain that agents use this info to guide decisions
- Emphasize it takes < 5 minutes to fill out

### **When showing Projects:**
- Highlight the portfolio view
- Show how they can track multiple migrations
- Demonstrate search/filter capabilities

### **When showing Agent Execution:**
- Emphasize the automation ("AI does the heavy lifting")
- Show the progress tracking
- Explain that demo mode is instant, real mode takes hours
- Highlight the 24 agents across 4 phases

### **Key Selling Points:**
1. **Speed**: AI automation reduces weeks to hours
2. **Accuracy**: 24 specialized agents, no human error
3. **Visibility**: Real-time progress tracking
4. **Repeatability**: Same process every time
5. **Scalability**: Handle 100s of migrations

---

**Questions?** This guide covers everything customers need to know about the onboarding flow.
