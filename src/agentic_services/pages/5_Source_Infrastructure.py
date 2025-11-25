"""Source Infrastructure - Configure Source Environment Details"""
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.nagarro_theme import apply_nagarro_theme
from auth.auth import DashboardAuth

# Page config
st.set_page_config(
    page_title="Source Infrastructure | Nagarro Agentic Services",
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

# Initialize source_infrastructure if not exists
if 'source_infrastructure' not in project:
    project['source_infrastructure'] = {}

# Header
st.markdown('<h1 class="page-title">Source Infrastructure</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="color: #B0B0B0; font-size: 1.1rem; margin-bottom: 2rem;">Define your current infrastructure for <strong>{project["name"]}</strong></p>', unsafe_allow_html=True)

st.info(" **Tip**: Provide details about your source environment so agents can discover and analyze your infrastructure accurately.")

st.markdown("---")

# Source Environment Type
st.markdown('<h2 class="professional-header">1. Source Environment Type</h2>', unsafe_allow_html=True)

source_type = st.radio(
    "Where is your current infrastructure hosted?",
    [
        "Cloud to Cloud (AWS to AWS)",
        "Cloud to Cloud (Other Cloud to AWS)",
        "On-Premises to Cloud",
        "Hybrid (Mixed Environment)"
    ],
    help="Select the type of migration you're performing"
)

project['source_infrastructure']['type'] = source_type

st.markdown("---")

# Cloud-to-Cloud Migration
if "Cloud to Cloud" in source_type:
    st.markdown('<h2 class="professional-header">2. Source Cloud Configuration</h2>', unsafe_allow_html=True)
    
    if "AWS to AWS" in source_type:
        st.success(" AWS to AWS migration - Use the same credentials from Cloud Credentials page")
        
        col1, col2 = st.columns(2)
        
        with col1:
            source_account = st.text_input(
                "Source AWS Account ID",
                placeholder="123456789012",
                help="The AWS account you're migrating FROM",
                value=project['source_infrastructure'].get('source_account_id', '')
            )
            
            source_vpc = st.text_input(
                "Source VPC ID (Optional)",
                placeholder="vpc-1234567890abcdef0",
                help="Specific VPC to migrate, or leave empty to scan all",
                value=project['source_infrastructure'].get('source_vpc', '')
            )
        
        with col2:
            source_region = st.selectbox(
                "Source AWS Region",
                [
                    "us-east-1 (N. Virginia)",
                    "us-west-2 (Oregon)",
                    "eu-west-1 (Ireland)",
                    "eu-central-1 (Frankfurt)",
                    "ap-southeast-1 (Singapore)",
                    "ap-northeast-1 (Tokyo)"
                ],
                help="Primary region of source infrastructure"
            )
            
            resource_tags = st.text_input(
                "Resource Tags (Optional)",
                placeholder="Environment=Production,Project=Migration",
                help="Filter resources by tags (comma-separated key=value pairs)",
                value=project['source_infrastructure'].get('resource_tags', '')
            )
        
        project['source_infrastructure'].update({
            'source_account_id': source_account,
            'source_region': source_region.split()[0],
            'source_vpc': source_vpc,
            'resource_tags': resource_tags
        })
    
    else:  # Other Cloud to AWS
        st.markdown("### Source Cloud Provider")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cloud_provider = st.selectbox(
                "Cloud Provider",
                ["Azure", "Google Cloud (GCP)", "Oracle Cloud", "IBM Cloud", "Alibaba Cloud"],
                help="Your current cloud provider"
            )
            
            provider_account = st.text_input(
                f"{cloud_provider} Account/Subscription ID",
                placeholder="Enter your account identifier",
                help=f"Your {cloud_provider} account or subscription ID"
            )
        
        with col2:
            provider_region = st.text_input(
                "Primary Region/Location",
                placeholder="e.g., eastus, us-central1",
                help="Primary region where resources are located"
            )
            
            # Placeholder for provider-specific auth
            st.text_input(
                "Access Credentials",
                placeholder="Will be configured separately",
                disabled=True,
                help="Provider-specific authentication (configure in advanced settings)"
            )
        
        project['source_infrastructure'].update({
            'cloud_provider': cloud_provider,
            'provider_account': provider_account,
            'provider_region': provider_region
        })
        
        st.info(f"ℹ {cloud_provider} to AWS migration requires provider-specific configuration. Our agents will guide you through the setup process.")

# On-Premises or Hybrid
else:
    st.markdown('<h2 class="professional-header">2. On-Premises Infrastructure</h2>', unsafe_allow_html=True)
    
    # Network Access Method
    st.markdown("### Network Access")
    
    access_method = st.selectbox(
        "How will agents access your on-premises infrastructure?",
        [
            "VPN Connection",
            "AWS Direct Connect",
            "Bastion Host / Jump Server",
            "Agent Deployment (Install on-prem)",
            "Manual Discovery (Provide inventory)"
        ],
        help="Select how our platform will connect to your environment"
    )
    
    project['source_infrastructure']['access_method'] = access_method
    
    if access_method == "VPN Connection":
        col1, col2 = st.columns(2)
        
        with col1:
            vpn_endpoint = st.text_input(
                "VPN Endpoint/Gateway",
                placeholder="vpn.yourcompany.com",
                help="VPN endpoint hostname or IP"
            )
            vpn_type = st.selectbox(
                "VPN Type",
                ["IPSec", "OpenVPN", "WireGuard", "Other"],
                help="Type of VPN connection"
            )
        
        with col2:
            vpn_credentials = st.text_area(
                "VPN Configuration",
                placeholder="VPN credentials will be securely stored",
                help="VPN authentication details (will be encrypted)",
                height=100
            )
        
        project['source_infrastructure'].update({
            'vpn_endpoint': vpn_endpoint,
            'vpn_type': vpn_type,
            'vpn_credentials': vpn_credentials
        })
    
    elif access_method == "AWS Direct Connect":
        st.info("📡 Direct Connect provides dedicated network connection from on-premises to AWS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dx_connection_id = st.text_input(
                "Direct Connect Connection ID",
                placeholder="dxcon-xxxxxx",
                help="Your AWS Direct Connect connection ID"
            )
        
        with col2:
            dx_vlan = st.text_input(
                "VLAN ID",
                placeholder="1234",
                help="VLAN ID for Direct Connect"
            )
        
        project['source_infrastructure'].update({
            'dx_connection_id': dx_connection_id,
            'dx_vlan': dx_vlan
        })
    
    elif access_method == "Bastion Host / Jump Server":
        col1, col2 = st.columns(2)
        
        with col1:
            bastion_host = st.text_input(
                "Bastion Host Address",
                placeholder="bastion.yourcompany.com or 10.0.0.50",
                help="Hostname or IP of jump server"
            )
            bastion_port = st.number_input(
                "SSH Port",
                value=22,
                min_value=1,
                max_value=65535,
                help="SSH port (usually 22)"
            )
        
        with col2:
            bastion_user = st.text_input(
                "SSH Username",
                placeholder="admin",
                help="Username for SSH authentication"
            )
            bastion_key = st.text_area(
                "SSH Private Key",
                placeholder="Paste SSH private key here (will be encrypted)",
                help="SSH private key for authentication",
                height=100
            )
        
        project['source_infrastructure'].update({
            'bastion_host': bastion_host,
            'bastion_port': bastion_port,
            'bastion_user': bastion_user,
            'bastion_key': bastion_key
        })
    
    elif access_method == "Agent Deployment (Install on-prem)":
        st.info(" We'll provide an agent to install in your on-premises environment")
        st.markdown("""
        **Agent Deployment Process:**
        1. Download our discovery agent
        2. Install on a server with network access
        3. Agent scans and reports back to our platform
        4. Secure, read-only access
        5. Can be uninstalled after discovery
        """)
        
        agent_platform = st.selectbox(
            "Agent Platform",
            ["Linux (x64)", "Windows Server", "Docker Container"],
            help="Operating system where agent will run"
        )
        
        project['source_infrastructure']['agent_platform'] = agent_platform
        
        st.download_button(
            "📥 Download Discovery Agent (Coming Soon)",
            data="# Agent download placeholder",
            file_name="nagarro-discovery-agent.sh",
            mime="text/plain",
            disabled=True
        )
    
    else:  # Manual Discovery
        st.info(" Manual discovery - You'll provide infrastructure inventory")
        st.markdown("""
        **Manual Discovery Process:**
        1. Download our inventory template (Excel/CSV)
        2. Fill in your infrastructure details
        3. Upload the completed inventory
        4. Agents will analyze based on your data
        """)
        
        st.download_button(
            "📥 Download Inventory Template",
            data="Server Name,IP Address,OS,CPU,Memory,Disk,Applications\n",
            file_name="infrastructure-inventory-template.csv",
            mime="text/csv"
        )
        
        uploaded_file = st.file_uploader(
            "Upload Completed Inventory",
            type=['csv', 'xlsx'],
            help="Upload your infrastructure inventory file"
        )
        
        if uploaded_file:
            st.success(f" Uploaded: {uploaded_file.name}")
            project['source_infrastructure']['inventory_file'] = uploaded_file.name
    
    st.markdown("---")
    
    # Server Discovery
    st.markdown("### Server/VM Discovery")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ip_ranges = st.text_area(
            "IP Address Ranges to Scan",
            placeholder="10.0.0.0/24\n192.168.1.0/24\n172.16.0.100-172.16.0.200",
            help="Enter IP ranges (CIDR or range notation), one per line",
            height=100,
            value=project['source_infrastructure'].get('ip_ranges', '')
        )
        
        ssh_enabled = st.checkbox(
            "Enable SSH scanning",
            value=True,
            help="Scan servers via SSH for detailed information"
        )
    
    with col2:
        ssh_credentials = st.text_area(
            "SSH Credentials (if enabled)",
            placeholder="username:password\nOR provide SSH keys above",
            help="Credentials for SSH access (will be encrypted)",
            height=100,
            disabled=not ssh_enabled
        )
        
        windows_enabled = st.checkbox(
            "Enable Windows scanning (WMI/RDP)",
            value=False,
            help="Scan Windows servers via WMI"
        )
    
    project['source_infrastructure'].update({
        'ip_ranges': ip_ranges,
        'ssh_enabled': ssh_enabled,
        'ssh_credentials': ssh_credentials if ssh_enabled else '',
        'windows_enabled': windows_enabled
    })
    
    st.markdown("---")
    
    # Database Discovery
    st.markdown("### Database Discovery")
    
    has_databases = st.checkbox(
        "I have databases to migrate",
        value=True,
        help="Enable database discovery and migration planning"
    )
    
    if has_databases:
        num_databases = st.number_input(
            "Number of databases",
            min_value=1,
            max_value=50,
            value=project['source_infrastructure'].get('num_databases', 1),
            help="How many databases need to be migrated?"
        )
        
        project['source_infrastructure']['num_databases'] = num_databases
        
        # Database connection details
        for i in range(min(int(num_databases), 5)):  # Limit to 5 in UI, rest can be bulk uploaded
            with st.expander(f" Database {i+1} Configuration", expanded=(i==0)):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    db_type = st.selectbox(
                        "Database Type",
                        ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "MongoDB", "MariaDB", "Other"],
                        key=f"db_type_{i}"
                    )
                
                with col2:
                    db_host = st.text_input(
                        "Hostname/IP",
                        placeholder="db.internal.com",
                        key=f"db_host_{i}"
                    )
                
                with col3:
                    db_port = st.number_input(
                        "Port",
                        value=5432 if db_type == "PostgreSQL" else 3306,
                        key=f"db_port_{i}"
                    )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    db_name = st.text_input(
                        "Database Name",
                        placeholder="production_db",
                        key=f"db_name_{i}"
                    )
                    db_user = st.text_input(
                        "Username (read-only)",
                        placeholder="readonly_user",
                        key=f"db_user_{i}"
                    )
                
                with col2:
                    db_password = st.text_input(
                        "Password",
                        type="password",
                        key=f"db_pass_{i}"
                    )
                    db_size = st.text_input(
                        "Estimated Size",
                        placeholder="e.g., 500GB",
                        key=f"db_size_{i}"
                    )
                
                # Store database config
                if f'databases' not in project['source_infrastructure']:
                    project['source_infrastructure']['databases'] = []
                
                # Ensure list is long enough
                while len(project['source_infrastructure']['databases']) <= i:
                    project['source_infrastructure']['databases'].append({})
                
                project['source_infrastructure']['databases'][i] = {
                    'type': db_type,
                    'host': db_host,
                    'port': db_port,
                    'name': db_name,
                    'user': db_user,
                    'password': db_password,
                    'size': db_size
                }
        
        if num_databases > 5:
            st.info(f"ℹ You have {num_databases} databases. First 5 shown above. Use bulk upload for remaining databases.")
            st.download_button(
                "📥 Download Database Inventory Template",
                data="Type,Host,Port,Name,Username,Password,Size\n",
                file_name="database-inventory-template.csv",
                mime="text/csv"
            )

