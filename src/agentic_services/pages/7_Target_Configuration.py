"""Target Configuration - Define Migration Target Settings"""
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.nagarro_theme import apply_nagarro_theme
from auth.auth import DashboardAuth

# Page config
st.set_page_config(
    page_title="Target Configuration | Nagarro Agentic Services",
    page_icon="",
    layout="wide"
)

# CRITICAL: Enforce authentication FIRST
auth = DashboardAuth()
auth.require_auth()

# Apply theme

# Home button
col_home, col_space = st.columns([1, 5])
with col_home:
    if st.button("← Home", key="btn_home", use_container_width=True):
        st.switch_page("app_streamlit.py")
apply_nagarro_theme()

# Check if project is selected
if not st.session_state.get('current_project'):
    st.error("️ No project selected. Please create a project first.")
    if st.button("← Go to Onboarding"):
        st.switch_page("pages/1_Onboarding.py")
    st.stop()

project = st.session_state.current_project

# Initialize target_config if not exists
if 'target_config' not in project:
    project['target_config'] = {}

# Header
st.markdown('<h1 class="page-title">Target Configuration</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="color: #B0B0B0; font-size: 1.1rem; margin-bottom: 2rem;">Define your migration target for <strong>{project["name"]}</strong></p>', unsafe_allow_html=True)

st.info(" **Tip**: Configure your target AWS landing zone architecture, naming conventions, and compliance requirements.")

st.markdown("---")

# Target AWS Account
st.markdown('<h2 class="professional-header">1. Target AWS Environment</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    same_account = st.radio(
        "Target AWS Account",
        ["Same as source account", "Different AWS account"],
        help="Are you migrating to the same AWS account or a different one?"
    )
    
    if same_account == "Different AWS account":
        target_account_id = st.text_input(
            "Target AWS Account ID",
            placeholder="987654321098",
            help="12-digit AWS account ID for target environment",
            value=project['target_config'].get('target_account_id', '')
        )
        project['target_config']['target_account_id'] = target_account_id
    else:
        project['target_config']['same_account'] = True

with col2:
    target_region = st.selectbox(
        "Target AWS Region *",
        [
            "us-east-1 (N. Virginia)",
            "us-west-2 (Oregon)",
            "eu-west-1 (Ireland)",
            "eu-central-1 (Frankfurt)",
            "ap-southeast-1 (Singapore)",
            "ap-southeast-2 (Sydney)",
            "ap-northeast-1 (Tokyo)",
            "ca-central-1 (Canada)",
            "sa-east-1 (São Paulo)"
        ],
        help="Primary region for migrated resources"
    )
    
    multi_region_target = st.checkbox(
        "Deploy across multiple regions",
        value=False,
        help="Enable for multi-region deployments (DR, global apps)"
    )
    
    if multi_region_target:
        secondary_regions = st.multiselect(
            "Additional target regions:",
            ["us-east-1", "us-west-2", "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-northeast-1"],
            help="Regions for DR or multi-region deployment"
        )
        project['target_config']['secondary_regions'] = secondary_regions

project['target_config']['target_region'] = target_region.split()[0]
project['target_config']['multi_region'] = multi_region_target

st.markdown("---")

# Landing Zone Configuration
st.markdown('<h2 class="professional-header">2. Landing Zone / Network Architecture</h2>', unsafe_allow_html=True)

st.markdown("### VPC Configuration")

col1, col2 = st.columns(2)

with col1:
    vpc_option = st.radio(
        "VPC Setup",
        ["Create new VPC", "Use existing VPC"],
        help="Create a new VPC or migrate to existing one"
    )
    
    if vpc_option == "Create new VPC":
        vpc_cidr = st.text_input(
            "VPC CIDR Block *",
            placeholder="10.0.0.0/16",
            help="IP range for new VPC (e.g., 10.0.0.0/16)",
            value=project['target_config'].get('vpc_cidr', '10.0.0.0/16')
        )
        project['target_config']['vpc_cidr'] = vpc_cidr
    else:
        existing_vpc_id = st.text_input(
            "Existing VPC ID",
            placeholder="vpc-0123456789abcdef",
            help="VPC ID to deploy into",
            value=project['target_config'].get('existing_vpc_id', '')
        )
        project['target_config']['existing_vpc_id'] = existing_vpc_id

with col2:
    availability_zones = st.number_input(
        "Number of Availability Zones",
        min_value=2,
        max_value=6,
        value=3,
        help="Deploy across how many AZs (min 2 for HA)"
    )
    
    subnet_strategy = st.selectbox(
        "Subnet Strategy",
        [
            "Public + Private subnets",
            "Public + Private + Database subnets",
            "Private only (no public)",
            "Custom subnet design"
        ],
        help="Network isolation strategy"
    )

project['target_config'].update({
    'availability_zones': availability_zones,
    'subnet_strategy': subnet_strategy
})

st.markdown("### Network Features")

col1, col2, col3 = st.columns(3)

with col1:
    nat_gateway = st.selectbox(
        "NAT Gateway",
        ["One per AZ (HA)", "Single NAT Gateway", "NAT Instance", "No NAT"],
        help="Outbound internet access for private subnets"
    )

