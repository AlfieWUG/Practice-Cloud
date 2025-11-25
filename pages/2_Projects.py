"""Projects Overview - View All Migration Projects"""
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agentic_services.ui.unified_theme import apply_unified_theme
from src.agentic_services.database import get_db
from src.agentic_services.auth.auth import DashboardAuth

# Page config
st.set_page_config(
    page_title="Projects | Nagarro Agentic Services",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# CRITICAL: Enforce authentication FIRST - DISABLED FOR TESTING
# auth = DashboardAuth()
# auth.require_auth()

# Apply unified theme
apply_unified_theme()

# Import and render unified sidebar navigation
from src.agentic_services.ui.unified_navigation import render_unified_sidebar
render_unified_sidebar()

# Get database instance
db = get_db()

# Load projects from database
all_projects = db.get_all_projects()

# Professional Header Section
st.markdown("""
    <div style="background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%); 
                padding: 2.5rem 2rem; border-radius: 16px; border: 2px solid #2A2F4A; 
                margin-bottom: 2rem; border-left: 6px solid #60c8b1;
                box-shadow: 0 10px 40px rgba(96, 200, 177, 0.2);">
        <h1 style="color: #60c8b1; font-size: 2.5rem; font-weight: 800; margin: 0 0 0.5rem 0;">
            Migration Projects
        </h1>
        <p style="color: #B0B0B0; font-size: 1.1rem; margin: 0; line-height: 1.6;">
            Manage and monitor your cloud migration projects
        </p>
    </div>
""", unsafe_allow_html=True)

# Quick actions
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("Create New Project", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Onboarding.py")

st.markdown("---")

# Initialize projects variable (will be used in summary metrics)
projects = all_projects

# Check if there are projects
if not all_projects:
    # Professional Empty State
    st.markdown("""
    <div class="feature-card" style="text-align: center; padding: 4rem;">
        <div style="background: linear-gradient(135deg, #60c8b1 0%, #4db89f 100%); 
                    width: 100px; height: 100px; border-radius: 20px; 
                    display: inline-flex; align-items: center; justify-content: center; 
                    margin-bottom: 2rem; box-shadow: 0 6px 20px rgba(96, 200, 177, 0.4);">
            <div style="width: 50px; height: 50px; border: 4px solid white; border-radius: 8px;"></div>
        </div>
        <h2 style="color: #60c8b1; font-size: 2rem; margin-bottom: 1rem;">No Projects Yet</h2>
        <p style="color: #B0B0B0; font-size: 1.2rem; margin: 1.5rem 0; line-height: 1.6;">
            Create your first migration project to get started with AI-powered agents
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Create Your First Project", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Onboarding.py")
else:
    # Filter and sort options
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search = st.text_input("Search projects", placeholder="Search by name or description...", label_visibility="visible")
    
    with col2:
        filter_status = st.selectbox(
            "Filter by Status",
            ["All", "Planning", "In Progress", "Completed", "Failed"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Created Date (Newest)", "Created Date (Oldest)", "Progress", "Name"]
        )
    
    st.markdown("---")
    
    # Filter projects
    filtered_projects = all_projects
    
    if search:
        filtered_projects = [
            p for p in filtered_projects 
            if search.lower() in p['name'].lower() 
            or search.lower() in p.get('description', '').lower()
        ]
    
    if filter_status != "All":
        filtered_projects = [p for p in filtered_projects if p['status'] == filter_status]
    
    # Sort projects
    if sort_by == "Created Date (Newest)":
        filtered_projects = sorted(filtered_projects, key=lambda x: x.get('created_at', x.get('created', '')), reverse=True)
    elif sort_by == "Created Date (Oldest)":
        filtered_projects = sorted(filtered_projects, key=lambda x: x.get('created_at', x.get('created', '')))
    elif sort_by == "Progress":
        filtered_projects = sorted(filtered_projects, key=lambda x: x['progress'], reverse=True)
    elif sort_by == "Name":
        filtered_projects = sorted(filtered_projects, key=lambda x: x['name'])
    
    # Display count
    st.markdown(f'<p style="color: #B0B0B0; margin-bottom: 1.5rem;">Showing {len(filtered_projects)} of {len(all_projects)} projects</p>', unsafe_allow_html=True)
    
    # Display projects in grid
    num_cols = 3
    rows = [filtered_projects[i:i+num_cols] for i in range(0, len(filtered_projects), num_cols)]
    
    for row in rows:
        cols = st.columns(num_cols)
        
        for idx, project in enumerate(row):
            with cols[idx]:
                # Status color
                status_colors = {
                    'Planning': '#2196f3',
                    'In Progress': '#ff9800',
                    'Completed': '#4caf50',
                    'Failed': '#f44336'
                }
                status_color = status_colors.get(project['status'], '#B0B0B0')
                
                # Priority badge color
                priority_colors = {
                    'High': '#f44336',
                    'Medium': '#ff9800',
                    'Low': '#4caf50'
                }
                priority_color = priority_colors.get(project.get('priority', 'Medium'), '#B0B0B0')
                
                # Project card using container
                with st.container():
                    # Header with title and priority badge
                    header_col1, header_col2 = st.columns([4, 1])
                    with header_col1:
                        st.markdown(f"###  {project['name']}")
                    with header_col2:
                        st.markdown(f'<span style="background: {priority_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; display: inline-block;">{project.get("priority", "Medium")}</span>', unsafe_allow_html=True)
                    
                    # Description
                    desc = project.get('description', 'No description')
                    desc_truncated = desc[:100] + ('...' if len(desc) > 100 else '')
                    st.write(desc_truncated)
                    
                    st.markdown("")
                    
                    # Status info
                    info_col1, info_col2 = st.columns(2)
                    with info_col1:
                        st.markdown(f"**Status:** :blue[{project['status']}]")
                        st.markdown(f"**Phase:** {project['phase']}")
                    with info_col2:
                        st.markdown(f"**Timeline:** {project.get('timeline', 'N/A')}")
                        st.markdown(f"**Progress:** {project['progress']}%")
                    
                    st.markdown("")
                
                # Progress bar
                st.progress(project['progress'] / 100)
                
                # Action buttons
                col_view, col_exec = st.columns(2)
                
                with col_view:
                    if st.button(" Details", key=f"details_{project['id']}", use_container_width=True):
                        st.session_state.current_project = project
                        # Stay on this page and show details below
                        st.rerun()
                
                with col_exec:
                    if st.button("️ Execute", key=f"execute_{project['id']}", use_container_width=True):
                        st.session_state.current_project = project
                        st.switch_page("pages/3_Agent_Execution.py")
                
                st.markdown("<br>", unsafe_allow_html=True)
    
    # Show project details if one is selected
    if st.session_state.get('current_project'):
        st.markdown("---")
        st.markdown('<h2 class="professional-header"> Project Details</h2>', unsafe_allow_html=True)
        
        project = st.session_state.current_project
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {project['name']}")
            st.markdown(f"**Description:** {project.get('description', 'No description')}")
            
            if project.get('requirements'):
                st.markdown("**Requirements:**")
                st.text(project['requirements'])
        
        with col2:
            st.markdown(f"**Status:** {project['status']}")
            st.markdown(f"**Phase:** {project['phase']}")
            st.markdown(f"**Priority:** {project.get('priority', 'N/A')}")
            st.markdown(f"**Timeline:** {project.get('timeline', 'N/A')}")
            st.markdown(f"**Budget:** {project.get('budget', 'N/A')}")
            st.markdown(f"**Complexity:** {project.get('complexity', 'N/A')}")
            
            # Handle created date field (db uses created_at, old session_state used created)
            created_date = project.get('created_at', project.get('created', 'N/A'))
            if isinstance(created_date, str) and len(created_date) >= 10:
                st.markdown(f"**Created:** {created_date[:10]}")
            else:
                st.markdown(f"**Created:** N/A")
        
        st.markdown("**Progress:**")
        st.progress(project['progress'] / 100)
        st.markdown(f"{project['progress']}% complete")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Connected pages navigation
        st.markdown('<h3 style="color: #60c8b1; margin-top: 2rem;">📋 Project Configuration</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #B0B0B0; margin-bottom: 1rem;">Configure project resources and settings</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("☁️ Cloud Credentials", key="detail_credentials", use_container_width=True):
                st.switch_page("pages/4_Cloud_Credentials.py")
        
        with col2:
            if st.button("🏗️ Source Infrastructure", key="detail_infrastructure", use_container_width=True):
                st.switch_page("pages/5_Source_Infrastructure.py")
        
        with col3:
            if st.button("💻 Source Code", key="detail_code", use_container_width=True):
                st.switch_page("pages/6_Source_Code.py")
        
        with col4:
            if st.button("🎯 Target Config", key="detail_target", use_container_width=True):
                st.switch_page("pages/7_Target_Configuration.py")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Action buttons
        st.markdown('<h3 style="color: #60c8b1;">⚡ Actions</h3>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("️ Execute Agents", key="detail_execute", use_container_width=True, type="primary"):
                st.switch_page("pages/3_Agent_Execution.py")
        
        with col2:
            if st.button("✏ Edit Project", key="detail_edit", use_container_width=True):
                st.info("Edit functionality coming soon!")
        
        with col3:
            # Delete project with confirmation
            if st.button("🗑 Delete Project", key="detail_delete", use_container_width=True):
                st.session_state.show_delete_confirmation = True
                st.rerun()
        
        # Delete confirmation dialog
        if st.session_state.get('show_delete_confirmation') and st.session_state.get('current_project'):
            st.markdown("---")
            st.error("⚠️ **Confirm Deletion**")
            st.markdown(f"""
            <div style="background: #1A1F3A; padding: 1.5rem; border-radius: 8px; border: 2px solid #f44336; margin: 1rem 0;">
                <p style="color: #FFFFFF; margin-bottom: 1rem;">
                    Are you sure you want to delete <strong>{project['name']}</strong>?
                </p>
                <p style="color: #B0B0B0; font-size: 0.9rem;">
                    This action cannot be undone. All project data, configurations, and related information will be permanently deleted.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
                if st.button("✅ Yes, Delete Project", key="confirm_delete", use_container_width=True, type="primary"):
                    try:
                        # Delete the project from database
                        success = db.delete_project(project['id'])
                        
                        if success:
                            st.success(f"✅ Project '{project['name']}' has been deleted successfully!")
                            
                            # Clear session state
                            if 'current_project' in st.session_state:
                                del st.session_state.current_project
                            if 'show_delete_confirmation' in st.session_state:
                                del st.session_state.show_delete_confirmation
                            
                            # Small delay for user to see success message
                            import time
                            time.sleep(1)
                            
                            # Refresh the page to show updated project list
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete project. Please try again.")
                            if 'show_delete_confirmation' in st.session_state:
                                del st.session_state.show_delete_confirmation
                    except Exception as e:
                        st.error(f"❌ Error deleting project: {str(e)}")
                        if 'show_delete_confirmation' in st.session_state:
                            del st.session_state.show_delete_confirmation
            
            with col_cancel:
                if st.button("❌ Cancel", key="cancel_delete", use_container_width=True):
                    if 'show_delete_confirmation' in st.session_state:
                        del st.session_state.show_delete_confirmation
                    st.rerun()

# Summary metrics
st.markdown("---")
st.markdown('<h2 class="section-header"> Summary</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Projects", len(projects))

with col2:
    in_progress = sum(1 for p in projects if p['status'] == 'In Progress')
    st.metric("In Progress", in_progress)

with col3:
    completed = sum(1 for p in projects if p['status'] == 'Completed')
    st.metric("Completed", completed)

with col4:
    avg_progress = sum(p['progress'] for p in projects) / len(projects) if projects else 0
    st.metric("Avg Progress", f"{avg_progress:.0f}%")
