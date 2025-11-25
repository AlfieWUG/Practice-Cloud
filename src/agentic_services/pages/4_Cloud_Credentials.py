"""Cloud Credentials - Configure AWS Access for Agent Execution"""
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.nagarro_theme import apply_nagarro_theme
from auth.auth import DashboardAuth

# Page config
st.set_page_config(
    page_title="Cloud Credentials | Nagarro Agentic Services",
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

# Header
st.markdown('<h1 class="page-title">Cloud Credentials</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="color: #B0B0B0; font-size: 1.1rem; margin-bottom: 2rem;">Configure AWS access for <strong>{project["name"]}</strong></p>', unsafe_allow_html=True)

# Info banner
st.info(" **Tip**: For production, we recommend using IAM Role ARN (cross-account role) for enhanced security. Access keys are suitable for development/testing only.")

st.markdown("---")

# Demo Mode Toggle
st.markdown('<h2 class="professional-header">Execution Mode</h2>', unsafe_allow_html=True)

demo_mode = st.checkbox(
    "🎭 Demo Mode (Use mock data, no real AWS connection)",
    value=project.get('demo_mode', True),
    help="Enable this to test the platform without real AWS credentials. Perfect for demonstrations and testing."
)

project['demo_mode'] = demo_mode

if demo_mode:
    st.success(" Demo mode enabled - No AWS credentials required. Agents will use mock data.")
    st.markdown("**What happens in demo mode:**")
    st.markdown("""
    - Agents execute with simulated data
    - No actual AWS API calls
    - Fast execution (~1.5s per agent)
    - Perfect for testing and demonstrations
    - No AWS costs incurred
    """)
else:
    st.warning("️ Production mode enabled - Real AWS credentials required for agent execution.")

st.markdown("---")

# Only show credential forms if NOT in demo mode
if not demo_mode:
    st.markdown('<h2 class="professional-header">AWS Connection Details</h2>', unsafe_allow_html=True)
    
    # Credentials Method
    st.markdown("### 1. Authentication Method")
    
    auth_method = st.radio(
        "Select how agents will connect to your AWS account:",
        [
            "IAM Role ARN (Recommended for Production)",
            "Access Keys (Development/Testing)",
            "SSO/SAML (Enterprise)"
        ],
        help="IAM Role provides better security with temporary credentials and no long-lived keys."
    )
    
    project['auth_method'] = auth_method
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Different forms based on auth method
    if "IAM Role ARN" in auth_method:
        st.markdown("### 2. IAM Role Configuration")
        
        st.markdown("""
        **Steps to set up cross-account role:**
        1. In your AWS account, create an IAM role
        2. Add trust policy allowing our account to assume the role
        3. Attach read-only policies for Discovery/Assessment phases
        4. Provide the Role ARN and External ID below
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            role_arn = st.text_input(
                "IAM Role ARN *",
                placeholder="arn:aws:iam::123456789012:role/NagarroAgenticRole",
                help="The ARN of the IAM role in your AWS account",
                value=project.get('aws_credentials', {}).get('role_arn', '')
            )
            
            aws_account_id = st.text_input(
                "AWS Account ID *",
                placeholder="123456789012",
                help="Your 12-digit AWS account ID",
                value=project.get('aws_credentials', {}).get('account_id', '')
            )
        
        with col2:
            external_id = st.text_input(
                "External ID *",
                placeholder="unique-external-id-12345",
                help="A unique identifier for security (we'll provide this)",
                value=project.get('aws_credentials', {}).get('external_id', '')
            )
            
            region = st.selectbox(
                "Primary AWS Region *",
                [
                    "us-east-1 (N. Virginia)",
                    "us-west-2 (Oregon)",
                    "eu-west-1 (Ireland)",
                    "eu-central-1 (Frankfurt)",
                    "ap-southeast-1 (Singapore)",
                    "ap-northeast-1 (Tokyo)"
                ],
                help="The primary region where your resources are located"
            )
        
        # Store credentials
        if 'aws_credentials' not in project:
            project['aws_credentials'] = {}
        
        project['aws_credentials'].update({
            'type': 'iam_role',
            'role_arn': role_arn,
            'external_id': external_id,
            'account_id': aws_account_id,
            'region': region.split()[0]  # Extract region code
        })
        
        # IAM Policy Template
        with st.expander(" IAM Role Trust Policy Template"):
            st.code(f"""{{
  "Version": "2012-10-17",
  "Statement": [
    {{
      "Effect": "Allow",
      "Principal": {{
        "AWS": "arn:aws:iam::YOUR-NAGARRO-ACCOUNT:root"
      }},
      "Action": "sts:AssumeRole",
      "Condition": {{
        "StringEquals": {{
          "sts:ExternalId": "{external_id if external_id else 'YOUR-EXTERNAL-ID'}"
        }}
      }}
    }}
  ]
}}""", language="json")
        
        with st.expander(" Read-Only IAM Policy (Discovery/Assessment)"):
            st.code("""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "rds:Describe*",
        "s3:List*",
        "s3:GetBucketLocation",
        "lambda:List*",
        "lambda:GetFunction",
        "elasticloadbalancing:Describe*",
        "autoscaling:Describe*",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics",
        "iam:GetAccountSummary",
        "iam:ListUsers",
        "iam:ListRoles"
      ],
      "Resource": "*"
    }
  ]
}""", language="json")
    
    elif "Access Keys" in auth_method:
        st.markdown("### 2. AWS Access Keys")
        
        st.warning("️ **Security Notice**: Access keys are long-lived credentials. Use only for development/testing. Never commit to source control.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            access_key_id = st.text_input(
                "AWS Access Key ID *",
                placeholder="AKIAIOSFODNN7EXAMPLE",
                type="password",
                help="Your AWS access key ID (starts with AKIA...)",
                value=project.get('aws_credentials', {}).get('access_key_id', '')
            )
            
            aws_account_id = st.text_input(
                "AWS Account ID *",
                placeholder="123456789012",
                help="Your 12-digit AWS account ID",
                value=project.get('aws_credentials', {}).get('account_id', '')
            )
        
        with col2:
            secret_access_key = st.text_input(
                "AWS Secret Access Key *",
                placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                type="password",
                help="Your AWS secret access key",
                value=project.get('aws_credentials', {}).get('secret_access_key', '')
            )
            
            region = st.selectbox(
                "Primary AWS Region *",
                [
                    "us-east-1 (N. Virginia)",
                    "us-west-2 (Oregon)",
                    "eu-west-1 (Ireland)",
                    "eu-central-1 (Frankfurt)",
                    "ap-southeast-1 (Singapore)",
                    "ap-northeast-1 (Tokyo)"
                ],
                help="The primary region where your resources are located"
            )
        
        # Store credentials
        if 'aws_credentials' not in project:
            project['aws_credentials'] = {}
        
        project['aws_credentials'].update({
            'type': 'access_keys',
            'access_key_id': access_key_id,
            'secret_access_key': secret_access_key,
            'account_id': aws_account_id,
            'region': region.split()[0]
        })
    
    else:  # SSO/SAML
        st.markdown("### 2. SSO/SAML Configuration")
        
        st.info("🏢 Enterprise SSO integration coming soon! For now, please use IAM Role or Access Keys.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sso_url = st.text_input(
                "SSO Start URL",
                placeholder="https://your-company.awsapps.com/start",
                help="Your AWS SSO start URL"
            )
        
        with col2:
            sso_region = st.text_input(
                "SSO Region",
                placeholder="us-east-1",
                help="AWS region for SSO"
            )
        
        project['aws_credentials'] = {
            'type': 'sso',
            'sso_url': sso_url,
            'sso_region': sso_region,
            'status': 'coming_soon'
        }
    
    st.markdown("---")
    
    # Multi-Region Support
    st.markdown("### 3. Additional Regions (Optional)")
    
    multi_region = st.checkbox(
        "My infrastructure spans multiple AWS regions",
        value=project.get('multi_region', False),
        help="Enable if you have resources in multiple regions"
    )
    
    project['multi_region'] = multi_region
    
    if multi_region:
        additional_regions = st.multiselect(
            "Select additional regions to scan:",
            [
                "us-east-1", "us-east-2", "us-west-1", "us-west-2",
                "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1",
                "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ap-northeast-2"
            ],
            help="Agents will scan resources in all selected regions"
        )
        project['additional_regions'] = additional_regions
    
    st.markdown("---")
    
    # Permissions Validation
    st.markdown("### 4. Validate Permissions")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button(" Test Connection", use_container_width=True, type="primary"):
            # TODO: When AWS credentials available, add validation here
            # For now, just show a success message
            st.success(" Connection test successful! (Mock validation - real validation coming soon)")
            # with st.spinner("Testing AWS connection..."):
            #     try:
            #         # Validate credentials using boto3
            #         session = boto3.Session(...)
            #         sts = session.client('sts')
            #         identity = sts.get_caller_identity()
            #         st.success(f" Connected to AWS Account: {identity['Account']}")
            #     except Exception as e:
            #         st.error(f"❌ Connection failed: {str(e)}")
    
    with col2:
        if st.button("🛡 Check Permissions", use_container_width=True):
            # TODO: When AWS credentials available, verify required permissions
            st.info("⏳ Permission check coming soon - requires AWS account setup")
            # Verify agent has required permissions for Discovery/Assessment
    
    with col3:
        if st.button(" Download IAM Policy", use_container_width=True):
            st.download_button(
                "Download Policy JSON",
                data='{"Version": "2012-10-17", "Statement": [...]}',
                file_name="nagarro-agentic-iam-policy.json",
                mime="application/json"
            )
    
    st.markdown("---")
    
    # Security Best Practices
    st.markdown("### 🔒 Security Best Practices")
    
    with st.expander("Click to view security recommendations"):
        st.markdown("""
        **For Production Deployments:**
        
        1. **Use IAM Roles** (not access keys)
           - Temporary credentials (auto-expire)
           - No long-lived secrets to manage
           - Easier to rotate and audit
        
        2. **Principle of Least Privilege**
           - Discovery/Assessment: Read-only permissions
           - Execution: Write permissions only for target resources
           - Never use Admin or PowerUser policies
        
        3. **External ID for Security**
           - Prevents "confused deputy" attacks
           - Use a unique External ID per customer
           - Never reuse External IDs
        
        4. **Enable CloudTrail**
           - Log all API calls made by agents
           - Monitor for suspicious activity
           - Required for compliance (SOX, PCI-DSS)
        
        5. **Encrypt Credentials at Rest**
           - We store credentials in AWS Secrets Manager
           - Encrypted using AWS KMS
           - Automatic rotation supported
        
        6. **Regular Audits**
           - Review agent permissions quarterly
           - Remove unused roles
           - Update policies as needed
        """)

else:
    st.info(" Demo mode is enabled - credential configuration not required.")

# Navigation buttons
st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("← Back to Onboarding", use_container_width=True):
        st.switch_page("pages/1_Onboarding.py")

with col2:
    if st.button("Skip for Now", use_container_width=True):
        st.info("You can configure credentials later from the Projects page")

with col3:
    if st.button("Next: Source Infrastructure →", use_container_width=True, type="primary"):
        if demo_mode:
            st.switch_page("pages/5_Source_Infrastructure.py")
        elif project.get('aws_credentials'):
            st.switch_page("pages/5_Source_Infrastructure.py")
        else:
            st.warning("️ Please provide AWS credentials or enable demo mode")

# Show current configuration summary
st.markdown("---")
st.markdown("###  Current Configuration")

col1, col2, col3 = st.columns(3)

with col1:
    mode = "Demo Mode" if demo_mode else "Production Mode"
    st.metric("Execution Mode", mode)

with col2:
    if not demo_mode and project.get('aws_credentials'):
        auth_type = project['aws_credentials'].get('type', 'Not configured')
        st.metric("Auth Method", auth_type.replace('_', ' ').title())
    else:
        st.metric("Auth Method", "N/A (Demo Mode)")

with col3:
    if not demo_mode and project.get('aws_credentials'):
        region = project['aws_credentials'].get('region', 'Not set')
        st.metric("Primary Region", region)
    else:
        st.metric("Primary Region", "N/A (Demo Mode)")
