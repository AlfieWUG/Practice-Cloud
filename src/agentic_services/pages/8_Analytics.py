"""Analytics Dashboard - Real-time Metrics & Insights"""
import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.nagarro_theme import apply_nagarro_theme
from database import get_db
from auth.auth import DashboardAuth

# Page config
st.set_page_config(
    page_title="Analytics | Nagarro Agentic Services",
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

# Header
st.markdown('<h1 class="page-title">Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #B0B0B0; font-size: 1.1rem; margin-bottom: 2rem;">Real-time insights into agent performance, migrations, and system health</p>', unsafe_allow_html=True)

# Quick refresh
col1, col2 = st.columns([5, 1])
with col2:
    if st.button(" Refresh", use_container_width=True):
        st.rerun()

st.markdown("---")

# ============================================================================
# KEY METRICS OVERVIEW
# ============================================================================

st.markdown('<h2 class="professional-header"> Key Performance Indicators</h2>', unsafe_allow_html=True)

# Get overall statistics
projects = db.get_all_projects()
total_projects = len(projects)
active_projects = sum(1 for p in projects if p['status'] not in ['Completed', 'Failed'])
completed_projects = sum(1 for p in projects if p['status'] == 'Completed')
avg_progress = sum(p['progress'] for p in projects) / total_projects if total_projects > 0 else 0

# Get execution stats
execution_stats = db.get_execution_stats()
total_executions = execution_stats.get('total', 0) or 0
completed_executions = execution_stats.get('completed', 0) or 0
failed_executions = execution_stats.get('failed', 0) or 0
success_rate = (completed_executions / total_executions * 100) if total_executions > 0 else 0
avg_duration = execution_stats.get('avg_duration', 0) or 0

# Display KPI cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Projects",
        total_projects,
        f"{active_projects} active",
        delta_color="off"
    )

with col2:
    st.metric(
        "Agent Executions",
        total_executions,
        f"+{completed_executions}" if completed_executions and completed_executions > 0 else "0",
        delta_color="normal"
    )

with col3:
    st.metric(
        "Success Rate",
        f"{success_rate:.1f}%",
        f"{failed_executions} failed" if failed_executions and failed_executions > 0 else "No failures",
        delta_color="inverse" if failed_executions and failed_executions > 0 else "off"
    )

with col4:
    st.metric(
        "Avg Execution Time",
        f"{avg_duration:.1f}s",
        delta_color="off"
    )

with col5:
    st.metric(
        "Completion Rate",
        f"{avg_progress:.0f}%",
        delta_color="off"
    )

st.markdown("---")

# ============================================================================
# CHARTS AND VISUALIZATIONS
# ============================================================================

# Create two columns for charts
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<h3 class="section-header">Project Status Distribution</h3>', unsafe_allow_html=True)
    
    if projects:
        # Count projects by status
        status_counts = {}
        for p in projects:
            status = p['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Create pie chart
        fig_status = go.Figure(data=[go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            hole=0.4,
            marker=dict(colors=['#60c8b1', '#ff9800', '#4caf50', '#f44336']),
            textinfo='label+percent',
            textfont=dict(color='white', size=14)
        )])
        
        fig_status.update_layout(
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=350,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("No projects yet")

with col_right:
    st.markdown('<h3 class="section-header">Projects by Phase</h3>', unsafe_allow_html=True)
    
    if projects:
        # Count projects by phase
        phase_counts = {}
        for p in projects:
            phase = p['phase']
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        # Create bar chart
        fig_phase = go.Figure(data=[go.Bar(
            x=list(phase_counts.keys()),
            y=list(phase_counts.values()),
            marker=dict(
                color='#60c8b1',
                line=dict(color='#4db89f', width=2)
            ),
            text=list(phase_counts.values()),
            textposition='auto',
        )])
        
        fig_phase.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='#2A2F4A'),
            yaxis=dict(gridcolor='#2A2F4A', title='Number of Projects'),
            height=350,
            margin=dict(l=20, r=20, t=20, b=60)
        )
        
        st.plotly_chart(fig_phase, use_container_width=True)
    else:
        st.info("No projects yet")

st.markdown("---")

# ============================================================================
# AGENT EXECUTION TRENDS
# ============================================================================

st.markdown('<h2 class="professional-header"> Agent Execution Analytics</h2>', unsafe_allow_html=True)

