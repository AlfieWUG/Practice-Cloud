"""Agents overview page"""

import streamlit as st

def render_agents_page():
    """Show all 24 implemented agents organized by functional focus area"""

    # Professional Header
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%); 
                    padding: 2.5rem 2rem; border-radius: 16px; border: 2px solid #2A2F4A; 
                    margin-bottom: 2rem; border-left: 6px solid #60c8b1;
                    box-shadow: 0 10px 40px rgba(96, 200, 177, 0.2);">
            <h1 style="color: #60c8b1; font-size: 2.5rem; font-weight: 800; margin: 0 0 0.5rem 0;">
                AI Agents Portfolio
            </h1>
            <p style="color: #B0B0B0; font-size: 1.1rem; margin: 0; line-height: 1.6;">
                Intelligent automation organized by business function
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Stats overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Agents", "24", "100% Complete")
    with col2:
        st.metric("Focus Areas", "3", "Core Functions")
    with col3:
        st.metric("Coverage", "100%", "End-to-End")
    with col4:
        st.metric("Status", "✅ Ready", "Deployed")
    
    st.divider()

    def render_focus_area(title: str, icon_letter: str, description: str, agents: list, color: str = "#60c8b1"):
        """Render a functional focus area with agents in a clean grid layout"""
        
        # Focus area header with professional icon badge - DARK THEME
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%); 
                    padding: 1.5rem; border-radius: 12px; border-left: 5px solid {color}; 
                    margin-bottom: 1.5rem; border: 2px solid #2A2F4A;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background: {color}; color: #FFFFFF; width: 50px; height: 50px; border-radius: 8px; 
                            display: flex; align-items: center; justify-content: center; font-size: 1.5rem; 
                            font-weight: 800; flex-shrink: 0;">{icon_letter}</div>
                <div>
                    <h2 style="color: {color}; margin: 0; font-size: 1.8rem; font-weight: 700;">{title}</h2>
                    <p style="color: #B0B0B0; margin: 0.3rem 0 0 0; font-size: 1rem; font-weight: 500;">{description}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if not agents:
            # Empty state
            st.markdown(f"""
            <div style="background: #1A1F3A; padding: 3rem; border-radius: 8px; border: 2px dashed #2A2F4A; text-align: center;">
                <p style="color: #B0B0B0; font-size: 1.1rem; margin: 0;">Exciting agents coming soon to this focus area!</p>
                <p style="color: #808080; font-size: 0.9rem; margin: 0.5rem 0 0 0;">Stay tuned for updates as we expand our capabilities.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            return
        
        # Display agents in 3-column grid
        num_cols = 3
        rows = [agents[i:i + num_cols] for i in range(0, len(agents), num_cols)]
        
        for row in rows:
            cols = st.columns(num_cols)
            for idx, agent in enumerate(row):
                with cols[idx]:
                    # Agent card - DARK THEME
                    agent_initial = agent['name'][0].upper()
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%); 
                                padding: 1.2rem; border-radius: 12px; border: 2px solid #2A2F4A; 
                                border-left: 4px solid {color};
                                height: 100%; transition: all 0.3s;">
                        <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
                            <div style="background: {color}; color: #FFFFFF; width: 32px; height: 32px; 
                                        border-radius: 6px; display: flex; align-items: center; 
                                        justify-content: center; font-size: 0.9rem; font-weight: 800; 
                                        margin-right: 0.8rem;">{agent_initial}</div>
                            <span style="background: #2ECC71; color: white; padding: 0.2rem 0.5rem; 
                                        border-radius: 4px; font-size: 0.7rem; font-weight: bold;">LIVE</span>
                        </div>
                        <h4 style="color: #60c8b1; margin: 0 0 0.5rem 0; font-size: 1rem; font-weight: 600;">{agent['name']}</h4>
                        <p style="color: #B0B0B0; font-size: 0.85rem; margin: 0; line-height: 1.4;">{agent['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Expandable details
                    with st.expander("View Capabilities"):
                        if agent.get('capabilities'):
                            for cap in agent['capabilities']:
                                st.markdown(f"• {cap}", help=None)
            
            # Add spacing between rows
            if row != rows[-1]:
                st.markdown("<div style='margin: 0.8rem 0;'></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

    # ======================================================================
    # FOCUS AREA 1: MIGRATION & MODERNIZATION
    # ======================================================================
    migration_agents = [
        {"name": "Infrastructure Scanner", "description": "Scans and inventories existing infrastructure across cloud and on-premise", "capabilities": ["Multi-cloud discovery", "Asset inventory", "Configuration mapping", "Technology stack detection"]},
        {"name": "Application Profiler", "description": "Profiles applications for performance, dependencies, and resource usage", "capabilities": ["Performance profiling", "Resource analysis", "Bottleneck identification", "Scaling pattern detection"]},
        {"name": "Data Discovery", "description": "Discovers and classifies data sources with PII detection", "capabilities": ["Data source discovery", "PII detection", "Compliance mapping (GDPR/HIPAA)", "Data lineage tracking"]},
        {"name": "Dependency Mapper", "description": "Maps application dependencies and service relationships", "capabilities": ["Service dependency mapping", "API integration analysis", "Critical path identification", "Circular dependency detection"]},
        {"name": "Integration Mapper", "description": "Maps external integrations, APIs, and third-party services", "capabilities": ["API discovery", "Integration point mapping", "Authentication flow analysis", "Webhook identification"]},
        {"name": "Network Analyzer", "description": "Analyzes network topology, connectivity, and security", "capabilities": ["Network topology mapping", "Port scanning", "Firewall rule analysis", "Latency measurement"]},
        {"name": "Infrastructure Provisioner", "description": "Provisions cloud infrastructure using Infrastructure as Code", "capabilities": ["IaC generation (Terraform/CloudFormation)", "Multi-region deployment", "Resource tagging", "Network configuration"]},
        {"name": "Data Migration", "description": "Migrates databases and file systems with validation", "capabilities": ["Database migration", "Schema transformation", "Data validation", "Incremental sync"]},
        {"name": "Application Migration", "description": "Migrates applications and services to cloud platforms", "capabilities": ["Containerization", "Zero-downtime migration", "Configuration management", "Rollback procedures"]},
        {"name": "Configuration Manager", "description": "Configures security groups, IAM roles, and networking", "capabilities": ["Security configuration", "IAM policy management", "Network ACLs", "Secrets management"]},
        {"name": "Testing Orchestrator", "description": "Orchestrates functional, performance, and integration testing", "capabilities": ["Automated testing", "Performance benchmarking", "Integration validation", "Regression testing"]},
        {"name": "Rollback Manager", "description": "Manages rollback procedures and disaster recovery", "capabilities": ["Automated rollback", "Snapshot management", "Disaster recovery", "Failover automation"]},
    ]
    render_focus_area(
        "Migration & Modernization",
        "M",  # Professional letter badge
        "End-to-end cloud migration, modernization, and platform transformation",
        migration_agents,
        "#60c8b1"
    )

    # ======================================================================
    # FOCUS AREA 2: COST OPTIMIZATION & FINOPS
    # ======================================================================
    finops_agents = [
        {"name": "Cost Estimator", "description": "Estimates migration and operational costs with TCO analysis", "capabilities": ["Migration cost estimation", "TCO analysis", "ROI calculation", "Cost comparison (cloud vs on-prem)"]},
        {"name": "Capacity Planner", "description": "Plans resource capacity and sizing for optimal performance", "capabilities": ["Resource sizing recommendations", "Capacity planning", "Auto-scaling strategy", "Growth forecasting"]},
        {"name": "Performance Baseline", "description": "Establishes performance baselines and SLA benchmarks", "capabilities": ["Performance baselining", "SLA monitoring", "Metrics collection", "Anomaly detection"]},
        {"name": "Cost Optimizer", "description": "Optimizes cloud costs through resource right-sizing and recommendations", "capabilities": ["Resource right-sizing", "Reserved instance recommendations", "Spot instance optimization", "Unused resource cleanup"]},
        {"name": "Performance Optimizer", "description": "Optimizes application and infrastructure performance", "capabilities": ["Bottleneck identification", "Cache optimization", "Query optimization", "Load balancing tuning"]},
    ]
    render_focus_area(
        "Cost Optimization & FinOps",
        "F",  # Professional letter badge
        "Cost management, optimization, and financial operations for cloud resources",
        finops_agents,
        "#3498db"
    )

    # ======================================================================
    # FOCUS AREA 3: AIOPS & INTELLIGENT OPERATIONS
    # ======================================================================
    aiops_agents = [
        {"name": "Security Auditor", "description": "Audits security configurations and identifies vulnerabilities", "capabilities": ["Security auditing", "Vulnerability scanning", "Compliance checking", "Threat detection"]},
        {"name": "Compliance Checker", "description": "Validates compliance with GDPR, HIPAA, PCI-DSS, SOC 2, ISO 27001", "capabilities": ["Compliance validation", "Gap analysis", "Risk scoring", "Remediation recommendations"]},
        {"name": "Risk Assessor", "description": "Identifies and assesses technical, business, and security risks", "capabilities": ["Risk identification", "Impact analysis", "Probability assessment", "Mitigation planning"]},
        {"name": "Licensing Analyzer", "description": "Analyzes software licenses and identifies compliance issues", "capabilities": ["License discovery", "Compliance checking", "Cost analysis", "Optimization recommendations"]},
        {"name": "Security Hardening", "description": "Hardens security configurations and enforces best practices", "capabilities": ["Security hardening", "Policy enforcement", "Vulnerability remediation", "Best practice implementation"]},
        {"name": "Monitoring Setup", "description": "Sets up comprehensive monitoring, alerting, and observability", "capabilities": ["Monitoring configuration", "Alert management", "Dashboard creation", "Log aggregation"]},
        {"name": "Documentation Generator", "description": "Generates comprehensive documentation, runbooks, and diagrams", "capabilities": ["Auto-documentation", "Runbook generation", "Architecture diagrams", "API documentation"]},
    ]
    render_focus_area(
        "AIOps & Intelligent Operations",
        "A",  # Professional letter badge
        "AI-powered operations, security, compliance, and observability",
        aiops_agents,
        "#e74c3c"
    )

    # Summary footer
    st.divider()
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%); 
                padding: 2rem; border-radius: 12px; border: 2px solid #2A2F4A; text-align: center;">
        <h3 style="color: #60c8b1; margin: 0 0 1rem 0; font-size: 1.5rem; font-weight: 700;">Complete AI-Powered Platform</h3>
        <p style="color: #B0B0B0; font-size: 1rem; margin: 0; line-height: 1.6;">
            Our comprehensive suite of 24 AI agents provides end-to-end automation across migration, 
            cost optimization, and intelligent operations. Each agent leverages AWS Bedrock's Claude models 
            for intelligent decision-making and seamless integration.
        </p>
    </div>
    """, unsafe_allow_html=True)
