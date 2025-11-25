"""
Chat Widget Component - Floating chat button and window
Can be expanded to use LLM in the future
"""
import streamlit as st
import sys
import os

def render_chat_widget():
    """Render chat button in sidebar - called from unified_navigation"""
    
    # Initialize chat state
    if 'chat_open' not in st.session_state:
        st.session_state.chat_open = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Chat button in sidebar (already in sidebar context from unified_navigation)
    # Use a global key that works across all pages
    st.markdown("---")
    if st.button("💬 Help Assistant", key="chat_toggle_global", use_container_width=True):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()


def render_chat_window():
    """Render chat window in main content area when open - SIMPLIFIED VERSION"""
    
    # Only render if chat is open
    if not st.session_state.get('chat_open', False):
        return
    
    # Get current page context
    current_page = _get_current_page_context()
    
    # Import bot service - handle import errors gracefully
    try:
        import sys
        import os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
        from src.agentic_services.bot.bot_service import get_bot_response
    except ImportError as e:
        st.error(f"Error loading bot service: {str(e)}")
        return
    
    # Initialize with welcome message if empty
    if not st.session_state.chat_messages:
        welcome_msg = f"👋 Hi! I'm your migration assistant. I can help you with **{current_page}**. What would you like to know?"
        st.session_state.chat_messages = [{"role": "bot", "content": welcome_msg}]
    
    # Render chat window as an expander at the top of the page
    with st.expander("💬 Help Assistant", expanded=True):
        st.markdown(f'<p style="color: #B0B0B0; font-size: 0.9rem; margin-bottom: 1rem;">Helping with: <strong style="color: #60c8b1;">{current_page}</strong></p>', unsafe_allow_html=True)
        
        # Chat messages container with scrollable area
        messages_container = st.container()
        with messages_container:
            # Show messages
            for idx, msg in enumerate(st.session_state.chat_messages):
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="background: #2A2F4A; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 0.75rem; margin-left: 20%; border-left: 3px solid #60c8b1;">
                        <strong style="color: #60c8b1;">You:</strong> <span style="color: #FFFFFF;">{msg["content"]}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #1A1F3A; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 0.75rem; margin-right: 20%; border-left: 3px solid #60c8b1;">
                        <strong style="color: #60c8b1;">Assistant:</strong> <span style="color: #B0B0B0;">{msg["content"]}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Chat input - use unique keys based on page context
        page_key = current_page.replace(" ", "_").lower()
        user_input = st.text_input(
            "Type your question...", 
            key=f"chat_input_{page_key}", 
            placeholder="Ask me anything about this page...",
            label_visibility="visible"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Send", key=f"chat_send_{page_key}", use_container_width=True):
                if user_input.strip():
                    # Add user message
                    st.session_state.chat_messages.append({"role": "user", "content": user_input.strip()})
                    
                    # Get bot response
                    bot_response = get_bot_response(user_input.strip(), current_page)
                    
                    # Add bot response
                    st.session_state.chat_messages.append({"role": "bot", "content": bot_response})
                    
                    st.rerun()
        
        with col2:
            if st.button("Clear", key=f"chat_clear_{page_key}", use_container_width=True):
                st.session_state.chat_messages = []
                welcome_msg = f"👋 Hi! I'm your migration assistant. I can help you with **{current_page}**. What would you like to know?"
                st.session_state.chat_messages = [{"role": "bot", "content": welcome_msg}]
                st.rerun()


def _get_current_page_context():
    """Detect current page context for the bot - FIXED: Check session state FIRST"""
    import sys
    import os
    
    # PRIORITY 1: Check session state FIRST (most reliable for app_streamlit.py pages)
    current_page = st.session_state.get('current_page', None)
    if current_page:
        page_state_map = {
            "Agents": "Agents",
            "Home": "Home",
            "About": "Home",          # Use Home knowledge base
            "Agent Showcase": "Home"  # Use Home knowledge base
        }
        if current_page in page_state_map:
            return page_state_map[current_page]
        # If it's a direct match in knowledge base, use it
        if current_page in ["Project Onboarding", "Projects", "Agent Execution", 
                           "Cloud Credentials", "Source Infrastructure", "Source Code",
                           "Target Configuration", "Analytics", "Reports"]:
            return current_page
    
    # PRIORITY 2: Check file path (for pages/ directory files)
    current_file = ""
    if len(sys.argv) > 0:
        current_file = sys.argv[0]
    
    # Also check __file__ if available
    try:
        caller_file = os.path.abspath(current_file)
    except:
        caller_file = current_file
    
    # Map file names to page names (knowledge base keys)
    page_map = {
        "1_Onboarding.py": "Project Onboarding",
        "2_Projects.py": "Projects",
        "3_Agent_Execution.py": "Agent Execution",
        "4_Cloud_Credentials.py": "Cloud Credentials",
        "5_Source_Infrastructure.py": "Source Infrastructure",
        "6_Source_Code.py": "Source Code",
        "7_Target_Configuration.py": "Target Configuration",
        "8_Analytics.py": "Analytics",
        "9_Reports.py": "Reports",
        "app_streamlit.py": "Home"  # Default for app_streamlit.py, but session state takes priority
    }
    
    # Check if we're in pages directory (these are separate page files)
    if "pages/" in current_file or "pages/" in str(caller_file):
        # Extract page number from path
        for key, value in page_map.items():
            if key.replace("_", "").replace(".py", "") in current_file.replace("_", "").replace(".py", ""):
                return value
    
    # Check current file path (only if not already matched)
    for key, value in page_map.items():
        if key in current_file or key in caller_file:
            # Only use this if we're actually on that page file, not app_streamlit.py
            if key != "app_streamlit.py" or current_page is None:
                return value
    
    # Last resort - default to Home
    return "Home"

