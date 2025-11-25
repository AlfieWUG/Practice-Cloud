# Dashboard Features - Quick Start Guide

## 🎉 What's New

We've added **persistent storage** and a powerful **Analytics Dashboard** to the Nagarro Agentic Services platform!

### ✨ Key Features:
- ✅ **SQLite Database** - Your data now persists across sessions
- ✅ **Analytics Dashboard** - Real-time insights with beautiful charts
- ✅ **Activity Tracking** - Full audit trail of all actions
- ✅ **Performance Metrics** - Track agent execution success rates

---

## ⚡ Quick Assess Upload API (AIMS)

The new **Quick Assess** workflow (AIMS Step 1) lets solution teams upload discovery documents directly from the dashboard. The backend FastAPI service now exposes an async-safe endpoint that streams files to Amazon S3 and tracks uploads in DynamoDB so LangGraph agents can pick them up later.

**Endpoint**

- `POST /api/v1/quick-assess/uploads`
- Body: `multipart/form-data` with one or more `files` (supports `.docx`, `.pdf`, `.vsdx`, `.drawio`, `.xml`)
- Limits: max 10 files per request, **50 MB** per file (enforced server-side)

**What happens under the hood**

1. Each request gets a unique `assessment_id` (e.g., `qa-a12bc34d...`)
2. Files are validated for type/size and streamed to the `S3_QUICK_ASSESS_BUCKET` bucket under `quick-assess/{assessment_id}/`
3. Metadata (`assessment_id`, filenames, sizes, status, upload timestamp) is persisted to `DYNAMODB_QUICK_ASSESS_TABLE`
4. The API responds with the `assessment_id` plus details for each stored document

**Example request**

```bash
ASSESS_API="http://localhost:8000/api/v1/quick-assess/uploads"
curl -X POST "$ASSESS_API" \
     -F "files=@/path/to/CurrentState.vsdx" \
     -F "files=@/path/to/AppInventory.xlsx"
```

**Example response**

```json
{
  "assessment_id": "qa-5b8b0caf94804f05b1d96e0f045f2059",
  "status": "uploaded",
  "files": [
    {
      "filename": "CurrentState.vsdx",
      "size_bytes": 481920,
      "s3_key": "quick-assess/qa-5b8b0caf94804f05b1d96e0f045f2059/CurrentState.vsdx"
    }
  ]
}
```

> 💡 **Errors**:  
> - 400 for invalid file types  
> - 413 when a file exceeds 50 MB  
> - 502 if S3 upload fails  
> - 503 if DynamoDB write fails

Frontend can store the returned `assessment_id` and immediately show success states while LangGraph agents orchestrate downstream processing.

---

## 🚀 Getting Started

### 1. Install/Update Dependencies

No new dependencies needed! Everything required is already in `requirements.txt`:
- `plotly` - For interactive charts
- `pandas` - For data manipulation

If you need to reinstall:
```bash
pip install -e ".[dev]"
```

### 2. Run the Application

```bash
cd /Users/aaldertoosthuizen/Projects/agentic-services
streamlit run app_streamlit.py
```

### 3. Explore New Features

#### Navigate to Analytics
1. From the home page, look for the new **"Analytics & Reports"** section in the left navigation
2. Click **"📈 Analytics"**
3. Explore the dashboard!

---

## 📊 Analytics Dashboard Features

### Key Metrics (Top Row):
- **Total Projects** - All migration projects created
- **Agent Executions** - Total agent runs across all projects
- **Success Rate** - Percentage of successful agent executions
- **Avg Execution Time** - Average time per agent
- **Completion Rate** - Overall project progress

### Charts:

#### 1. **Project Status Distribution** (Donut Chart)
- Visual breakdown of projects by status
- Planning / In Progress / Completed / Failed

#### 2. **Projects by Phase** (Bar Chart)
- Count of projects in each migration phase
- Discovery / Assessment / Execution / Optimization

#### 3. **Execution Status by Agent** (Stacked Bar)
- Shows which agents have been executed
- Color-coded by status (completed, running, failed, queued)

#### 4. **Top Performing Agents** (Score Cards)
- Success rate for each agent
- Ranked by performance
- Shows execution count

#### 5. **Project Progress Timeline** (Horizontal Bar)
- Visual timeline of all projects
- Progress percentage for each
- Color-coded by status

#### 6. **Recent Activity** (Feed)
- Last 20 activities across all projects
- Time-ago formatting (e.g., "2h ago")
- Icons by activity type

---

## 💾 Database Overview

### Location:
Your data is stored in: `/Users/aaldertoosthuizen/Projects/agentic-services/data/agentic_services.db`

This file is **gitignored** so your local data won't be committed to version control.

### What's Stored:
1. **Projects** - All project metadata
2. **Agent Executions** - Every agent run with status, timing, results
3. **Artifacts** - Generated migration plans, diagrams, configs (coming soon)
4. **Notifications** - System alerts (coming soon)
5. **Checklist Items** - Readiness tracking (coming soon)
6. **Cost Tracking** - Budget and spend data (coming soon)
7. **Activity Log** - Full audit trail

### Benefits:
- ✅ **Persistent** - Data survives app restarts
- ✅ **Fast** - SQLite is blazing fast for < 100GB data
- ✅ **Portable** - Single file, easy to backup
- ✅ **No Setup** - Zero configuration needed

---

## 🔄 Migrating Existing Data

If you had projects in `st.session_state` before:

