import streamlit as st
import time
import pandas as pd

def run_demo_discovery():
    """Discovery demo"""
    from demo.demo_data import DISCOVERY_RESULTS
    
    st.subheader("Discovery Agent - Live Infrastructure Scan")
    
    progress_bar = st.progress(0)
    status = st.empty()
    
    steps = [
        ("Connecting to datacenter...", 15),
        ("Scanning network topology...", 30),
        ("Discovering VMs and servers...", 50),
        ("Mapping applications...", 70),
        ("Analyzing dependencies...", 85),
        ("Generating reports...", 100)
    ]
    
    for step, prog in steps:
        status.text(step)
        progress_bar.progress(prog)
        time.sleep(0.8)
    
    status.text("✓ Discovery complete!")
    time.sleep(0.3)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Servers", DISCOVERY_RESULTS['summary']['total_servers'])
    with col2:
        st.metric("Applications", DISCOVERY_RESULTS['summary']['applications'])
    with col3:
        st.metric("Databases", DISCOVERY_RESULTS['summary']['databases'])
    with col4:
        st.metric("Dependencies", DISCOVERY_RESULTS['summary']['dependencies_mapped'])
    
    st.success("✓ Discovered and mapped 1,847 dependencies automatically!")
    
    with st.expander("Sample Applications"):
        df = pd.DataFrame(DISCOVERY_RESULTS['application_portfolio'])
        st.dataframe(df, use_container_width=True)

def run_demo_assessment():
    """Assessment demo"""
    from demo.demo_data import ASSESSMENT_RESULTS
    
    st.subheader("Assessment Agent - Cloud Readiness Analysis")
    
    progress_bar = st.progress(0)
    status = st.empty()
    
    steps = [
        ("Analyzing complexity...", 25),
        ("Calculating readiness...", 50),
        ("Estimating costs...", 75),
        ("Generating recommendations...", 100)
    ]
    
    for step, prog in steps:
        status.text(step)
        progress_bar.progress(prog)
        time.sleep(0.7)
    
    status.text("✓ Assessment complete!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Readiness", f"{ASSESSMENT_RESULTS['cloud_readiness_score']}/100", "Good")
    with col2:
        st.metric("Timeline", "9 months")
    with col3:
        st.metric("Year 3 Savings", "$2.1M/year")
    
    st.success("✓ 156 applications analyzed and categorized!")
    
    with st.expander("Migration Strategies"):
        import plotly.graph_objects as go
        
        fig = go.Figure(data=[go.Pie(
            labels=list(ASSESSMENT_RESULTS['migration_strategies'].keys()),
            values=list(ASSESSMENT_RESULTS['migration_strategies'].values()),
            hole=.3,
            marker=dict(colors=['#FF6600', '#FF8533', '#FFA366', '#FFCC99'])
        )])
        fig.update_layout(title="6Rs Strategy Distribution")
        st.plotly_chart(fig, use_container_width=True)

