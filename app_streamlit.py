"""
Nagarro Agentic Services - Main Dashboard
Uses unified theme and navigation for consistency
"""
import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Page configuration
st.set_page_config(
    page_title="Nagarro Agentic Services - AIMS",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication - DISABLED FOR TESTING
# from agentic_services.auth import DashboardAuth
# auth = DashboardAuth()
# auth.require_auth()

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"
if 'current_section' not in st.session_state:
    st.session_state.current_section = None

# Apply unified theme (all CSS in one place)
from agentic_services.ui.unified_theme import apply_unified_theme
apply_unified_theme()

# Render unified navigation (same for all pages)
from agentic_services.ui.unified_navigation import render_unified_sidebar
render_unified_sidebar()

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

page = st.session_state.current_page

if page == "Home":
    # Professional Hero Section
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%); 
                    padding: 4rem 2rem; border-radius: 16px; border: 2px solid #2A2F4A; 
                    margin-bottom: 2.5rem; text-align: center; border-left: 6px solid #60c8b1;
                    box-shadow: 0 10px 40px rgba(96, 200, 177, 0.2);">
            <h1 style="color: #60c8b1; font-size: 3rem; font-weight: 900; margin: 0 0 1rem 0; 
                       background: linear-gradient(135deg, #60c8b1 0%, #7dd3c3 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;">
                Nagarro Agentic Services
            </h1>
            <p style="color: #B0B0B0; font-size: 1.3rem; margin: 0 0 1.5rem 0; line-height: 1.8; font-weight: 300;">
                AI-Powered Cloud Migration & Modernization Platform
            </p>
            <p style="color: #60c8b1; font-size: 1.1rem; margin: 0; font-weight: 500;">
                Transform your cloud journey with 24 intelligent agents
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Stats Section with Better Styling
    st.markdown("""
        <style>
        .metric-container {
            background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 2px solid #2A2F4A;
            border-left: 4px solid #60c8b1;
            transition: all 0.3s ease;
        }
        .metric-container:hover {
            border-color: #60c8b1;
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(96, 200, 177, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("AI Agents", "24", "100% Complete", delta_color="normal")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Active Projects", "0", "0", delta_color="off")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Completed Migrations", "0", "0", delta_color="off")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Total Savings", "$0", "0%", delta_color="off")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Professional Quick Actions
    st.markdown('<h2 class="section-header" style="margin-top: 2rem;">Quick Actions</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #B0B0B0; margin-bottom: 2rem; font-size: 1.1rem;">Begin your intelligent automation journey</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card" style="cursor: pointer; transition: all 0.3s ease;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: linear-gradient(135deg, #60c8b1 0%, #4db89f 100%); 
                                width: 60px; height: 60px; border-radius: 12px; 
                                display: flex; align-items: center; justify-content: center; 
                                box-shadow: 0 4px 15px rgba(96, 200, 177, 0.4);">
                        <div style="width: 30px; height: 30px; border: 3px solid white; border-radius: 4px;"></div>
                    </div>
                    <h3 style="color: #60c8b1; margin: 0; font-size: 1.5rem;">Create New Project</h3>
                </div>
                <p style="color: #B0B0B0; line-height: 1.6; margin: 0;">
                    Start a new cloud migration project and get started with AI-powered agents. 
                    Configure your infrastructure, set up credentials, and begin your journey.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Create Project", key="home_create_project", use_container_width=True, 
                     type="primary"):
            st.switch_page("pages/1_Onboarding.py")
    
    with col2:
        st.markdown("""
            <div class="feature-card" style="cursor: pointer; transition: all 0.3s ease;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: linear-gradient(135deg, #60c8b1 0%, #4db89f 100%); 
                                width: 60px; height: 60px; border-radius: 12px; 
                                display: flex; align-items: center; justify-content: center; 
                                box-shadow: 0 4px 15px rgba(96, 200, 177, 0.4);">
                        <div style="width: 30px; height: 30px; border: 3px solid white; border-radius: 50%;"></div>
                    </div>
                    <h3 style="color: #60c8b1; margin: 0; font-size: 1.5rem;">Quick Assess</h3>
                </div>
                <p style="color: #B0B0B0; line-height: 1.6; margin: 0;">
                    Upload documents and diagrams for instant automated assessment. 
                    Get cloud readiness scores and infrastructure analysis in minutes.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Start Assessment", key="home_quick_assess", use_container_width=True, 
                     type="primary"):
            st.switch_page("pages/10_Quick_Assess.py")
    
    with col3:
        st.markdown("""
            <div class="feature-card" style="cursor: pointer; transition: all 0.3s ease;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: linear-gradient(135deg, #60c8b1 0%, #4db89f 100%); 
                                width: 60px; height: 60px; border-radius: 12px; 
                                display: flex; align-items: center; justify-content: center; 
                                box-shadow: 0 4px 15px rgba(96, 200, 177, 0.4);">
                        <div style="width: 30px; height: 30px; border: 3px solid white; border-radius: 50%; position: relative;">
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 20px; height: 20px; background: white; border-radius: 50%;"></div>
                        </div>
                    </div>
                    <h3 style="color: #60c8b1; margin: 0; font-size: 1.5rem;">Explore All Agents</h3>
                </div>
                <p style="color: #B0B0B0; line-height: 1.6; margin: 0;">
                    Discover our complete portfolio of 24 specialized agents organized by 
                    Migration, FinOps, and AIOps focus areas. See what each agent can do.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("View All Agents", key="home_view_agents", use_container_width=True, 
                     type="primary"):
            st.session_state.current_page = "Agents"
            st.rerun()
    
    # Quick Assess Recent Assessments Widget
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">Recent Quick Assessments</h2>', unsafe_allow_html=True)
    
    try:
        from src.agentic_services.utils.quick_assess_client import get_client
        client = get_client()
        response = client.list_assessments(limit=3)
        assessments = response.get("assessments", [])
        
        if assessments:
            col1, col2, col3 = st.columns(3)
            for idx, assessment in enumerate(assessments[:3]):
                with [col1, col2, col3][idx]:
                    with st.container():
                        st.markdown(f"""
                            <div class="feature-card" style="padding: 1.5rem;">
                                <h4 style="color: #60c8b1; margin: 0 0 0.5rem 0;">{assessment.get('assessment_id', 'Unknown')[:20]}...</h4>
                                <p style="color: #B0B0B0; font-size: 0.9rem; margin: 0 0 0.5rem 0;">
                                    Status: <strong>{assessment.get('status', 'unknown')}</strong>
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("View Details", key=f"qa_widget_{assessment.get('assessment_id')}", use_container_width=True):
                            st.session_state.qa_assessment_id = assessment.get("assessment_id")
                            st.switch_page("pages/10_Quick_Assess.py")
        else:
            st.info("No recent assessments. Start your first Quick Assess in the 'Quick Assess' page.")
    except Exception as e:
        st.warning(f"Could not load recent assessments: {e}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Professional Features Section
    st.markdown('<h2 class="section-header">Intelligent Automation at Scale</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #B0B0B0; margin-bottom: 2rem; font-size: 1.1rem;">Three powerful focus areas for complete cloud transformation</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card" style="height: 100%; transition: all 0.3s ease;">
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <div style="background: linear-gradient(135deg, #60c8b1 0%, #4db89f 100%); 
                                width: 80px; height: 80px; border-radius: 16px; 
                                display: inline-flex; align-items: center; justify-content: center; 
                                margin-bottom: 1rem;
                                box-shadow: 0 6px 20px rgba(96, 200, 177, 0.4);">
                        <div style="width: 40px; height: 40px; border: 4px solid white; border-radius: 8px; transform: rotate(45deg);"></div>
                    </div>
                </div>
                <h3 style="color: #60c8b1; text-align: center; margin-bottom: 1rem; font-size: 1.4rem;">Migration Agents</h3>
                <p style="color: #B0B0B0; line-height: 1.7; text-align: center; margin: 0;">
                    Automated cloud migration with zero-downtime strategies and intelligent 
                    resource optimization. 12 specialized agents for end-to-end migration.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card" style="height: 100%; transition: all 0.3s ease;">
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <div style="background: linear-gradient(135deg, #60c8b1 0%, #4db89f 100%); 
                                width: 80px; height: 80px; border-radius: 16px; 
                                display: inline-flex; align-items: center; justify-content: center; 
                                margin-bottom: 1rem;
                                box-shadow: 0 6px 20px rgba(96, 200, 177, 0.4);">
                        <div style="width: 0; height: 0; border-left: 20px solid transparent; border-right: 20px solid transparent; border-bottom: 35px solid white;"></div>
                    </div>
                </div>
                <h3 style="color: #60c8b1; text-align: center; margin-bottom: 1rem; font-size: 1.4rem;">FinOps Agents</h3>
                <p style="color: #B0B0B0; line-height: 1.7; text-align: center; margin: 0;">
                    Cost optimization, budget management, and financial governance across 
                    your cloud infrastructure. 5 agents for complete cost control.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="feature-card" style="height: 100%; transition: all 0.3s ease;">
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <div style="background: linear-gradient(135deg, #60c8b1 0%, #4db89f 100%); 
                                width: 80px; height: 80px; border-radius: 16px; 
                                display: inline-flex; align-items: center; justify-content: center; 
                                margin-bottom: 1rem;
                                box-shadow: 0 6px 20px rgba(96, 200, 177, 0.4);">
                        <div style="width: 40px; height: 40px; border: 4px solid white; border-radius: 50%; position: relative;">
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 20px; height: 20px; background: white; border-radius: 50%;"></div>
                        </div>
                    </div>
                </div>
                <h3 style="color: #60c8b1; text-align: center; margin-bottom: 1rem; font-size: 1.4rem;">AIOps Agents</h3>
                <p style="color: #B0B0B0; line-height: 1.7; text-align: center; margin: 0;">
                    Proactive monitoring, incident management, and automated remediation 
                    for cloud operations. 7 agents for intelligent operations.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Add a visual separator with style
    st.markdown("""
        <div style="margin: 3rem 0; text-align: center;">
            <div style="height: 2px; background: linear-gradient(90deg, transparent, #60c8b1, transparent); 
                        margin: 2rem 0;"></div>
        </div>
    """, unsafe_allow_html=True)

elif page == "Agents":
    from agentic_services.pages.agents_overview import render_agents_page
    render_agents_page()

elif page == "Agent Showcase":
    try:
        from demo.demo_mode import (
            run_demo_discovery,
            run_demo_assessment,
            run_demo_planning,
            run_demo_quick_assess,
        )
        from demo.demo_data import DEMO_SCENARIO
        
        st.markdown('<h1 class="page-title">Agent Showcase</h1>', unsafe_allow_html=True)
        st.markdown("### Watch AI Agents Plan a Real Migration")
        
        # Demo Scenario Info
        st.info(f"""
        **Scenario:** {DEMO_SCENARIO['company']} | 
        {DEMO_SCENARIO['current_environment']['servers']} servers → {DEMO_SCENARIO['target']} | 
        {DEMO_SCENARIO['budget']} budget
        """)
        
        st.markdown('<div class="section-header">Featured Agents: Discovery, Assessment, Planning, Quick Assess</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["Discovery Agent", "Assessment Agent", "Planning & Artifacts", "Quick Assess"])
        
        with tab1:
            st.markdown("**Discovery Agent** scans infrastructure and maps dependencies")
            run_demo_discovery()
        
        with tab2:
            st.markdown("**Assessment Agent** analyzes cloud readiness")
            run_demo_assessment()
        
        with tab3:
            st.markdown("**Planning Agent** creates wave plans and generates artifacts")
            run_demo_planning()
        
        with tab4:
            st.markdown("**Quick Assess** ingests documents/diagrams for instant insights")
            run_demo_quick_assess()
    except Exception as e:
        st.error(f"Error loading demo: {str(e)}")
        st.markdown('<h1 class="page-title">Agent Showcase</h1>', unsafe_allow_html=True)
        st.markdown("""
            <div class="feature-card">
                <h3>Interactive Agent Demo</h3>
                <p>Experience our AI agents in action with real-time demonstrations of cloud migration workflows.</p>
                <p style="color: #ff6b6b; margin-top: 1rem;">⚠️ Demo module not available. Error: """ + str(e) + """</p>
            </div>
        """, unsafe_allow_html=True)

elif page == "About":
    st.markdown('<h1 class="page-title">About</h1>', unsafe_allow_html=True)
    st.markdown("""
        <div class="feature-card">
            <h3>Nagarro Agentic Services</h3>
            <p>An AI-powered platform for intelligent cloud migration and modernization, featuring 24 specialized agents.</p>
        </div>
    """, unsafe_allow_html=True)
