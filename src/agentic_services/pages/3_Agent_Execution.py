"""Agent Execution - Run Migration Agents by Phase"""
import streamlit as st
import sys
import os
import time
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.nagarro_theme import apply_nagarro_theme
from database import get_db
from auth.auth import DashboardAuth
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Agent Execution | Nagarro Agentic Services",
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

# Check if a project is selected
if not st.session_state.get('current_project'):
    st.error("️ No project selected")
    st.markdown("Please select a project from the Projects page.")
    
    if st.button("← Go to Projects"):
        st.switch_page("pages/2_Projects.py")
    
    st.stop()

project = st.session_state.current_project

# Define agents by phase (matching your actual agent structure)
AGENTS_BY_PHASE = {
    "Discovery": [
        "discovery", "analysis", "planning", "artifact_generation",
        "network_scanner", "application_profiler", "performance_monitor", "data_classifier"
    ],
    "Assessment": [
        "dependency_mapper", "compliance_checker", "cost_estimator",
        "risk_assessment", "capacity_planner"
    ],
    "Execution": [
        "infrastructure_provisioner", "data_migration", "application_migration",
        "configuration", "testing", "rollback"
    ],
    "Optimization": [
        "performance_optimizer", "cost_optimizer", "security_hardening",
        "monitoring_setup", "documentation"
    ]
}

# Format agent name for display
def format_agent_name(agent_name):
    return agent_name.replace('_', ' ').title()

# Get agent status from database
def get_agent_status(project_id, agent_name):
    # Get all executions for this project and find the latest for this agent
    executions = db.get_project_executions(project_id)
    agent_executions = [e for e in executions if e['agent_name'] == agent_name]
    
    if agent_executions:
        # Return the most recent execution
        return agent_executions[0]
    else:
        return {
            'status': 'queued',
            'progress': 0,
            'started_at': None,
            'completed_at': None,
            'error_message': None
        }

# Update agent status in database
def update_agent_status(project_id, agent_name, phase, status, progress=None, error=None, execution_id=None):
    if execution_id:
        # Update existing execution
        updates = {'status': status}
        if progress is not None:
            updates['progress'] = progress
        if error:
            updates['error_message'] = error
        if status in ['completed', 'failed']:
            updates['completed_at'] = datetime.now().isoformat()
            
            # Get the original execution to calculate duration
            executions = db.get_project_executions(project_id)
            current_exec = next((e for e in executions if e.get('id') == execution_id), None)
            if current_exec and current_exec.get('started_at'):
                try:
                    # Parse started_at (SQLite format: 2024-11-18 14:29:51)
                    started_str = current_exec['started_at']
                    if ' ' in started_str and 'T' not in started_str:
                        start_time = datetime.strptime(started_str, "%Y-%m-%d %H:%M:%S")
                    else:
                        start_time = datetime.fromisoformat(started_str.replace('Z', '+00:00'))
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    updates['duration_seconds'] = duration
                except (ValueError, AttributeError):
                    # If parsing fails, don't set duration
                    pass
        
        db.update_execution(execution_id, updates)
    else:
        # Create new execution
        execution_data = {
            'project_id': project_id,
            'agent_name': agent_name,
            'phase': phase,
            'status': status,
            'progress': progress or 0,
            'started_at': datetime.now().isoformat() if status == 'running' else None
        }
        execution_id = db.create_execution(execution_data)
    
    return execution_id

# Determine phase for agent
def get_agent_phase(agent_name):
    for phase, agents in AGENTS_BY_PHASE.items():
        if agent_name in agents:
            return phase
    return "Discovery"  # Default

# Mock agent execution function
def execute_agent(project_id, agent_name):
    """Mock execution - simulates 3-5 seconds of work"""
    phase = get_agent_phase(agent_name)
    
    # Create execution record
    execution_id = update_agent_status(project_id, agent_name, phase, 'running', 0)
    
    # Simulate progress
    for i in range(0, 101, 20):
        time.sleep(0.3)
        update_agent_status(project_id, agent_name, phase, 'running', i, execution_id=execution_id)
    
    # Mark as completed
    update_agent_status(project_id, agent_name, phase, 'completed', 100, execution_id=execution_id)
    
    # Update project progress in database
    total_agents = sum(len(agents) for agents in AGENTS_BY_PHASE.values())
    all_executions = db.get_project_executions(project_id)
    completed_agents = sum(1 for e in all_executions if e['status'] == 'completed')
    progress = int((completed_agents / total_agents) * 100)
    
    db.update_project(project_id, {'progress': progress})
    
    # Also update in session state for immediate UI update
    if st.session_state.get('current_project') and st.session_state.current_project['id'] == project_id:
        st.session_state.current_project['progress'] = progress

# Header
st.markdown(f'<h1 class="page-title">️ {project["name"]}</h1>', unsafe_allow_html=True)

# Project info bar
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    st.markdown(f"**Status:** {project['status']} | **Phase:** {project['phase']}")

with col2:
    st.markdown(f"**Priority:** {project.get('priority', 'N/A')}")

