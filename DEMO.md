# 🚀 Nagarro Agentic Services - Demo Guide

Quick guide for running client demonstrations.

## Quick Start

Run this single command from the project directory:

```bash
./start_demo.sh
```

That's it! The script will:
- ✅ Check/create virtual environment
- ✅ Install dependencies if needed
- ✅ Verify .env configuration
- ✅ Launch the Streamlit dashboard

## What to Show Clients

### 1. Home Dashboard
- Overview of the 24 AI agents
- Platform capabilities and features
- System status and metrics

### 2. Create New Project (Onboarding)
- Walk through the multi-step project setup
- Show the AI-powered requirements analysis
- Demonstrate project configuration options

### 3. Projects View
- View all migration projects
- Filter and search capabilities
- Project details with connected pages:
  - ☁️ Cloud Credentials
  - 🏗️ Source Infrastructure
  - 💻 Source Code
  - 🎯 Target Configuration

### 4. Agent Execution
- Select and run specific agents
- Real-time execution monitoring
- Agent orchestration workflow

### 5. Analytics & Reports
- Project metrics and insights
- Cost optimization data
- Performance analytics

## Demo Mode

The system runs in **DEMO_MODE=true** by default, which means:
- ✅ No AWS credentials required
- ✅ Uses mock data for demonstrations
- ✅ All features work locally
- ✅ Safe for client presentations

## Stopping the Demo

Press `Ctrl+C` in the terminal to stop the Streamlit server.

## Troubleshooting

### Port Already in Use
If port 8501 is busy, Streamlit will automatically use 8502, 8503, etc.

### Missing Dependencies
Run:
```bash
source venv/bin/activate
pip install -e ".[dev]"
```

### Environment Issues
Ensure `.env` file exists with:
```
DEMO_MODE=true
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=NagarroMUC@2025!
```

## Pre-Demo Checklist

- [ ] Run `./start_demo.sh` 5 minutes before the call
- [ ] Verify login works with demo credentials
- [ ] Test navigation between key pages
- [ ] Have example project ready to create
- [ ] Close unnecessary browser tabs/applications
- [ ] Check internet connection (for video calls)

## Questions?

Contact the development team for support.
