import streamlit as st
import os

st.set_page_config(
    page_title="Nagarro Agentic Services",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# DARK THEME CSS with NAGARRO GREEN + LOGO
st.markdown("""
<style>
    :root {
        --nagarro-green: #60c8b1;
        --nagarro-green-dark: #4db89f;
        --nagarro-green-light: #7dd3c3;
    }
    
    .stApp {
        background: #0A0E27;
    }
    
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    .stMarkdown, p, span, label, h1, h2, h3 {
        color: #FFFFFF !important;
    }
    
    .page-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #60c8b1 0%, #7dd3c3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .logo-container {
        text-align: center;
        padding: 1rem 0;
        background: #1A1F3A;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    .logo-container img {
        max-width: 180px;
        height: auto;
    }
    
    .nav-tagline {
        text-align: center;
        color: #B0B0B0;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    [data-testid="stMetricValue"] {
        color: #60c8b1 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #B0B0B0 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #60c8b1 !important;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%);
        border: 2px solid #2A2F4A;
        border-left: 5px solid #60c8b1;
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        transition: all 0.3s;
    }
    
    .feature-card:hover {
        border-color: #60c8b1;
        transform: translateX(5px);
        box-shadow: 0 10px 30px rgba(96, 200, 177, 0.3);
    }
    
    .feature-card h3 {
        color: #60c8b1 !important;
        margin: 0 0 1rem 0;
    }
    
    .feature-card p {
        color: #B0B0B0 !important;
        margin: 0;
        line-height: 1.6;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #60c8b1 0%, #4db89f 100%);
        color: white !important;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        margin: 0.5rem 0;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #7dd3c3 0%, #60c8b1 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(96, 200, 177, 0.4);
    }
    
    .stAlert {
        background: #1A1F3A !important;
        border: 2px solid #2A2F4A !important;
        border-left: 5px solid #60c8b1 !important;
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #1A1F3A;
        color: #B0B0B0 !important;
        border: 2px solid #2A2F4A;
        padding: 1rem 2rem;
        border-radius: 8px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #60c8b1 0%, #4db89f 100%);
        color: white !important;
        border-color: #60c8b1;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #60c8b1 0%, #7dd3c3 100%);
    }
    
    hr {
        border-color: #2A2F4A !important;
        margin: 2rem 0;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .badge-active {
        background: #60c8b1;
        color: #0A0E27;
        font-weight: 700;
    }
    
    .streamlit-expanderHeader {
        background: #1A1F3A !important;
        border: 2px solid #2A2F4A !important;
        color: white !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #60c8b1 !important;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%);
        border: 2px solid #2A2F4A;
        border-left: 5px solid #60c8b1;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .agent-card h3 {
        color: #60c8b1 !important;
    }
    
    .professional-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #60c8b1 !important;
        margin: 1.5rem 0 1rem 0;
        padding: 0.5rem 0;
        border-bottom: 2px solid #2A2F4A;
    }
    
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #60c8b1 !important;
        margin: 1rem 0 0.5rem 0;
    }
    
    .nav-button {
        background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%);
        border: 2px solid #2A2F4A;
        border-left: 4px solid #60c8b1;
    }
    
    .nav-button:hover {
        border-color: #60c8b1;
        background: linear-gradient(135deg, #2A2F4A 0%, #3A3F5A 100%);
    }
    
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #60c8b1;
        margin-right: 0.5rem;
    }
    
    .coming-soon-card {
        background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%);
        border: 2px dashed #60c8b1;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .coming-soon-content h3 {
        color: #60c8b1 !important;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .coming-soon-content p {
        color: #B0B0B0 !important;
        font-size: 1rem;
        line-height: 1.6;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Layout
col_nav, col_main = st.columns([1, 3])

# ============================================================================
# LEFT NAVIGATION WITH LOGO
# ============================================================================
with col_nav:
    # Check if logo exists
    logo_path = "assets/images/nagarro_logo.png"
    
    if os.path.exists(logo_path):
        # Display logo
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image(logo_path, use_column_width=True)
        st.markdown('<div class="nav-tagline">Agentic Services Platform</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Fallback to text
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 2.5rem; font-weight: 700; color: #00E676; margin-bottom: 0.5rem;">
                Nagarro
            </div>
            <div style="color: #B0B0B0; font-size: 0.85rem;">
                Agentic Services Platform
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<div class="section-header">Navigation</div>', unsafe_allow_html=True)
    
    if st.button("Home", key="nav_home", use_container_width=True):
        st.session_state.current_page = "Home"
        st.rerun()
    
    if st.button("All Agents", key="nav_agents", use_container_width=True):
        st.session_state.current_page = "Agents"
        st.rerun()
    
    if st.button("Agent Showcase", key="nav_demo", use_container_width=True):
        st.session_state.current_page = "Agent Showcase"
        st.rerun()
    
    if st.button("About", key="nav_about", use_container_width=True):
        st.session_state.current_page = "About"
        st.rerun()
    
    st.markdown("---")
    
    st.markdown('<div class="section-header">System Status</div>', unsafe_allow_html=True)
    st.markdown('<span class="status-badge badge-active"><span class="status-indicator"></span>Online</span>', unsafe_allow_html=True)
    st.markdown("")
    st.markdown("**6** agents active")
    st.markdown("**98%** success rate")

# ============================================================================
# MAIN CONTENT
# ============================================================================
with col_main:
    page = st.session_state.current_page
    
    if page == "Home":
        st.markdown('<h1 class="page-title">Welcome to Nagarro Agentic Services</h1>', unsafe_allow_html=True)
        st.markdown("### AI-Powered Cloud Migration & Modernization Platform")
        
        st.markdown("")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("AI Agents", "6", "All Active")
        with col2:
            st.metric("Migrations", "50+", "Completed")
        with col3:
            st.metric("Success Rate", "98%", "+2%")
        with col4:
            st.metric("Time Saved", "60-80%")
        
        st.markdown("---")
        
        st.markdown('<div class="professional-header">Quick Start</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3>Explore All Agents</h3>
                <p>View all 6 specialized AI agents, their capabilities, and which ones are featured in our demo.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("View All Agents →", key="quick_agents"):
                st.session_state.current_page = "Agents"
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3>Experience Agent Showcase</h3>
                <p>See AI agents plan a real migration with generated artifacts and instant insights.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Open Showcase →", key="quick_demo"):
                st.session_state.current_page = "Agent Showcase"
                st.rerun()
        
        st.markdown("---")
        
        st.markdown('<div class="professional-header">Why Agentic Services?</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3>Speed</h3>
                <p>Complete in days what traditionally takes months. Our AI agents work 24/7 analyzing infrastructure.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3>Accuracy</h3>
                <p>Automated dependency mapping catches what humans miss. 1000+ dependencies tracked automatically.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h3>Quality</h3>
                <p>Professional artifacts generated automatically. Wave plans and strategies ready for stakeholders.</p>
            </div>
            """, unsafe_allow_html=True)
    elif page == "Agents":
        try:
            from pages.agents_overview import render_agents_page
            render_agents_page()
        except Exception as e:
            st.error(f"Error loading agents: {str(e)}")
    
    elif page == "Agent Showcase":
        try:
            from demo.demo_mode import (
                run_demo_discovery,
                run_demo_assessment,
                run_demo_planning,
                run_demo_quick_assess,
            )

            st.markdown('<h1 class="page-title">Agent Showcase</h1>', unsafe_allow_html=True)
            st.markdown("### Watch AI Agents Plan a Real Migration")

            st.info("**Scenario:** Meridian Financial Group | 247 servers → AWS Cloud | $4.2M budget")

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
            st.error(f"Error: {str(e)}")
    
    elif page == "About":
        st.markdown('<h1 class="page-title">About Nagarro Agentic Services</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        ## 🎯 Our Mission
        
        Transform cloud migration from a risky, time-consuming manual process into an intelligent, 
        automated journey powered by specialized AI agents.
        
        ---
        
        ## 🤖 The Platform
        
        Six specialized AI agents work collaboratively:
        
        - **Discovery** → Find everything
        - **Assessment** → Analyze complexity
        - **Planning** → Create strategy
        - **Architecture** → Design target
        - **Transformation** → Modernize code
        - **Testing** → Validate results
        
        ---
        
        ## 📈 Results
        
        - **60-80% faster** migration planning
        - **1000+** dependencies mapped automatically
        - **Professional** artifacts ready for stakeholders
        - **Risk-managed** wave-based approach
        
        ---
        
        ## 🏢 Powered by Nagarro
        
        [Learn more about Nagarro Cloud Services →](https://www.nagarro.com/en/services/cloud)
        """)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: #1A1F3A; border-radius: 12px;">
        <h3 style="color: #00E676; margin: 0;">🚀 Nagarro Agentic Services Platform</h3>
        <p style="color: #B0B0B0;">AI-Powered Migration & Modernization</p>
    </div>
    """, unsafe_allow_html=True)