with col3:
    st.markdown(f"**Timeline:** {project.get('timeline', 'N/A')}")

with col4:
    if st.button("← Back to Projects"):
        st.switch_page("pages/2_Projects.py")

# Progress bar
st.markdown("**Overall Progress:**")
st.progress(project['progress'] / 100)
st.markdown(f"{project['progress']}% complete")

st.markdown("---")

# Agent execution by phase
st.markdown('<h2 class="professional-header">Execute AI Agents</h2>', unsafe_allow_html=True)

# Create tabs for each phase
tab1, tab2, tab3, tab4 = st.tabs([" Discovery", "📊 Assessment", "🚀 Execution", "⚡ Optimization"])

# Discovery Phase
with tab1:
    st.markdown("### Discovery Phase")
    st.markdown("Analyze and discover your current infrastructure, applications, and data")
    
    agents = AGENTS_BY_PHASE["Discovery"]
    
    # Run All button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("▶ Run All Discovery Agents", key="run_all_discovery", use_container_width=True):
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            for idx, agent in enumerate(agents):
                status_placeholder.markdown(f"Running **{format_agent_name(agent)}**...")
                execute_agent(project['id'], agent)
                progress_placeholder.progress((idx + 1) / len(agents))
            
            status_placeholder.success(" Discovery phase complete!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("---")
    
    # Display agents in grid
    cols = st.columns(3)
    for idx, agent in enumerate(agents):
        with cols[idx % 3]:
            status = get_agent_status(project['id'], agent)
            
            # Status icon and color
            if status['status'] == 'completed':
                icon = ""
                color = "#4caf50"
            elif status['status'] == 'running':
                icon = "🟡"
                color = "#ff9800"
            elif status['status'] == 'failed':
                icon = "❌"
                color = "#f44336"
            else:
                icon = "⏸"
                color = "#B0B0B0"
            
            st.markdown(f"""
            <div class="agent-card">
                <h3 style="display: flex; align-items: center; gap: 0.5rem;">
                    <span>{icon}</span>
                    <span>{format_agent_name(agent)}</span>
                </h3>
                <p style="color: {color}; font-weight: 600;">{status['status'].title()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if status['status'] == 'running':
                st.progress(status['progress'] / 100)
                st.markdown(f"{status['progress']}%")
            elif status['status'] == 'completed':
                st.progress(1.0)
                # Calculate duration safely
                duration_seconds = status.get('duration_seconds')
                if duration_seconds and isinstance(duration_seconds, (int, float)):
                    st.markdown(f" Completed in {duration_seconds:.1f}s")
                else:
                    st.markdown(" Completed")
            
            if status['status'] in ['queued', 'failed']:
                if st.button(f"Run {format_agent_name(agent)}", key=f"run_{agent}", use_container_width=True):
                    with st.spinner(f"Running {format_agent_name(agent)}..."):
                        execute_agent(project['id'], agent)
                    st.rerun()

# Assessment Phase
with tab2:
    st.markdown("### Assessment Phase")
    st.markdown("Deep analysis of dependencies, compliance, costs, and risks")
    
    agents = AGENTS_BY_PHASE["Assessment"]
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("▶ Run All Assessment Agents", key="run_all_assessment", use_container_width=True):
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            for idx, agent in enumerate(agents):
                status_placeholder.markdown(f"Running **{format_agent_name(agent)}**...")
                execute_agent(project['id'], agent)
                progress_placeholder.progress((idx + 1) / len(agents))
            
            status_placeholder.success(" Assessment phase complete!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("---")
    
    cols = st.columns(3)
    for idx, agent in enumerate(agents):
        with cols[idx % 3]:
            status = get_agent_status(project['id'], agent)
            
            if status['status'] == 'completed':
                icon = ""
                color = "#4caf50"
            elif status['status'] == 'running':
                icon = "🟡"
                color = "#ff9800"
            elif status['status'] == 'failed':
                icon = "❌"
                color = "#f44336"
            else:
                icon = "⏸"
                color = "#B0B0B0"
            
            st.markdown(f"""
            <div class="agent-card">
                <h3 style="display: flex; align-items: center; gap: 0.5rem;">
                    <span>{icon}</span>
                    <span>{format_agent_name(agent)}</span>
                </h3>
                <p style="color: {color}; font-weight: 600;">{status['status'].title()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if status['status'] == 'running':
                st.progress(status['progress'] / 100)
                st.markdown(f"{status['progress']}%")
            elif status['status'] == 'completed':
                st.progress(1.0)
                # Calculate duration safely
                duration_seconds = status.get('duration_seconds')
                if duration_seconds and isinstance(duration_seconds, (int, float)):
                    st.markdown(f" Completed in {duration_seconds:.1f}s")
                else:
                    st.markdown(" Completed")
            
            if status['status'] in ['queued', 'failed']:
                if st.button(f"Run {format_agent_name(agent)}", key=f"run_{agent}", use_container_width=True):
                    with st.spinner(f"Running {format_agent_name(agent)}..."):
                        execute_agent(project['id'], agent)
                    st.rerun()

# Execution Phase
with tab3:
    st.markdown("### Execution Phase")
    st.markdown("Provision infrastructure, migrate data and applications")
    
    agents = AGENTS_BY_PHASE["Execution"]
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("▶ Run All Execution Agents", key="run_all_execution", use_container_width=True):
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            for idx, agent in enumerate(agents):
                status_placeholder.markdown(f"Running **{format_agent_name(agent)}**...")
                execute_agent(project['id'], agent)
                progress_placeholder.progress((idx + 1) / len(agents))
            
            status_placeholder.success(" Execution phase complete!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("---")
    
    cols = st.columns(3)
    for idx, agent in enumerate(agents):
        with cols[idx % 3]:
            status = get_agent_status(project['id'], agent)
            
            if status['status'] == 'completed':
                icon = ""
                color = "#4caf50"
            elif status['status'] == 'running':
                icon = "🟡"
                color = "#ff9800"
            elif status['status'] == 'failed':
                icon = "❌"
                color = "#f44336"
            else:
                icon = "⏸"
                color = "#B0B0B0"
            
            st.markdown(f"""
            <div class="agent-card">
                <h3 style="display: flex; align-items: center; gap: 0.5rem;">
                    <span>{icon}</span>
                    <span>{format_agent_name(agent)}</span>
                </h3>
                <p style="color: {color}; font-weight: 600;">{status['status'].title()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if status['status'] == 'running':
                st.progress(status['progress'] / 100)
                st.markdown(f"{status['progress']}%")
            elif status['status'] == 'completed':
                st.progress(1.0)
                # Calculate duration safely
                duration_seconds = status.get('duration_seconds')
                if duration_seconds and isinstance(duration_seconds, (int, float)):
                    st.markdown(f" Completed in {duration_seconds:.1f}s")
                else:
                    st.markdown(" Completed")
            
            if status['status'] in ['queued', 'failed']:
                if st.button(f"Run {format_agent_name(agent)}", key=f"run_{agent}", use_container_width=True):
                    with st.spinner(f"Running {format_agent_name(agent)}..."):
                        execute_agent(project['id'], agent)
                    st.rerun()

# Optimization Phase
with tab4:
    st.markdown("### Optimization Phase")
    st.markdown("Optimize performance, costs, security, and monitoring")
    
    agents = AGENTS_BY_PHASE["Optimization"]
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("▶ Run All Optimization Agents", key="run_all_optimization", use_container_width=True):
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            for idx, agent in enumerate(agents):
                status_placeholder.markdown(f"Running **{format_agent_name(agent)}**...")
                execute_agent(project['id'], agent)
                progress_placeholder.progress((idx + 1) / len(agents))
            
            status_placeholder.success(" Optimization phase complete!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("---")
    
    cols = st.columns(3)
    for idx, agent in enumerate(agents):
        with cols[idx % 3]:
            status = get_agent_status(project['id'], agent)
            
            if status['status'] == 'completed':
                icon = ""
                color = "#4caf50"
            elif status['status'] == 'running':
                icon = "🟡"
                color = "#ff9800"
            elif status['status'] == 'failed':
                icon = "❌"
                color = "#f44336"
            else:
                icon = "⏸"
                color = "#B0B0B0"
            
            st.markdown(f"""
            <div class="agent-card">
                <h3 style="display: flex; align-items: center; gap: 0.5rem;">
                    <span>{icon}</span>
                    <span>{format_agent_name(agent)}</span>
                </h3>
                <p style="color: {color}; font-weight: 600;">{status['status'].title()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if status['status'] == 'running':
                st.progress(status['progress'] / 100)
                st.markdown(f"{status['progress']}%")
            elif status['status'] == 'completed':
                st.progress(1.0)
                # Calculate duration safely
                duration_seconds = status.get('duration_seconds')
                if duration_seconds and isinstance(duration_seconds, (int, float)):
                    st.markdown(f" Completed in {duration_seconds:.1f}s")
                else:
                    st.markdown(" Completed")
            
            if status['status'] in ['queued', 'failed']:
                if st.button(f"Run {format_agent_name(agent)}", key=f"run_{agent}", use_container_width=True):
                    with st.spinner(f"Running {format_agent_name(agent)}..."):
                        execute_agent(project['id'], agent)
                    st.rerun()

# Summary
st.markdown("---")
st.markdown('<h2 class="section-header"> Execution Summary</h2>', unsafe_allow_html=True)

total_agents = sum(len(agents) for agents in AGENTS_BY_PHASE.values())

# Get execution stats from database
all_executions = db.get_project_executions(project['id'])
completed = sum(1 for e in all_executions if e['status'] == 'completed')
running = sum(1 for e in all_executions if e['status'] == 'running')
failed = sum(1 for e in all_executions if e['status'] == 'failed')

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Agents", total_agents)

with col2:
    st.metric("Completed", completed, delta=f"{(completed/total_agents*100):.0f}%")

with col3:
    st.metric("Running", running)

with col4:
    st.metric("Failed", failed)

if completed == total_agents:
    st.success("🎉 All agents completed successfully!")
    st.balloons()
