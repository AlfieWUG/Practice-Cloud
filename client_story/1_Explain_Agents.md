# Client Storyline: Explain Agents

## Scene 1 – Set the Context (1 min)
1. Begin on the Streamlit dashboard home page.
2. Mention that the platform uses autonomous agents to accelerate cloud modernization.
3. Highlight that each agent represents a specialized consultant: discovery, analysis, risk, cost, etc.

## Scene 2 – Tour the Agent Catalog (3 min)
1. Navigate to the "Agents" page (menu item on the left sidebar).
2. Describe how agents are grouped by domain: discovery, planning, migration, optimization.
3. For each group, pick one agent and briefly explain its role (e.g., "Discovery Agent reads documentation to build an inventory").
4. Point out the metadata per agent (inputs, outputs, dependencies, run history) to show transparency.

## Scene 3 – Deep Dive per Focus Area (4 min)
Work left-to-right across the catalog and give clients tangible hooks for each cluster:

### Migration Discovery Agents
- **Discovery Agent** – Connects to vCenter/CMDB, inventories servers, tags criticality.
- **Documentation Parser** – Reads Word/PDF runbooks, extracts architecture facts.
- **Dependency Mapper** – Builds application/service graphs and highlights choke points.

### Assessment & Planning Agents
- **Assessment Agent** – Scores cloud readiness, classifies each app into 6Rs, projects cost/ROI.
- **Risk Assessment Agent** – Flags gaps (unsupported OS, missing DR, single points of failure).
- **Planning Agent** – Generates wave plans, timelines, rollback steps, and dependencies.

### FinOps Agents
- **Cost Optimizer** – Models target-state spend, recommends reserved capacity vs on-demand.
- **Budget Guardrail Agent** – Monitors planned vs actual cloud cost during execution.

### AIOps / Operations Agents
- **Monitoring Setup Agent** – Auto-configures observability stack (CloudWatch, Datadog, etc.).
- **Automation Agent** – Applies runbooks for patching, scaling, and incident remediation.

Explain that each agent card in the UI links to docs/run histories so stakeholders know exactly what inputs/outputs to expect.

## Scene 3 – Show an Agent in Action (4 min)
1. Select a real project (or demo project) with past agent executions.
2. Open an execution record to show the steps, logs, and generated artifacts.
3. Explain how agents chain together—e.g., discovery feeds analysis, then planning.
4. Emphasize governance: every run is logged with timestamps, user identity, and evidence files.

## Scene 4 – Value Proposition (2 min)
1. Summarize the benefits: repeatability, explainable decisions, audit trail.
2. Tie back to client needs (faster assessments, consistent recommendations, reduced manual effort).
3. Invite questions about extending agents or plugging in client-specific logic.
