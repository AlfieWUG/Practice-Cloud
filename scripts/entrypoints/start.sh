#!/bin/bash

# Nagarro Agentic Services Platform - Startup Script
# Usage: ./start.sh

echo "🚀 Starting Nagarro Agentic Services Platform..."
echo ""

# Navigate to project directory
cd /Users/aaldertoosthuizen/Projects/agentic-services

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit not found. Installing..."
    pip install streamlit
fi

# Check if plotly is installed (needed for some visualizations)
echo "🔍 Checking dependencies..."
python -c "import plotly" 2>/dev/null || {
    echo "📦 Installing plotly..."
    pip install plotly
}

echo ""
echo "✅ Environment ready!"
echo ""
echo "🌐 Starting dashboard..."
echo "   URL: http://localhost:8501"
echo ""
echo "📋 Features available:"
echo "   ✅ Main Dashboard"
echo "   ✅ Onboarding (create projects)"
echo "   ✅ Projects (portfolio view)"
echo "   ✅ Agent Execution (24 agents, 4 phases)"
echo "   ✅ Cloud Credentials (AWS setup)"
echo "   ✅ Source Infrastructure (servers, databases)"
echo "   ✅ Source Code (GitHub/GitLab repos)"
echo "   ✅ Target Configuration (AWS landing zone)"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Start Streamlit
streamlit run app_streamlit.py
