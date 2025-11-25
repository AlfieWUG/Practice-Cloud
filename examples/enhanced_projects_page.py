"""
Enhanced Projects Page - Example with Premium Components
This shows how to upgrade your existing Projects page with premium components
"""
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from streamlit_option_menu import option_menu

# Page config
st.set_page_config(
    page_title="Projects | Enhanced",
    page_icon="📁",
    layout="wide"
)

# Apply your existing theme
from src.agentic_services.ui.unified_theme import apply_unified_theme
apply_unified_theme()

# Enhanced Navigation with Icons
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Projects", "Agents", "Analytics"],
        icons=["house", "folder", "robot", "graph-up"],
        menu_icon="cast",
        default_index=1,
        orientation="vertical",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#0A0E27",
            },
            "icon": {"color": "#60c8b1", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "color": "#B0B0B0",
                "padding": "12px",
            },
            "nav-link-selected": {
                "background-color": "#60c8b1",
                "color": "#FFFFFF",
            },
        }
    )

# Main content
st.title("📁 Projects - Enhanced Version")

# Sample data (replace with your actual data)
sample_projects = pd.DataFrame({
    'ID': [1, 2, 3],
    'Project Name': ['E-Commerce Migration', 'Data Center Migration', 'Application Modernization'],
    'Status': ['In Progress', 'Planning', 'Completed'],
    'Progress': [65, 20, 100],
    'Created': ['2024-01-15', '2024-02-01', '2023-12-10'],
    'Priority': ['High', 'Medium', 'Low']
})

# BEFORE: Basic Streamlit table
st.subheader("❌ Before: Basic Streamlit Table")
st.dataframe(sample_projects, use_container_width=True)

st.markdown("---")

# AFTER: Professional AgGrid table
st.subheader("✅ After: Professional AgGrid Table")

# Configure grid options
gb = GridOptionsBuilder.from_dataframe(sample_projects)
gb.configure_pagination(enabled=True, paginationPageSize=10)
gb.configure_side_bar()
gb.configure_default_column(
    groupable=True,
    value=True,
    enableRowGroup=True,
    editable=False,
    resizable=True
)
gb.configure_selection('single', use_checkbox=True)
gb.configure_column("Progress", type=["progressBar"], valueGetter="data.Progress")

# Apply Nagarro theme colors
gridOptions = gb.build()
gridOptions['rowStyle'] = {
    'background-color': '#1A1F3A',
    'color': '#FFFFFF'
}

# Display enhanced table
selected_rows = AgGrid(
    sample_projects,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    height=400,
    theme='dark',
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    allow_unsafe_jscode=True,
    custom_css={
        ".ag-theme-alpine-dark": {
            "--ag-background-color": "#0A0E27",
            "--ag-header-background-color": "#1A1F3A",
            "--ag-odd-row-background-color": "#1A1F3A",
            "--ag-row-hover-color": "#2A2F4A",
            "--ag-selected-row-background-color": "#60c8b1",
            "--ag-header-foreground-color": "#60c8b1",
            "--ag-foreground-color": "#FFFFFF",
        }
    }
)

# Show selected row
if selected_rows['selected_rows']:
    st.info(f"Selected: {selected_rows['selected_rows'][0]['Project Name']}")

st.markdown("---")

# Enhanced Charts (using Plotly - you already have this!)
st.subheader("📊 Enhanced Charts with Plotly")

import plotly.express as px

# Create professional chart
fig = px.bar(
    sample_projects,
    x='Project Name',
    y='Progress',
    title="Project Progress Overview",
    color='Progress',
    color_continuous_scale=['#1A1F3A', '#60c8b1'],
    template="plotly_dark"
)

# Apply Nagarro theme
fig.update_layout(
    plot_bgcolor='#1A1F3A',
    paper_bgcolor='#0A0E27',
    font_color='#FFFFFF',
    title_font_color='#60c8b1',
    xaxis_title="Project",
    yaxis_title="Progress (%)"
)

st.plotly_chart(fig, use_container_width=True)






