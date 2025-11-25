"""
Quick Assess - Upload documents and diagrams for automated assessment
"""
import streamlit as st
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agentic_services.ui.unified_theme import apply_unified_theme
from src.agentic_services.utils.quick_assess_client import get_client

# Page config
st.set_page_config(
    page_title="Quick Assess | Nagarro Agentic Services",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply unified theme
apply_unified_theme()

# Import and render unified sidebar navigation
from src.agentic_services.ui.unified_navigation import render_unified_sidebar
render_unified_sidebar()

# Initialize session state
if "qa_assessment_id" not in st.session_state:
    st.session_state.qa_assessment_id = None
if "qa_status" not in st.session_state:
    st.session_state.qa_status = None
if "qa_results" not in st.session_state:
    st.session_state.qa_results = None
if "qa_recent_list" not in st.session_state:
    st.session_state.qa_recent_list = []

# Get API client
client = get_client()

# Professional Header
st.markdown("""
    <div style="background: linear-gradient(135deg, #1A1F3A 0%, #2A2F4A 100%); 
                padding: 2.5rem 2rem; border-radius: 16px; border: 2px solid #2A2F4A; 
                margin-bottom: 2rem; border-left: 6px solid #60c8b1;
                box-shadow: 0 10px 40px rgba(96, 200, 177, 0.2);">
        <h1 style="color: #60c8b1; font-size: 2.5rem; font-weight: 800; margin: 0 0 0.5rem 0;">
            Quick Assess
        </h1>
        <p style="color: #B0B0B0; font-size: 1.1rem; margin: 0; line-height: 1.6;">
            Upload discovery documents and architecture diagrams for automated assessment
        </p>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📤 New Assessment", "📋 Recent Assessments", "📊 History"])

# ============================================================================
# TAB 1: NEW ASSESSMENT
# ============================================================================
with tab1:
    st.markdown('<h2 class="professional-header">Upload Files</h2>', unsafe_allow_html=True)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload documents and diagrams",
        type=["docx", "pdf", "vsdx", "drawio", "xml"],
        accept_multiple_files=True,
        help="Supported formats: Word (.docx), PDF (.pdf), Visio (.vsdx), draw.io (.drawio, .xml). Max 50MB per file."
    )
    
    if uploaded_files:
        st.info(f"✅ {len(uploaded_files)} file(s) selected")
        
        # Show file list
        with st.expander("📄 Selected Files", expanded=True):
            for f in uploaded_files:
                size_mb = len(f.read()) / (1024 * 1024)
                f.seek(0)  # Reset file pointer
                st.write(f"• **{f.name}** ({size_mb:.2f} MB)")
        
        # Execute button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🚀 Execute Assessment", type="primary", use_container_width=True):
                try:
                    with st.spinner("Uploading files..."):
                        # Upload files
                        response = client.upload_files(uploaded_files)
                        assessment_id = response["assessment_id"]
                        st.session_state.qa_assessment_id = assessment_id
                        
                        # Execute workflow
                        execute_response = client.execute_assessment(assessment_id)
                        workflow_id = execute_response.get("workflow_id", "unknown")
                        
                        st.success(f"✅ Assessment started! ID: `{assessment_id}`")
                        st.info("⏳ Processing may take 5-10 minutes. Check the status below.")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Status & Results Section (if assessment is running)
    if st.session_state.qa_assessment_id:
        st.markdown("---")
        st.markdown('<h2 class="professional-header">Assessment Status</h2>', unsafe_allow_html=True)
        
        assessment_id = st.session_state.qa_assessment_id
        
        # Poll for status
        try:
            status_data = client.get_status(assessment_id)
            st.session_state.qa_status = status_data
            
            status = status_data.get("status", "unknown")
            stage = status_data.get("stage", "unknown")
            progress = status_data.get("progress", 0)
            error = status_data.get("error")
            
            # Progress bar
            st.progress(progress / 100)
            
            # Status display
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Status", status.upper(), delta=None)
            with col2:
                st.metric("Stage", stage.replace("_", " ").title(), delta=None)
            
            # Error handling
            if error:
                st.error(f"❌ Error: {error}")
                if st.button("🔄 Retry Assessment"):
                    try:
                        client.execute_assessment(assessment_id)
                        st.success("✅ Retry initiated")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Retry failed: {e}")
            
            # Auto-refresh if processing
            if status == "processing":
                time.sleep(2)
                st.rerun()
            
            # Show results if completed
            if status == "completed":
                st.success("✅ Assessment completed!")
                
                try:
                    results = client.get_results(assessment_id)
                    st.session_state.qa_results = results
                    
                    # Display key metrics
                    analysis = results.get("analysis", {})
                    readiness_score = analysis.get("cloud_readiness_score", 0)
                    
                    st.markdown("---")
                    st.markdown('<h2 class="professional-header">Results</h2>', unsafe_allow_html=True)
                    
                    # Readiness Score
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Cloud Readiness Score", f"{readiness_score}/100", delta=None)
                    
                    # Key Findings
                    key_findings = analysis.get("key_findings", [])
                    if key_findings:
                        st.markdown("### 🔍 Key Findings")
                        for finding in key_findings[:5]:
                            st.write(f"• {finding}")
                    
                    # Download buttons
                    st.markdown("### 📥 Download Report")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        try:
                            pdf_bytes = client.download_report(assessment_id)
                            st.download_button(
                                "📄 Download PDF Report",
                                pdf_bytes,
                                file_name=f"quick-assess-{assessment_id}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"PDF download failed: {e}")
                    
                    with col2:
                        # JSON download
                        import json
                        json_str = json.dumps(results, indent=2)
                        st.download_button(
                            "📊 Download JSON",
                            json_str.encode(),
                            file_name=f"quick-assess-{assessment_id}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    
                except Exception as e:
                    st.error(f"Failed to load results: {e}")
        
        except Exception as e:
            st.error(f"Status check failed: {e}")

# ============================================================================
# TAB 2: RECENT ASSESSMENTS
# ============================================================================
with tab2:
    st.markdown('<h2 class="professional-header">Recent Assessments</h2>', unsafe_allow_html=True)
    
    try:
        response = client.list_assessments(limit=10)
        assessments = response.get("assessments", [])
        
        if not assessments:
            st.info("No assessments yet. Create your first assessment in the 'New Assessment' tab.")
        else:
            for assessment in assessments:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{assessment.get('assessment_id', 'Unknown')}**")
                    
                    with col2:
                        status = assessment.get("status", "unknown")
                        st.write(f"Status: {status}")
                    
                    with col3:
                        upload_time = assessment.get("upload_time", "")
                        if upload_time:
                            try:
                                dt = datetime.fromisoformat(upload_time.replace("Z", "+00:00"))
                                st.write(dt.strftime("%Y-%m-%d %H:%M"))
                            except:
                                st.write(upload_time)
                    
                    with col4:
                        if st.button("View", key=f"view_{assessment.get('assessment_id')}"):
                            st.session_state.qa_assessment_id = assessment.get("assessment_id")
                            st.session_state.qa_status = None
                            st.session_state.qa_results = None
                            st.switch_page("pages/10_Quick_Assess.py")
                    
                    st.divider()
    
    except Exception as e:
        st.error(f"Failed to load assessments: {e}")

# ============================================================================
# TAB 3: HISTORY
# ============================================================================
with tab3:
    st.markdown('<h2 class="professional-header">Assessment History</h2>', unsafe_allow_html=True)
    
    try:
        response = client.list_assessments(limit=50)
        assessments = response.get("assessments", [])
        
        if not assessments:
            st.info("No assessment history.")
        else:
            # Convert to DataFrame for better display
            import pandas as pd
            
            data = []
            for a in assessments:
                data.append({
                    "Assessment ID": a.get("assessment_id", "")[:20] + "...",
                    "Status": a.get("status", "unknown"),
                    "Upload Time": a.get("upload_time", "")[:19] if a.get("upload_time") else "",
                    "Files": len(a.get("files", [])),
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"Failed to load history: {e}")