### Option 1: Automatic (Recommended)
We'll build a migration script soon that will:
- Detect old session state data
- Import into new database
- Preserve all project information

### Option 2: Manual Recreation
For now, you can:
1. Note down your existing project details
2. Use **📋 Onboarding** page to recreate them
3. Re-execute agents as needed

**Note**: Session state data is cleared on browser refresh, so there's likely nothing to migrate.

---

## 🎯 Using the Analytics Dashboard

### Example Workflow:

#### Create Test Projects:
```
1. Go to: 📋 Onboarding
2. Create 3 test projects:
   - "E-Commerce Migration" (Priority: High, Timeline: 3-6 months)
   - "Database Modernization" (Priority: Medium, Timeline: 1-3 months)
   - "API Gateway Migration" (Priority: Low, Timeline: 6-12 months)
```

#### Execute Some Agents:
```
1. Go to: 📁 Projects
2. Select a project
3. Go to: ⚙️ Agent Execution
4. Run Discovery agents
5. Check "Run All Discovery Agents"
```

#### View Analytics:
```
1. Go to: 📈 Analytics
2. See your projects in charts
3. View execution metrics
4. Check activity feed
```

#### Refresh Data:
```
- Click "🔄 Refresh" button in top-right
- Or refresh browser (F5)
```

---

## 🧪 Testing the Database

### Quick Test Script:

```python
# Create a test file: test_db.py
from src.agentic_services.database import get_db

# Get database instance
db = get_db()

# Create a test project
project_data = {
    'name': 'Test Migration Project',
    'description': 'Testing the new database',
    'requirements': 'Test requirements',
    'timeline': '1-3 months',
    'priority': 'High',
    'budget': '$100K - $500K',
    'complexity': 'Moderate',
    'status': 'Planning',
    'phase': 'Discovery',
    'progress': 0
}

project_id = db.create_project(project_data)
print(f"✅ Created project with ID: {project_id}")

# Get all projects
projects = db.get_all_projects()
print(f"📊 Total projects: {len(projects)}")

# Get recent activity
activity = db.get_recent_activity(limit=5)
print(f"📜 Recent activity items: {len(activity)}")
```

Run it:
```bash
python test_db.py
```

---

## 🐛 Troubleshooting

### Database Not Creating

**Problem**: `data/agentic_services.db` doesn't exist

**Solution**:
```bash
# Ensure directory exists
mkdir -p data

# Run the app once
streamlit run app_streamlit.py

# Database will be created automatically on first run
```

---

### Analytics Page Empty

**Problem**: Charts show "No projects yet"

**Solution**:
1. Create at least one project via **📋 Onboarding**
2. Execute at least one agent via **⚙️ Agent Execution**
3. Go back to **📈 Analytics** and click **🔄 Refresh**

---

### Charts Not Loading

**Problem**: Plotly charts not rendering

**Solution**:
```bash
# Reinstall plotly
pip uninstall plotly
pip install plotly==5.18.0

# Clear Streamlit cache
streamlit cache clear

# Restart the app
```

---

### Permission Issues

**Problem**: `PermissionError: [Errno 13] Permission denied: 'data/agentic_services.db'`

**Solution**:
```bash
# Fix permissions
chmod 755 data/
chmod 644 data/agentic_services.db

# If still having issues, try different location
export DB_PATH="$HOME/agentic_services.db"
streamlit run app_streamlit.py
```

---

## 📚 Next Steps

### Coming Soon (Phase 2):
1. **📊 Reports & Artifacts Hub**
   - Download migration plans
   - View generated diagrams
   - Export to PDF/Word

2. **✅ Migration Readiness Checklist**
   - Pre-migration checklist
   - Readiness score (0-100%)
   - Blocker identification

### Want to Contribute?
Check out `DASHBOARD_ROADMAP.md` for the full feature list and timeline!

---

## 🆘 Getting Help

### Issues?
1. Check `DASHBOARD_ROADMAP.md` for known issues
2. Review error messages in terminal
3. Check Streamlit logs in `.streamlit/logs/`

### Questions?
- Check code comments in `src/agentic_services/database/db_manager.py`
- Review example usage in `pages/8_📈_Analytics.py`

---

## 🎨 Customization

### Change Database Location:
```python
# In your code:
from src.agentic_services.database import DatabaseManager

db = DatabaseManager(db_path="/custom/path/mydb.db")
```

### Add Custom Metrics:
Edit `pages/8_📈_Analytics.py` and add your own Plotly charts!

Example:
```python
import plotly.graph_objects as go

# Create custom chart
fig = go.Figure(data=[go.Bar(x=..., y=...)])
fig.update_layout(...)
st.plotly_chart(fig, use_container_width=True)
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Database file exists at `data/agentic_services.db`
- [ ] Can create a new project via Onboarding
- [ ] Project appears in **📁 Projects** page
- [ ] Can execute agents in **⚙️ Agent Execution**
- [ ] Analytics dashboard shows data in **📈 Analytics**
- [ ] Activity feed shows project creation
- [ ] Charts render correctly (no blank charts)
- [ ] Refresh button works
- [ ] Page loads in < 2 seconds

---

## 🎉 Success!

You now have:
- ✅ Persistent data storage
- ✅ Professional analytics dashboard
- ✅ Full audit trail
- ✅ Foundation for advanced features

**Enjoy the new features!** 🚀

---

**Version**: 1.0
**Last Updated**: 2025-11-18
**Status**: Production Ready ✅