st.markdown("---")

# Test Connectivity
st.markdown('<h2 class="professional-header">3. Validate Connectivity</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(" Test Network Access", use_container_width=True, type="primary"):
        # TODO: Add network connectivity test when infrastructure is available
        st.success(" Network test successful! (Mock validation - real test coming soon)")

with col2:
    if st.button("️ Scan Servers", use_container_width=True):
        # TODO: Add server scanning when agents are connected
        st.info("⏳ Server scanning coming soon - requires network access setup")

with col3:
    if st.button(" Test Databases", use_container_width=True):
        # TODO: Add database connectivity test
        st.info("⏳ Database test coming soon")

st.markdown("---")

# Navigation
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("← Back to Cloud Credentials", use_container_width=True):
        st.switch_page("pages/4_Cloud_Credentials.py")

with col2:
    if st.button("Skip for Now", use_container_width=True):
        st.info("You can configure source infrastructure later")

with col3:
    if st.button("Next: Source Code →", use_container_width=True, type="primary"):
        st.switch_page("pages/6_Source_Code.py")

# Configuration Summary
st.markdown("---")
st.markdown("###  Configuration Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Source Type", project['source_infrastructure'].get('type', 'Not configured').split('(')[0].strip())

with col2:
    access = project['source_infrastructure'].get('access_method', 'N/A')
    if 'Cloud to Cloud' in project['source_infrastructure'].get('type', ''):
        access = "Cloud API"
    st.metric("Access Method", access if len(access) < 20 else access[:17] + "...")

with col3:
    db_count = project['source_infrastructure'].get('num_databases', 0)
    st.metric("Databases", db_count)