def run_demo_planning():
    """Planning demo"""
    from demo.demo_data import WAVE_PLAN
    from demo.artifact_generator import generate_wave_plan_artifact, generate_strategy_document
    
    st.subheader("Planning Agent - Wave Plan Generation")
    
    progress_bar = st.progress(0)
    status = st.empty()
    
    steps = [
        ("Analyzing dependencies...", 20),
        ("Sequencing applications...", 40),
        ("Creating waves...", 60),
        ("Planning rollbacks...", 80),
        ("Generating artifacts...", 100)
    ]
    
    for step, prog in steps:
        status.text(step)
        progress_bar.progress(prog)
        time.sleep(0.7)
    
    status.text("✓ Planning complete!")
    
    st.success(f"✓ Created {WAVE_PLAN['total_waves']}-wave plan over {WAVE_PLAN['timeline']}!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Waves", WAVE_PLAN['total_waves'])
    with col2:
        st.metric("Timeline", WAVE_PLAN['timeline'])
    with col3:
        st.metric("Approach", "Risk-Managed")
    
    with st.expander("Wave Details"):
        df = pd.DataFrame([
            {
                "Wave": f"W{w['wave']}: {w['name']}",
                "Duration": w['duration'],
                "Apps": len(w['apps']),
                "Servers": w['servers'],
                "Risk": w['risk']
            }
            for w in WAVE_PLAN['waves']
        ])
        st.dataframe(df, use_container_width=True)
    
    st.divider()
    st.subheader("Generated Artifacts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generate Wave Plan", use_container_width=True, type="primary"):
            with st.spinner("Creating document..."):
                time.sleep(1)
                filename, content = generate_wave_plan_artifact()
                st.success("✓ Wave Plan created!")
                
                st.download_button(
                    label="Download Wave Plan",
                    data=content,
                    file_name="Nagarro_Wave_Plan.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                
                with st.expander("Preview"):
                    st.markdown(content[:1500] + "\n\n*...preview truncated*")
    
    with col2:
        if st.button("Generate Strategy", use_container_width=True, type="primary"):
            with st.spinner("Creating document..."):
                time.sleep(1)
                filename, content = generate_strategy_document()
                st.success("✓ Strategy created!")
                
                st.download_button(
                    label="Download Strategy",
                    data=content,
                    file_name="Nagarro_Migration_Strategy.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                
                with st.expander("Preview"):
                    st.markdown(content[:1500] + "\n\n*...preview truncated*")


def run_demo_quick_assess():
    """Quick Assess demo"""
    from demo.demo_data import QUICK_ASSESS_FILES, QUICK_ASSESS_RESULTS
    import plotly.express as px

    st.subheader("Quick Assess – Document & Diagram Intelligence")

    upload_col, status_col = st.columns([3, 2])

    with upload_col:
        st.caption("Uploaded Evidence")
        df = pd.DataFrame(QUICK_ASSESS_FILES)
        st.dataframe(
            df.rename(columns={"filename": "Filename", "type": "Type", "size_mb": "Size (MB)", "status": "Status"}),
            hide_index=True,
            use_container_width=True,
        )

    with status_col:
        st.caption("Workflow Timeline")
        steps = [
            ("Uploading documents…", 15),
            ("Parsing text & diagrams…", 45),
            ("Detecting entities…", 65),
            ("Running environment analysis…", 85),
            ("Generating report…", 100),
        ]
        progress_bar = st.progress(0)
        status = st.empty()
        for text, pct in steps:
            status.info(text)
            progress_bar.progress(pct)
            time.sleep(0.7)
        status.success("✓ Assessment complete")

    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Cloud Readiness", f"{QUICK_ASSESS_RESULTS['cloud_readiness_score']}/100")
    with col2:
        st.metric("Documents", QUICK_ASSESS_RESULTS["summary"]["documents_processed"])
    with col3:
        st.metric("Diagrams", QUICK_ASSESS_RESULTS["summary"]["diagrams_parsed"])
    with col4:
        st.metric("Entities", QUICK_ASSESS_RESULTS["summary"]["entities_detected"])

    st.success("✓ Insights ready in under 8 minutes with AI-powered parsing.")

    risk_fig = px.bar(
        x=list(QUICK_ASSESS_RESULTS["risks"].keys()),
        y=list(QUICK_ASSESS_RESULTS["risks"].values()),
        labels={"x": "Risk Area", "y": "Findings"},
        title="Risk Hotspots Identified",
        color=list(QUICK_ASSESS_RESULTS["risks"].values()),
        color_continuous_scale="Reds",
    )
    st.plotly_chart(risk_fig, use_container_width=True)

    tech_col, rec_col = st.columns(2)
    with tech_col:
        st.markdown("#### Technology Stack Snapshot")
        st.markdown(
            """
            - **Languages:** {langs}
            - **Frameworks:** {frameworks}
            - **Databases:** {dbs}
            - **Platforms:** {platforms}
            """.format(
                langs=", ".join(QUICK_ASSESS_RESULTS["technology_stack"]["languages"]),
                frameworks=", ".join(QUICK_ASSESS_RESULTS["technology_stack"]["frameworks"]),
                dbs=", ".join(QUICK_ASSESS_RESULTS["technology_stack"]["databases"]),
                platforms=", ".join(QUICK_ASSESS_RESULTS["technology_stack"]["platforms"]),
            )
        )
    with rec_col:
        st.markdown("#### Top Recommendations")
        for rec in QUICK_ASSESS_RESULTS["recommendations"]:
            st.markdown(f"- {rec}")

    with st.expander("View JSON output"):
        st.json(QUICK_ASSESS_RESULTS, expanded=False)
