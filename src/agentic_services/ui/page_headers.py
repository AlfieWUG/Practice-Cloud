"""
Professional Page Headers - Consistent styling across all pages
"""
import streamlit as st

def render_professional_header(title: str, subtitle: str = None):
    """
    Render a professional header section consistent with Home page design
    
    Args:
        title: Main page title
        subtitle: Optional subtitle/description
    """
    subtitle_html = f'<p style="color: #B0B0B0; font-size: 1.1rem; margin: 0; line-height: 1.6;">{subtitle}</p>' if subtitle else ''
    
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%); 
                    padding: 2.5rem 2rem; border-radius: 16px; border: 2px solid #2A2F4A; 
                    margin-bottom: 2rem; border-left: 6px solid #60c8b1;
                    box-shadow: 0 10px 40px rgba(96, 200, 177, 0.2);">
            <h1 style="color: #60c8b1; font-size: 2.5rem; font-weight: 800; margin: 0 0 0.5rem 0;">
                {title}
            </h1>
            {subtitle_html}
        </div>
    """, unsafe_allow_html=True)






