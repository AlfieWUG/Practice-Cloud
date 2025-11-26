"""
Unified Dashboard Theme - All CSS in One Place
Nagarro Colors: Blue (#0A0E27, #1A1F3A, #2A2F4A) and Green (#60c8b1, #4db89f, #7dd3c3)
"""
import streamlit as st

def apply_unified_theme():
    """Apply unified Nagarro theme to all pages"""
    
    st.markdown("""
    <style>
    /* ============================================
       NAGARRO COLOR VARIABLES
       ============================================ */
    :root {
        --nagarro-green: #60c8b1;
        --nagarro-green-dark: #4db89f;
        --nagarro-green-light: #7dd3c3;
        --nagarro-navy: #0A0E27;
        --nagarro-blue-dark: #1A1F3A;
        --nagarro-blue-medium: #2A2F4A;
        --nagarro-text-white: #FFFFFF;
        --nagarro-text-gray: #B0B0B0;
    }
    
    /* ============================================
       GLOBAL APP STYLING
       ============================================ */
    .stApp {
        background: var(--nagarro-navy) !important;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
        background: var(--nagarro-navy) !important;
    }
    
    /* ============================================
       SIDEBAR STYLING - FIXED & ALWAYS VISIBLE
       ============================================ */
    [data-testid="stSidebar"] {
        background: var(--nagarro-navy) !important;
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
        border-right: 1px solid var(--nagarro-blue-medium) !important;
    }
    
    /* Prevent sidebar from collapsing */
    [data-testid="stSidebar"][aria-expanded="false"],
    [data-testid="stSidebar"][aria-expanded="true"] {
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
        transform: translateX(0) !important;
    }
    
    /* Hide sidebar collapse button completely */
    [data-testid="collapsedControl"],
    button[data-testid="collapsedControl"],
    [data-testid="collapsedControl"] button,
    button[aria-label*="Close"],
    button[aria-label*="Open"],
    [data-testid="stSidebar"] button[aria-expanded],
    [data-testid="stSidebar"] [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    
    /* Hide Streamlit's default sidebar navigation */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebar"] nav:not(:has(button)),
    [data-testid="stSidebar"] [data-testid="stSidebarNav"],
    [data-testid="stSidebar"] > div:first-child > nav,
    [data-testid="stSidebar"] > div:first-child > div[data-testid="stSidebarNav"],
    [data-testid="stSidebar"] ul[data-testid="stSidebarNav"],
    [data-testid="stSidebar"] nav ul,
    [data-testid="stSidebar"] nav a,
    [data-testid="stSidebar"] > div > nav,
    [data-testid="stSidebar"] > div > div > nav {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        opacity: 0 !important;
    }
    
    /* Hide Streamlit default sidebar titles */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2:first-child,
    [data-testid="stSidebar"] > div:first-child > h1,
    [data-testid="stSidebar"] > div:first-child > h2,
    [data-testid="stSidebar"] > div:first-child > div:first-child > h1,
    [data-testid="stSidebar"] > div:first-child > div:first-child > h2,
    [data-testid="stSidebar"] > div > div > h1,
    [data-testid="stSidebar"] > div > div > h2 {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        font-size: 0 !important;
        line-height: 0 !important;
    }
    
    /* Hide Streamlit default navigation links */
    [data-testid="stSidebar"] a[href*="pages"],
    [data-testid="stSidebar"] a[href*="Onboarding"],
    [data-testid="stSidebar"] a[href*="Projects"],
    [data-testid="stSidebar"] a[href*="Agent_Execution"],
    [data-testid="stSidebar"] a[href*="Cloud_Credentials"],
    [data-testid="stSidebar"] a[href*="Source_Infrastructure"],
    [data-testid="stSidebar"] a[href*="Source_Code"],
    [data-testid="stSidebar"] a[href*="Target_Configuration"],
    [data-testid="stSidebar"] a[href*="Analytics"],
    [data-testid="stSidebar"] a[href*="Reports"],
    [data-testid="stSidebar"] a[href*=".py"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        opacity: 0 !important;
    }
    
    /* Sidebar text colors */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: var(--nagarro-text-white) !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown * {
        color: var(--nagarro-text-white) !important;
    }
    
    /* ============================================
       TYPOGRAPHY
       ============================================ */
    .stMarkdown, p, span, label, div {
        color: var(--nagarro-text-white) !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--nagarro-text-white) !important;
    }
    
    .page-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--nagarro-green) !important;
        margin-bottom: 1rem;
    }
    
    .section-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--nagarro-green) !important;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* ============================================
       BUTTONS
       ============================================ */
    .stButton > button {
        background: linear-gradient(135deg, var(--nagarro-green) 0%, var(--nagarro-green-dark) 100%);
        color: var(--nagarro-text-white) !important;
        border: none;
        padding: 0.85rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(96, 200, 177, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--nagarro-green-light) 0%, var(--nagarro-green) 100%);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(96, 200, 177, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(96, 200, 177, 0.3);
    }
    
    /* Sidebar button styling */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: transparent;
        border: 1px solid var(--nagarro-blue-medium);
        color: var(--nagarro-text-white) !important;
        text-align: left;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 6px;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--nagarro-blue-dark);
        border-color: var(--nagarro-green);
        transform: translateX(4px);
    }
    
    /* Active button state */
    [data-testid="stSidebar"] .stButton > button.active {
        background: linear-gradient(135deg, var(--nagarro-green) 0%, var(--nagarro-green-dark) 100%);
        border-color: var(--nagarro-green);
        color: var(--nagarro-text-white) !important;
    }
    
    /* ============================================
       CARDS & CONTAINERS
       ============================================ */
    .feature-card,
    .metric-card,
    .widget-card,
    .agent-card {
        background: linear-gradient(135deg, var(--nagarro-blue-dark) 0%, var(--nagarro-blue-medium) 100%);
        border: 2px solid var(--nagarro-blue-medium);
        border-left: 5px solid var(--nagarro-green);
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover,
    .metric-card:hover,
    .widget-card:hover,
    .agent-card:hover {
        border-color: var(--nagarro-green);
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(96, 200, 177, 0.3);
    }
    
    .feature-card h3,
    .agent-card h3 {
        color: var(--nagarro-green) !important;
        margin: 0 0 1rem 0;
    }
    
    .feature-card p,
    .agent-card p {
        color: var(--nagarro-text-gray) !important;
        margin: 0;
        line-height: 1.6;
    }
    
    /* ============================================
       METRICS & STATS
       ============================================ */
    [data-testid="stMetricValue"] {
        color: var(--nagarro-green) !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--nagarro-text-gray) !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: var(--nagarro-green) !important;
    }
    
    /* ============================================
       PROGRESS BARS
       ============================================ */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--nagarro-green) 0%, var(--nagarro-green-light) 100%);
    }
    
    /* ============================================
       ALERTS
       ============================================ */
    .stAlert {
        background: var(--nagarro-blue-dark) !important;
        border: 2px solid var(--nagarro-blue-medium) !important;
        border-left: 5px solid var(--nagarro-green) !important;
        color: var(--nagarro-text-white) !important;
    }
    
    /* ============================================
       TABS
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--nagarro-blue-dark);
        color: var(--nagarro-text-gray) !important;
        border: 2px solid var(--nagarro-blue-medium);
        padding: 1rem 2rem;
        border-radius: 8px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--nagarro-green) 0%, var(--nagarro-green-dark) 100%);
        color: var(--nagarro-text-white) !important;
        border-color: var(--nagarro-green);
    }
    
    /* ============================================
       INPUT FIELDS
       ============================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: var(--nagarro-blue-dark) !important;
        border: 1px solid var(--nagarro-blue-medium) !important;
        color: var(--nagarro-text-white) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--nagarro-green) !important;
    }
    
    /* ============================================
       BADGES & STATUS
       ============================================ */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .badge-active {
        background: var(--nagarro-green);
        color: var(--nagarro-navy);
        font-weight: 700;
    }
    
    /* ============================================
       LOGO CONTAINER
       ============================================ */
    .logo-container {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1.5rem;
    }
    
    .logo-container img {
        max-width: 120px;
        height: auto;
    }
    
    .nav-tagline {
        text-align: center;
        color: var(--nagarro-text-gray);
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    /* ============================================
       SEPARATORS
       ============================================ */
    hr {
        border-color: var(--nagarro-blue-medium) !important;
        margin: 1.5rem 0;
    }
    
    /* ============================================
       EXPANDERS
       ============================================ */
    .streamlit-expanderHeader {
        background: var(--nagarro-blue-dark) !important;
        border: 2px solid var(--nagarro-blue-medium) !important;
        color: var(--nagarro-text-white) !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--nagarro-green) !important;
    }
    
    /* ============================================
       NAVIGATION SPECIFIC STYLING
       ============================================ */
    /* Top navigation stack (Home, All Agents, etc.) */
    div[data-testid="stSidebar"] .top-nav-stack div[data-testid="stButton"] > button {
        border-radius: 10px !important;
        background: #111d2c !important;
        border: 1px solid #27394d !important;
        color: #f4f6fb !important;
        font-size: 0.9rem !important;
        padding-top: 0.4rem !important;
        padding-bottom: 0.4rem !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
        margin: 0.25rem 0 !important;
    }
    
    div[data-testid="stSidebar"] .top-nav-stack div[data-testid="stButton"] > button:hover {
        border-color: #4fd1c5 !important;
        color: #4fd1c5 !important;
        background: #1a2a3a !important;
    }
    
    /* Quick Actions section */
    div[data-testid="stSidebar"] .quick-actions div[data-testid="stButton"] > button {
        background: #1f2a3a !important;
        border: 1px solid #2f4156 !important;
        border-radius: 8px !important;
        width: 100% !important;
        margin: 0.25rem 0 !important;
    }
    
    div[data-testid="stSidebar"] .quick-actions div[data-testid="stButton"] > button:hover {
        background: #2a3a4a !important;
        border-color: var(--nagarro-green) !important;
    }
    
    /* Section header styling in sidebar */
    div[data-testid="stSidebar"] .section-header {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: var(--nagarro-green) !important;
        margin: 1rem 0 0.5rem 0 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    </style>
    
    <script>
    // Continuously hide Streamlit default navigation
    document.addEventListener('DOMContentLoaded', function() {
        function hideDefaultNav() {
            const navElements = document.querySelectorAll('[data-testid="stSidebarNav"], [data-testid="stSidebar"] nav, [data-testid="stSidebar"] ul[data-testid="stSidebarNav"]');
            navElements.forEach(el => {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
                el.style.height = '0';
                el.style.overflow = 'hidden';
            });
            
            const titles = document.querySelectorAll('[data-testid="stSidebar"] h1:first-child, [data-testid="stSidebar"] h2:first-child');
            titles.forEach(el => {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
                el.style.height = '0';
            });
            
            const links = document.querySelectorAll('[data-testid="stSidebar"] a[href*="pages"]');
            links.forEach(el => {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
            });
        }
        
        hideDefaultNav();
        
        const observer = new MutationObserver(function(mutations) {
            hideDefaultNav();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true
        });
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Render chat window in main content area if open
    # This is called AFTER all CSS is applied, so it appears at the top of content
    from agentic_services.ui.chat_widget import render_chat_window
    render_chat_window()

