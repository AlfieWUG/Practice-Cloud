"""
Unified Navigation Component - Used by ALL Pages
Consistent sidebar navigation with Nagarro branding
"""
import streamlit as st
import os
import base64
import sys

def get_logo_base64():
    """Load Nagarro logo as base64 for embedding"""
    logo_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'assets', 'images', 'nagarro_logo.png')
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

def render_unified_sidebar():
    """
    Render unified sidebar navigation - used by ALL pages
    Structure:
    - Nagarro Logo
    - Navigation (Home, Agent Showcase, About)
    - Project (New Projects, Current Projects)
    - Onboarding (Cloud Credentials, Source Infrastructure, Source Code, Target Configuration)
    - Monitoring (Analytics, Reports)
    """
    
    # Get current page from session state or query params
    current_page = st.session_state.get('current_page', 'Home')
    
    # Load logo
    logo_b64 = get_logo_base64()
    
    # Logo Section
    with st.sidebar:
        if logo_b64:
            st.markdown(f"""
            <div class="logo-container">
                <img src="data:image/png;base64,{logo_b64}" alt="Nagarro" />
                <div class="nav-tagline">Agentic Services</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="logo-container">
                <div style="font-size: 1.8rem; font-weight: 700; color: #60c8b1; margin-bottom: 0.5rem;">
                    Nagarro
                </div>
                <div class="nav-tagline">Agentic Services</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation Section
        st.markdown('<div class="section-header">Navigation</div>', unsafe_allow_html=True)
        
        # Navigation buttons - always switch to main app
        if st.button("Home", key="nav_home", use_container_width=True):
            st.session_state.current_page = "Home"
            st.switch_page("app_streamlit.py")
        
        if st.button("All Agents", key="nav_agents", use_container_width=True):
            st.session_state.current_page = "Agents"
            st.switch_page("app_streamlit.py")
        
        if st.button("About", key="nav_about", use_container_width=True):
            st.session_state.current_page = "About"
            st.switch_page("app_streamlit.py")
        
        if st.button("Agent Showcase", key="nav_demo", use_container_width=True):
            st.session_state.current_page = "Agent Showcase"
            st.switch_page("app_streamlit.py")
        
        st.markdown("---")
        
        # Project Section
        st.markdown('<div class="section-header">📁 Project</div>', unsafe_allow_html=True)
        
        if st.button("New Projects", key="nav_new_projects", use_container_width=True):
            st.switch_page("pages/1_Onboarding.py")
        
        if st.button("Current Projects", key="nav_current_projects", use_container_width=True):
            st.switch_page("pages/2_Projects.py")
        
        st.markdown("---")
        
        # Onboarding Section
        st.markdown('<div class="section-header">📋 Onboarding</div>', unsafe_allow_html=True)
        
        if st.button("Cloud Credentials", key="nav_cloud_credentials", use_container_width=True):
            st.switch_page("pages/4_Cloud_Credentials.py")
        
        if st.button("Source Infrastructure", key="nav_source_infrastructure", use_container_width=True):
            st.switch_page("pages/5_Source_Infrastructure.py")
        
        if st.button("Source Code", key="nav_source_code", use_container_width=True):
            st.switch_page("pages/6_Source_Code.py")
        
        if st.button("Target Configuration", key="nav_target_config", use_container_width=True):
            st.switch_page("pages/7_Target_Configuration.py")
        
        st.markdown("---")
        
        # Quick Assess Section
        st.markdown('<div class="section-header">⚡ Quick Assess</div>', unsafe_allow_html=True)
        
        if st.button("Quick Assess", key="nav_quick_assess", use_container_width=True):
            st.switch_page("pages/10_Quick_Assess.py")
        
        st.markdown("---")
        
        # Monitoring Section
        st.markdown('<div class="section-header">📊 Monitoring</div>', unsafe_allow_html=True)
        
        if st.button("Analytics", key="nav_analytics", use_container_width=True):
            st.switch_page("pages/8_Analytics.py")
        
        if st.button("Reports", key="nav_reports", use_container_width=True):
            st.switch_page("pages/9_Reports.py")
        
        st.markdown("---")
        
        # System Status
        st.markdown('<div class="section-header">System Status</div>', unsafe_allow_html=True)
        st.markdown('<span class="status-badge badge-active">● Online</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Help Assistant Chat Widget
        from src.agentic_services.ui.chat_widget import render_chat_widget
        render_chat_widget()

