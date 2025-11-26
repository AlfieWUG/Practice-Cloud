"""
Unified Navigation Component - Used by ALL Pages
Consistent sidebar navigation with Nagarro branding
"""
import base64
import os
import streamlit as st

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
    
    # Navigation-specific CSS is now in unified_theme.py for consistency

    nav_links = [
        {"label": "Home", "page": "Home", "target": "app_streamlit.py"},
        {"label": "All Agents", "page": "Agents", "target": "app_streamlit.py"},
        {"label": "Agent Showcase", "page": "Agent Showcase", "target": "app_streamlit.py"},
        {"label": "About", "page": "About", "target": "app_streamlit.py"},
    ]

    quick_actions = [
        {"label": "Start Quick Assess", "target": "pages/10_Quick_Assess.py"},
        {"label": "Create Project", "target": "pages/1_Onboarding.py"},
    ]

    section_config = [
        {
            "title": "📁 Project",
            "expanded": True,
            "items": [
                {"label": "New Projects", "target": "pages/1_Onboarding.py"},
                {"label": "Current Projects", "target": "pages/2_Projects.py"},
            ],
        },
        {
            "title": "📋 Onboarding",
            "items": [
                {"label": "Cloud Credentials", "target": "pages/4_Cloud_Credentials.py"},
                {"label": "Source Infrastructure", "target": "pages/5_Source_Infrastructure.py"},
                {"label": "Source Code", "target": "pages/6_Source_Code.py"},
                {"label": "Target Configuration", "target": "pages/7_Target_Configuration.py"},
            ],
        },
        {
            "title": "⚡ Quick Assess",
            "items": [
                {"label": "Quick Assess", "target": "pages/10_Quick_Assess.py"},
            ],
        },
        {
            "title": "📊 Monitoring",
            "items": [
                {"label": "Analytics", "target": "pages/8_Analytics.py"},
                {"label": "Reports", "target": "pages/9_Reports.py"},
            ],
        },
    ]

    st.session_state.setdefault('current_page', 'Home')

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

        with st.container():
            st.markdown('<div class="top-nav-stack">', unsafe_allow_html=True)
            for link in nav_links:
                if st.button(link["label"], use_container_width=True, key=f"nav_top_{link['label']}"):
                    st.session_state.current_page = link["page"]
                    st.switch_page(link["target"])
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        with st.container():
            st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)
            st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
            for action in quick_actions:
                if st.button(action["label"], use_container_width=True, key=f"quick_{action['label']}"):
                    st.switch_page(action["target"])
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        for section in section_config:
            with st.expander(section["title"], expanded=section.get("expanded", False)):
                for item in section["items"]:
                    key = f"nav_{section['title']}_{item['label']}".replace(" ", "_").lower()
                    if st.button(item["label"], key=key, use_container_width=True):
                        st.switch_page(item["target"])

        st.markdown("---")
        
        # System Status
        st.markdown('<div class="section-header">System Status</div>', unsafe_allow_html=True)
        st.markdown('<span class="status-badge badge-active">● Online</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Help Assistant Chat Widget
        from src.agentic_services.ui.chat_widget import render_chat_widget
        render_chat_widget()