with col2:
    vpc_endpoints = st.multiselect(
        "VPC Endpoints",
        ["S3", "DynamoDB", "EC2", "SSM", "Secrets Manager", "ECR"],
        default=["S3", "DynamoDB"],
        help="Private access to AWS services (saves data transfer costs)"
    )

with col3:
    transit_gateway = st.checkbox(
        "Use Transit Gateway",
        value=False,
        help="Connect multiple VPCs (for large migrations)"
    )

project['target_config'].update({
    'nat_gateway': nat_gateway,
    'vpc_endpoints': vpc_endpoints,
    'transit_gateway': transit_gateway
})

st.markdown("---")

# Naming & Tagging
st.markdown('<h2 class="professional-header">3. Naming Conventions & Tagging</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Resource Naming")
    
    naming_pattern = st.text_input(
        "Naming Pattern",
        placeholder="e.g., {env}-{app}-{resource}-{id}",
        help="Pattern for resource names. Use {env}, {app}, {resource}, {id}",
        value=project['target_config'].get('naming_pattern', '{env}-{app}-{resource}')
    )
    
    environment_name = st.selectbox(
        "Environment",
        ["dev", "test", "staging", "prod", "dr"],
        help="Environment identifier for naming"
    )
    
    name_examples = st.text_area(
        "Example Names",
        value=f"{environment_name}-web-alb-01\n{environment_name}-api-ec2-01\n{environment_name}-data-rds-01",
        height=80,
        disabled=True,
        help="Preview of generated names"
    )

with col2:
    st.markdown("### Mandatory Tags")
    
    st.markdown("All resources will be tagged with:")
    
    tag_environment = st.text_input("Environment", value=environment_name, key="tag_env")
    tag_project = st.text_input("Project", value=project['name'][:50], key="tag_proj")
    tag_owner = st.text_input("Owner", placeholder="team@company.com", key="tag_owner")
    tag_cost_center = st.text_input("CostCenter", placeholder="Engineering", key="tag_cc")
    
    custom_tags = st.text_area(
        "Additional Tags (key=value, one per line)",
        placeholder="Application=ECommerce\nManagedBy=Terraform\nBackup=Daily",
        height=80,
        help="Any additional tags to apply"
    )

project['target_config'].update({
    'naming_pattern': naming_pattern,
    'environment': environment_name,
    'tags': {
        'Environment': tag_environment,
        'Project': tag_project,
        'Owner': tag_owner,
        'CostCenter': tag_cost_center,
        'custom': custom_tags
    }
})

st.markdown("---")

# Compliance & Security
st.markdown('<h2 class="professional-header">4. Compliance & Security Requirements</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Compliance Frameworks")
    
    compliance_reqs = st.multiselect(
        "Required Compliance Standards",
        [
            "PCI-DSS (Payment Card Industry)",
            "HIPAA (Healthcare)",
            "SOC 2 Type II",
            "ISO 27001",
            "GDPR (EU Privacy)",
            "FedRAMP (US Government)",
            "NIST",
            "None / Not Applicable"
        ],
        help="Select all that apply"
    )
    
    data_classification = st.selectbox(
        "Data Classification",
        ["Public", "Internal", "Confidential", "Highly Confidential"],
        help="Highest classification level of data"
    )

with col2:
    st.markdown("### Security Controls")
    
    encryption_at_rest = st.checkbox(
        "Encryption at rest (all storage)",
        value=True,
        help="Encrypt EBS, S3, RDS, etc."
    )
    
    encryption_in_transit = st.checkbox(
        "Encryption in transit (TLS/SSL)",
        value=True,
        help="Require HTTPS/TLS for all communication"
    )
    
    kms_key_type = st.radio(
        "KMS Key Type",
        ["AWS Managed Keys", "Customer Managed Keys (CMK)"],
        help="CMK gives more control but requires key management"
    )
    
    security_group_policy = st.selectbox(
        "Security Group Policy",
        ["Least privilege (default deny)", "Moderate", "Permissive"],
        help="Default security posture"
    )

project['target_config'].update({
    'compliance': compliance_reqs,
    'data_classification': data_classification,
    'encryption_at_rest': encryption_at_rest,
    'encryption_in_transit': encryption_in_transit,
    'kms_key_type': kms_key_type,
    'security_group_policy': security_group_policy
})

st.markdown("---")

# Operational Requirements
st.markdown('<h2 class="professional-header">5. Operational Requirements</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### High Availability")
    
    ha_requirement = st.selectbox(
        "HA Requirement",
        ["Multi-AZ (standard)", "Multi-Region (DR)", "Single AZ (dev/test)"],
        help="High availability strategy"
    )
    
    rto_target = st.selectbox(
        "RTO Target (Recovery Time)",
        ["< 1 hour", "< 4 hours", "< 24 hours", "Best effort"],
        help="How quickly must systems recover from failure?"
    )
    
    rpo_target = st.selectbox(
        "RPO Target (Data Loss)",
        ["< 5 minutes", "< 1 hour", "< 24 hours", "Best effort"],
        help="How much data loss is acceptable?"
    )

with col2:
    st.markdown("### Backup & Disaster Recovery")
    
    backup_frequency = st.selectbox(
        "Backup Frequency",
        ["Continuous (PITR)", "Hourly", "Daily", "Weekly", "None"],
        help="How often to backup data"
    )
    
    backup_retention = st.number_input(
        "Backup Retention (days)",
        min_value=1,
        max_value=365,
        value=30,
        help="How long to keep backups"
    )
    
    dr_strategy = st.selectbox(
        "DR Strategy",
        ["Pilot Light", "Warm Standby", "Multi-Site Active/Active", "Backup & Restore"],
        help="Disaster recovery approach"
    )

project['target_config'].update({
    'ha_requirement': ha_requirement,
    'rto_target': rto_target,
    'rpo_target': rpo_target,
    'backup_frequency': backup_frequency,
    'backup_retention': backup_retention,
    'dr_strategy': dr_strategy
})

st.markdown("---")

# Monitoring & Logging
st.markdown('<h2 class="professional-header">6. Monitoring & Logging</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    cloudwatch_logs = st.checkbox(
        "Enable CloudWatch Logs",
        value=True,
        help="Centralized logging for all resources"
    )
    
    log_retention = st.selectbox(
        "Log Retention Period",
        ["7 days", "30 days", "90 days", "1 year", "Never expire"],
        help="How long to keep logs"
    )
    
    cloudtrail = st.checkbox(
        "Enable CloudTrail (API logging)",
        value=True,
        help="Track all API calls (required for compliance)"
    )

with col2:
    cloudwatch_alarms = st.checkbox(
        "Configure CloudWatch Alarms",
        value=True,
        help="Alert on resource health and performance"
    )
    
    alarm_notification = st.text_input(
        "Alarm Notification Email",
        placeholder="ops-team@company.com",
        help="Email for CloudWatch alarm notifications"
    )
    
    enable_xray = st.checkbox(
        "Enable AWS X-Ray (tracing)",
        value=False,
        help="Distributed tracing for microservices"
    )

project['target_config'].update({
    'cloudwatch_logs': cloudwatch_logs,
    'log_retention': log_retention,
    'cloudtrail': cloudtrail,
    'cloudwatch_alarms': cloudwatch_alarms,
    'alarm_notification': alarm_notification,
    'xray': enable_xray
})

st.markdown("---")

# Cost Optimization
st.markdown('<h2 class="professional-header">7. Cost Optimization Preferences</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    cost_priority = st.select_slider(
        "Cost vs Performance Priority",
        options=["Minimize Cost", "Balanced", "Maximize Performance"],
        value="Balanced",
        help="Guides instance sizing and service selection"
    )
    
    reserved_instances = st.checkbox(
        "Consider Reserved Instances",
        value=True,
        help="RIs provide up to 75% savings for predictable workloads"
    )
    
    savings_plans = st.checkbox(
        "Consider Savings Plans",
        value=True,
        help="Flexible commitment-based discounts"
    )

with col2:
    spot_instances = st.checkbox(
        "Use Spot Instances where possible",
        value=False,
        help="Up to 90% savings but can be interrupted"
    )
    
    auto_scaling = st.checkbox(
        "Enable Auto Scaling",
        value=True,
        help="Scale resources based on demand"
    )
    
    cost_budget = st.number_input(
        "Monthly Cost Budget (USD)",
        min_value=0,
        value=10000,
        step=1000,
        help="Target monthly AWS spend"
    )

project['target_config'].update({
    'cost_priority': cost_priority,
    'reserved_instances': reserved_instances,
    'savings_plans': savings_plans,
    'spot_instances': spot_instances,
    'auto_scaling': auto_scaling,
    'cost_budget': cost_budget
})

st.markdown("---")

# Summary & Validation
st.markdown('<h2 class="professional-header">8. Configuration Summary</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Target Region", project['target_config']['target_region'])
    st.metric("Environment", project['target_config']['environment'])

with col2:
    st.metric("Availability Zones", project['target_config']['availability_zones'])
    compliance_count = len(project['target_config'].get('compliance', []))
    st.metric("Compliance Standards", compliance_count)

with col3:
    st.metric("HA Strategy", project['target_config']['ha_requirement'].split('(')[0].strip())
    st.metric("Monthly Budget", f"${project['target_config']['cost_budget']:,}")

st.markdown("---")

# Navigation
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("← Back to Source Code", use_container_width=True):
        st.switch_page("pages/6_Source_Code.py")

with col2:
    if st.button("💾 Save Configuration", use_container_width=True):
        st.success(" Configuration saved to project!")

with col3:
    if st.button("Start Agent Execution →", use_container_width=True, type="primary"):
        st.success("🎉 Configuration complete! Redirecting to Agent Execution...")
        import time
        time.sleep(1)
        st.switch_page("pages/3_Agent_Execution.py")

# Configuration Review
with st.expander(" View Complete Configuration"):
    st.json(project['target_config'])