if total_executions > 0:
    # Get all executions across all projects
    all_executions = []
    for project in projects:
        executions = db.get_project_executions(project['id'])
        for exec in executions:
            exec['project_name'] = project['name']
            all_executions.append(exec)
    
    if all_executions:
        # Create DataFrame
        df_exec = pd.DataFrame(all_executions)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h3 class="section-header">Execution Status by Agent</h3>', unsafe_allow_html=True)
            
            # Count by agent and status
            agent_status = df_exec.groupby(['agent_name', 'status']).size().reset_index(name='count')
            
            # Create grouped bar chart
            fig_agent = px.bar(
                agent_status,
                x='agent_name',
                y='count',
                color='status',
                barmode='stack',
                color_discrete_map={
                    'completed': '#4caf50',
                    'running': '#ff9800',
                    'failed': '#f44336',
                    'queued': '#B0B0B0'
                }
            )
            
            fig_agent.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(title='Agent', tickangle=-45, gridcolor='#2A2F4A'),
                yaxis=dict(title='Executions', gridcolor='#2A2F4A'),
                height=400,
                margin=dict(l=20, r=20, t=20, b=100),
                legend=dict(title='Status')
            )
            
            st.plotly_chart(fig_agent, use_container_width=True)
        
        with col2:
            st.markdown('<h3 class="section-header">Top Performing Agents</h3>', unsafe_allow_html=True)
            
            # Calculate success rate per agent
            agent_stats = []
            for agent_name in df_exec['agent_name'].unique():
                agent_execs = df_exec[df_exec['agent_name'] == agent_name]
                total = len(agent_execs)
                completed = len(agent_execs[agent_execs['status'] == 'completed'])
                success_rate = (completed / total * 100) if total > 0 else 0
                
                agent_stats.append({
                    'Agent': agent_name.replace('_', ' ').title(),
                    'Executions': total,
                    'Success Rate': success_rate,
                    'Completed': completed
                })
            
            df_agent_stats = pd.DataFrame(agent_stats).sort_values('Success Rate', ascending=False)
            
            # Display as table with colored metrics
            for idx, row in df_agent_stats.head(10).iterrows():
                success_color = '#4caf50' if row['Success Rate'] >= 90 else '#ff9800' if row['Success Rate'] >= 70 else '#f44336'
                
                st.markdown(f"""
                <div class="agent-card" style="padding: 0.75rem; margin: 0.5rem 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{row['Agent']}</strong><br>
                            <span style="color: #B0B0B0; font-size: 0.85rem;">{row['Executions']} executions</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: {success_color}; font-size: 1.5rem; font-weight: 700;">{row['Success Rate']:.0f}%</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("ℹ No agent executions yet. Start executing agents to see analytics.")

st.markdown("---")

# ============================================================================
# PROJECT PROGRESS TIMELINE
# ============================================================================

st.markdown('<h2 class="professional-header">📅 Project Timeline</h2>', unsafe_allow_html=True)

if projects:
    # Create timeline data
    timeline_data = []
    for p in projects:
        timeline_data.append({
            'Project': p['name'][:30] + '...' if len(p['name']) > 30 else p['name'],
            'Progress': p['progress'],
            'Status': p['status'],
            'Phase': p['phase'],
            'Priority': p.get('priority', 'Medium')
        })
    
    df_timeline = pd.DataFrame(timeline_data).sort_values('Progress', ascending=True)
    
    # Create horizontal bar chart
    fig_timeline = go.Figure()
    
    # Color by status
    status_colors = {
        'Planning': '#2196f3',
        'In Progress': '#ff9800',
        'Completed': '#4caf50',
        'Failed': '#f44336'
    }
    
    for status in df_timeline['Status'].unique():
        df_status = df_timeline[df_timeline['Status'] == status]
        
        fig_timeline.add_trace(go.Bar(
            y=df_status['Project'],
            x=df_status['Progress'],
            name=status,
            orientation='h',
            marker=dict(color=status_colors.get(status, '#B0B0B0')),
            text=[f"{p}%" for p in df_status['Progress']],
            textposition='inside',
        ))
    
    fig_timeline.update_layout(
        barmode='stack',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(title='Progress (%)', gridcolor='#2A2F4A', range=[0, 100]),
        yaxis=dict(title='', gridcolor='#2A2F4A'),
        height=max(300, len(projects) * 40),
        margin=dict(l=20, r=20, t=20, b=60),
        legend=dict(title='Status', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
else:
    st.info("No projects to display")

st.markdown("---")

# ============================================================================
# RECENT ACTIVITY
# ============================================================================

st.markdown('<h2 class="professional-header">📜 Recent Activity</h2>', unsafe_allow_html=True)

recent_activity = db.get_recent_activity(limit=20)

if recent_activity:
    for activity in recent_activity[:10]:
        # Format timestamp - handle different SQLite datetime formats
        try:
            created_at_str = activity.get('created_at', '')
            if not created_at_str:
                time_str = "Unknown"
            else:
                # Try parsing different datetime formats
                try:
                    # SQLite default format: 2024-11-18 14:29:51
                    if ' ' in created_at_str and 'T' not in created_at_str:
                        created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
                    else:
                        # ISO format: 2024-11-18T14:29:51 or 2024-11-18T14:29:51.123456
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    
                    time_ago = (datetime.now() - created_at).total_seconds()
                    
                    if time_ago < 0:
                        time_str = "Just now"
                    elif time_ago < 60:
                        time_str = "Just now"
                    elif time_ago < 3600:
                        time_str = f"{int(time_ago / 60)}m ago"
                    elif time_ago < 86400:
                        time_str = f"{int(time_ago / 3600)}h ago"
                    else:
                        time_str = f"{int(time_ago / 86400)}d ago"
                except (ValueError, AttributeError) as e:
                    # Fallback: just show the raw timestamp
                    time_str = created_at_str[:16] if len(created_at_str) > 16 else created_at_str
        except Exception as e:
            time_str = "Unknown"
        
        # Icon by action type
        action_icons = {
            'project_created': '🆕',
            'agent_executed': '️',
            'artifact_generated': '',
            'project_updated': '✏',
            'execution_completed': '',
            'execution_failed': '❌'
        }
        icon = action_icons.get(activity.get('action_type', ''), '•')
        
        # Get activity description safely
        description = activity.get('action_description', 'Activity performed')
        user_name = activity.get('user_name')
        
        # Use native Streamlit components instead of custom HTML
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                if user_name:
                    st.markdown(f"{icon} **{description}** (by {user_name})")
                else:
                    st.markdown(f"{icon} **{description}**")
            with col2:
                st.markdown(f"*{time_str}*")
            st.markdown("---")
else:
    st.info("No recent activity")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #B0B0B0; font-size: 0.9rem;">
    Last updated: {}<br>
    Refresh page to see latest data
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
