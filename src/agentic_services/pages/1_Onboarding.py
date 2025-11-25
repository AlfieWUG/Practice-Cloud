"""Customer Onboarding - Create New Migration Projects"""
import streamlit as st
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.nagarro_theme import apply_nagarro_theme
from database import get_db
from auth.auth import DashboardAuth

# Page config
st.set_page_config(
    page_title="Onboarding | Nagarro Agentic Services",
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

# Get database instance
db = get_db()

# Load projects from database
projects = db.get_all_projects()

# Header
st.markdown('<h1 class="page-title">Customer Onboarding</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #B0B0B0; font-size: 1.1rem; margin-bottom: 2rem;">Create a new cloud migration project and get started with AI-powered agents</p>', unsafe_allow_html=True)

st.markdown("---")

# Project Creation Form
st.markdown('<h2 class="professional-header">Create New Migration Project</h2>', unsafe_allow_html=True)

with st.form("onboarding_form", clear_on_submit=True):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        project_name = st.text_input(
            "Project Name *",
            placeholder="e.g., E-Commerce Platform Migration",
            help="A descriptive name for your migration project"
        )
        
        description = st.text_area(
            "Description",
            placeholder="Brief overview of the project...",
            help="High-level description of the migration scope",
            height=100
        )
        
        requirements = st.text_area(
            "Requirements & Goals",
            placeholder="• Migrate 100+ microservices\n• 5TB of product data\n• Zero-downtime migration\n• Maintain compliance standards",
            help="Detailed requirements, goals, and constraints",
            height=150
        )
    
    with col2:
        timeline = st.selectbox(
            "Timeline",
            ["1-3 months", "3-6 months", "6-12 months", "12+ months"],
            help="Expected project duration"
        )
        
        priority = st.selectbox(
            "Priority",
            ["High", "Medium", "Low"],
            help="Business priority level"
        )
        
        budget = st.selectbox(
            "Budget Range",
            ["< $100K", "$100K - $500K", "$500K - $1M", "$1M+"],
            help="Estimated project budget"
        )
        
        complexity = st.selectbox(
            "Complexity",
            ["Simple", "Moderate", "Complex", "Very Complex"],
            help="Technical complexity assessment"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_cancel, col_submit = st.columns([1, 1])
    
    with col_cancel:
        cancel = st.form_submit_button("← Back to Dashboard", use_container_width=True)
    
    with col_submit:
        submitted = st.form_submit_button("Create Project", use_container_width=True, type="primary")
    
    if cancel:
        st.switch_page("app_streamlit.py")
    
    if submitted:
        if not project_name:
            st.error("Warning: Project name is required")
        else:
            # Create new project in database
            project_data = {
                'name': project_name,
                'description': description,
                'requirements': requirements,
                'timeline': timeline,
                'priority': priority,
                'budget': budget,
                'complexity': complexity,
                'status': 'Planning',
                'phase': 'Discovery',
                'progress': 0,
                'demo_mode': True
            }
            
            project_id = db.create_project(project_data)
            
            # Load created project and store in session for navigation
            project = db.get_project(project_id)
            st.session_state.current_project = project
            
            st.success(f"Success: Project '{project_name}' created successfully!")
            st.balloons()
            
            # Small delay for user feedback
            import time
            time.sleep(1)
            
            # Navigate to agent execution page
            st.switch_page("pages/3_Agent_Execution.py")

st.markdown("---")

# Display existing projects
if projects:
    st.markdown('<h2 class="professional-header">Your Projects</h2>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: #B0B0B0; margin-bottom: 1.5rem;">You have {len(projects)} project(s)</p>', unsafe_allow_html=True)
    
    for project in projects:
        with st.expander(f"Project: {project['name']} - {project['status']}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Description:** {project.get('description', 'No description')}")
                st.markdown(f"**Phase:** {project['phase']}")
                
                if project.get('requirements'):
                    st.markdown("**Requirements:**")
                    st.text(project['requirements'][:200] + "..." if len(project['requirements']) > 200 else project['requirements'])
            
            with col2:
                st.markdown(f"**Timeline:** {project.get('timeline', 'N/A')}")
                st.markdown(f"**Priority:** {project.get('priority', 'N/A')}")
                st.markdown(f"**Budget:** {project.get('budget', 'N/A')}")
            
            with col3:
                st.markdown(f"**Progress:** {project['progress']}%")
                st.progress(project['progress'] / 100)
                created_at = project.get('created_at', project.get('created', 'N/A'))
                if isinstance(created_at, str):
                    st.markdown(f"**Created:** {created_at[:10]}")
                else:
                    st.markdown(f"**Created:** N/A")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_view, col_execute = st.columns([1, 1])
            
            with col_view:
                if st.button("View Project", key=f"view_{project['id']}", use_container_width=True):
                    st.session_state.current_project = project
                    st.switch_page("pages/2_Projects.py")
            
            with col_execute:
                if st.button("Execute Agents", key=f"exec_{project['id']}", use_container_width=True):
                    st.session_state.current_project = project
                    st.switch_page("pages/3_Agent_Execution.py")
else:
    # Empty state
    st.markdown("""
    <div class="feature-card" style="text-align: center; padding: 3rem;">
        <h3 style="font-size: 3rem; margin-bottom: 1rem;"></h3>
        <h3>No Projects Yet</h3>
        <p>Create your first migration project above to get started with AI-powered cloud migration</p>
    </div>
    """, unsafe_allow_html=True)

# Footer with quick stats
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Projects", len(projects))

with col2:
    active_projects = sum(1 for p in projects if p['status'] != 'Completed')
    st.metric("Active Projects", active_projects)

with col3:
    completed_projects = sum(1 for p in projects if p['status'] == 'Completed')
    st.metric("Completed", completed_projects)

with col4:
    avg_progress = sum(p['progress'] for p in projects) / len(projects) if projects else 0
    st.metric("Avg Progress", f"{avg_progress:.0f}%")
