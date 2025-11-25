"""Source Code - Configure Code Repository Access"""
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.nagarro_theme import apply_nagarro_theme
from auth.auth import DashboardAuth

# Page config
st.set_page_config(
    page_title="Source Code | Nagarro Agentic Services",
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

# Initialize source_code if not exists
if 'source_code' not in project:
    project['source_code'] = {}

# Header
st.markdown('<h1 class="page-title">Source Code Repositories</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="color: #B0B0B0; font-size: 1.1rem; margin-bottom: 2rem;">Configure access to source code for <strong>{project["name"]}</strong></p>', unsafe_allow_html=True)

st.info(" **Tip**: Providing repository access allows agents to analyze dependencies, frameworks, and generate accurate migration plans.")

st.markdown("---")

# Skip option for non-code migrations
has_code = st.checkbox(
    "This migration includes application source code",
    value=True,
    help="Disable if migrating infrastructure only (no custom applications)"
)

project['source_code']['has_code'] = has_code

if not has_code:
    st.success(" No source code configuration needed - infrastructure-only migration")
    st.markdown("---")
    
    # Navigation
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Back to Source Infrastructure", use_container_width=True):
            st.switch_page("pages/5_Source_Infrastructure.py")
    
    with col2:
        if st.button("Next: Target Configuration →", use_container_width=True, type="primary"):
            st.switch_page("pages/7_Target_Configuration.py")
    
    st.stop()

st.markdown("---")

# Repository Provider
st.markdown('<h2 class="professional-header">1. Repository Provider</h2>', unsafe_allow_html=True)

repo_provider = st.selectbox(
    "Select your code repository provider:",
    [
        "GitHub",
        "GitLab",
        "Bitbucket",
        "Azure DevOps",
        "AWS CodeCommit",
        "Self-Hosted Git",
        "Other"
    ],
    help="Where is your source code hosted?"
)

project['source_code']['provider'] = repo_provider

st.markdown("---")

# Authentication
st.markdown('<h2 class="professional-header">2. Authentication</h2>', unsafe_allow_html=True)

if repo_provider == "GitHub":
    st.markdown("### GitHub Access")
    st.markdown("""
    **To create a Personal Access Token:**
    1. Go to GitHub → Settings → Developer settings → Personal access tokens
    2. Generate new token (classic)
    3. Select scopes: `repo` (full control of private repositories)
    4. Copy and paste the token below
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        github_token = st.text_input(
            "GitHub Personal Access Token *",
            type="password",
            placeholder="ghp_xxxxxxxxxxxxxxxxxxxx",
            help="Your GitHub PAT with repo access",
            value=project['source_code'].get('token', '')
        )
    
    with col2:
        github_org = st.text_input(
            "Organization/Username",
            placeholder="your-org or your-username",
            help="GitHub organization or user account",
            value=project['source_code'].get('org', '')
        )
    
    project['source_code'].update({
        'token': github_token,
        'org': github_org
    })

elif repo_provider == "GitLab":
    st.markdown("### GitLab Access")
    st.markdown("""
    **To create an Access Token:**
    1. Go to GitLab → User Settings → Access Tokens
    2. Create new token with `read_api` and `read_repository` scopes
    3. Copy and paste below
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        gitlab_token = st.text_input(
            "GitLab Access Token *",
            type="password",
            placeholder="glpat-xxxxxxxxxxxxxxxxxxxx",
            help="Your GitLab access token",
            value=project['source_code'].get('token', '')
        )
    
    with col2:
        gitlab_url = st.text_input(
            "GitLab URL",
            value="https://gitlab.com",
            help="GitLab instance URL (leave default for gitlab.com)"
        )
    
    project['source_code'].update({
        'token': gitlab_token,
        'url': gitlab_url
    })

elif repo_provider == "Bitbucket":
    st.markdown("### Bitbucket Access")
    
    col1, col2 = st.columns(2)
    
    with col1:
        bitbucket_username = st.text_input(
            "Bitbucket Username",
            placeholder="your-username",
            value=project['source_code'].get('username', '')
        )
        
        bitbucket_password = st.text_input(
            "App Password *",
            type="password",
            placeholder="Create in Bitbucket Settings → App passwords",
            help="Bitbucket app password",
            value=project['source_code'].get('token', '')
        )
    
    with col2:
        bitbucket_workspace = st.text_input(
            "Workspace",
            placeholder="your-workspace",
            help="Bitbucket workspace name",
            value=project['source_code'].get('workspace', '')
        )
    
    project['source_code'].update({
        'username': bitbucket_username,
        'token': bitbucket_password,
        'workspace': bitbucket_workspace
    })

elif repo_provider == "Azure DevOps":
    st.markdown("### Azure DevOps Access")
    
    col1, col2 = st.columns(2)
    
    with col1:
        azure_org = st.text_input(
            "Organization",
            placeholder="your-organization",
            help="Azure DevOps organization name",
            value=project['source_code'].get('org', '')
        )
        
        azure_pat = st.text_input(
            "Personal Access Token *",
            type="password",
            placeholder="Azure DevOps PAT",
            help="PAT with Code (Read) permission",
            value=project['source_code'].get('token', '')
        )
    
    with col2:
        azure_project = st.text_input(
            "Project",
            placeholder="your-project",
            help="Azure DevOps project name",
            value=project['source_code'].get('project', '')
        )
    
    project['source_code'].update({
        'org': azure_org,
        'token': azure_pat,
        'project': azure_project
    })

elif repo_provider == "AWS CodeCommit":
    st.markdown("### AWS CodeCommit Access")
    st.success(" Will use AWS credentials from Cloud Credentials page")
    
    codecommit_region = st.selectbox(
        "CodeCommit Region",
        ["us-east-1", "us-west-2", "eu-west-1", "eu-central-1", "ap-southeast-1"],
        help="AWS region where CodeCommit repositories are located"
    )
    
    project['source_code']['region'] = codecommit_region

elif repo_provider == "Self-Hosted Git":
    st.markdown("### Self-Hosted Git Access")
    
    col1, col2 = st.columns(2)
    
    with col1:
        git_url = st.text_input(
            "Git Server URL",
            placeholder="https://git.yourcompany.com",
            help="URL of your self-hosted Git server",
            value=project['source_code'].get('url', '')
        )
        
        git_username = st.text_input(
            "Username",
            placeholder="git-username",
            value=project['source_code'].get('username', '')
        )
    
    with col2:
        git_password = st.text_input(
            "Password/Token",
            type="password",
            placeholder="password or token",
            help="Password or access token",
            value=project['source_code'].get('token', '')
        )
        
        git_ssh_key = st.text_area(
            "SSH Private Key (Optional)",
            placeholder="Paste SSH key if using key-based auth",
            height=100
        )
    
    project['source_code'].update({
        'url': git_url,
        'username': git_username,
        'token': git_password,
        'ssh_key': git_ssh_key
    })

else:  # Other
    st.markdown("### Other Repository Configuration")
    
    repo_details = st.text_area(
        "Repository Details",
        placeholder="Please provide details about your repository system...",
        height=150,
        help="Describe your repository system and access method"
    )
    
    project['source_code']['details'] = repo_details

st.markdown("---")

# Repository Configuration
st.markdown('<h2 class="professional-header">3. Repositories to Analyze</h2>', unsafe_allow_html=True)

repo_selection = st.radio(
    "Which repositories should agents analyze?",
    [
        "All repositories in organization/workspace",
        "Specific repositories only",
        "Repositories matching a pattern"
    ]
)

project['source_code']['selection_type'] = repo_selection

if repo_selection == "Specific repositories only":
    num_repos = st.number_input(
        "Number of repositories",
        min_value=1,
        max_value=50,
        value=project['source_code'].get('num_repos', 1),
        help="How many repositories?"
    )
    
    project['source_code']['num_repos'] = num_repos
    
    repositories = []
    
    for i in range(min(int(num_repos), 10)):  # Show first 10 in UI
        with st.expander(f" Repository {i+1}", expanded=(i==0)):
            col1, col2 = st.columns(2)
            
            with col1:
                repo_url = st.text_input(
                    "Repository URL or Name",
                    placeholder="owner/repo-name or full URL",
                    key=f"repo_url_{i}",
                    help="Repository identifier"
                )
                
                repo_branch = st.text_input(
                    "Branch/Tag",
                    placeholder="main or master or v1.0.0",
                    value="main",
                    key=f"repo_branch_{i}",
                    help="Branch or tag to analyze"
                )
            
            with col2:
                repo_language = st.selectbox(
                    "Primary Language",
                    ["Auto-detect", "Java", "Python", "JavaScript/Node.js", "C#/.NET", 
                     "Go", "Ruby", "PHP", "C/C++", "TypeScript", "Other"],
                    key=f"repo_lang_{i}"
                )
                
                repo_framework = st.text_input(
                    "Framework/Stack",
                    placeholder="e.g., Spring Boot, Django, React",
                    key=f"repo_framework_{i}",
                    help="Main framework or tech stack"
                )
            
            repositories.append({
                'url': repo_url,
                'branch': repo_branch,
                'language': repo_language,
                'framework': repo_framework
            })
    
    project['source_code']['repositories'] = repositories
    
    if num_repos > 10:
        st.info(f"ℹ You have {num_repos} repositories. First 10 shown above. Use bulk upload for remaining.")
        st.download_button(
            "📥 Download Repository List Template",
            data="Repository URL,Branch,Language,Framework\n",
            file_name="repository-list-template.csv",
            mime="text/csv"
        )

elif repo_selection == "Repositories matching a pattern":
    pattern = st.text_input(
        "Repository name pattern",
        placeholder="e.g., *-service, backend-*, prod-*",
        help="Use * as wildcard. Example: 'app-*' matches app-api, app-web, etc."
    )
    
    project['source_code']['pattern'] = pattern

st.markdown("---")

# Build Configuration
st.markdown('<h2 class="professional-header">4. Build Configuration (Optional)</h2>', unsafe_allow_html=True)

has_build = st.checkbox(
    "Analyze build configuration and dependencies",
    value=True,
    help="Enable to analyze package dependencies and build scripts"
)

if has_build:
    st.markdown("### Dependency Files")
    
    dependency_files = st.multiselect(
        "Select dependency files to analyze:",
        [
            "package.json (Node.js/npm)",
            "requirements.txt (Python/pip)",
            "Pipfile (Python/pipenv)",
            "pom.xml (Java/Maven)",
            "build.gradle (Java/Gradle)",
            "Gemfile (Ruby)",
            "composer.json (PHP)",
            "go.mod (Go)",
            "Cargo.toml (Rust)",
            "packages.config (C#/NuGet)",
            "project.json (C#)",
        ],
        default=["package.json (Node.js/npm)", "requirements.txt (Python/pip)"],
        help="Agents will scan these files to analyze dependencies"
    )
    
    project['source_code']['dependency_files'] = dependency_files
    
    col1, col2 = st.columns(2)
    
    with col1:
        dockerfile = st.checkbox(
            "Scan Dockerfiles",
            value=True,
            help="Analyze Docker configurations"
        )
    
    with col2:
        ci_cd = st.checkbox(
            "Analyze CI/CD pipelines",
            value=True,
            help="Scan .github/workflows, .gitlab-ci.yml, etc."
        )
    
    project['source_code'].update({
        'dockerfile': dockerfile,
        'ci_cd': ci_cd
    })

st.markdown("---")

# Test Connection
st.markdown('<h2 class="professional-header">5. Validate Access</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(" Test Connection", use_container_width=True, type="primary"):
        # TODO: Add repository connection test
        st.success(" Repository access validated! (Mock - real validation coming soon)")

with col2:
    if st.button(" List Repositories", use_container_width=True):
        # TODO: List accessible repositories
        st.info("⏳ Repository listing coming soon")

with col3:
    if st.button("🔎 Scan Dependencies", use_container_width=True):
        # TODO: Scan dependency files
        st.info("⏳ Dependency scanning coming soon")

st.markdown("---")

# Navigation
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("← Back to Source Infrastructure", use_container_width=True):
        st.switch_page("pages/5_Source_Infrastructure.py")

with col2:
    if st.button("Skip for Now", use_container_width=True):
        st.info("You can configure repositories later")

with col3:
    if st.button("Next: Target Configuration →", use_container_width=True, type="primary"):
        st.switch_page("pages/7_Target_Configuration.py")

# Configuration Summary
st.markdown("---")
st.markdown("###  Configuration Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Provider", project['source_code'].get('provider', 'Not configured'))

with col2:
    if project['source_code'].get('selection_type'):
        selection = project['source_code']['selection_type'].split()[0]
        st.metric("Selection", selection)
    else:
        st.metric("Selection", "Not configured")

with col3:
    repo_count = project['source_code'].get('num_repos', 'All')
    if repo_selection == "All repositories in organization/workspace":
        repo_count = "All"
    st.metric("Repositories", repo_count)
