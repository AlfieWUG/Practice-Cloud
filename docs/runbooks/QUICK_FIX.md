# Quick Fix for Execute Endpoint 500 Error

## The Problem
The backend is using cached Python code, so it's not picking up the graph fixes.

## The Solution

**Run this command to force a clean restart:**

```bash
cd /Users/aaldertoosthuizen/Projects/agentic-services
./scripts/restart_backend_clean.sh
```

This script will:
1. ✅ Kill any existing backend processes
2. ✅ Clear all Python cache files
3. ✅ Restart the backend with fresh code

## Alternative: Manual Restart

If the script doesn't work, do this manually:

```bash
# 1. Kill existing backend
pkill -f "uvicorn main:app"

# 2. Clear cache
find src -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find onboarding-portal/backend -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true

# 3. Restart
cd /Users/aaldertoosthuizen/Projects/agentic-services
source venv/bin/activate
cd onboarding-portal/backend
export APP_ENV=development SECRET_KEY=some-dev-secret QUICK_ASSESS_API_KEY=demo-key
export DYNAMODB_ENDPOINT=http://localhost:8001 AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_REGION=us-east-1
uvicorn main:app --reload --port 8000
```

## What Was Fixed

1. ✅ LangGraph graph structure (removed parallel edges)
2. ✅ ReportRenderer style conflict
3. ✅ Missing dependencies installed
4. ✅ Better error handling

The graph now builds successfully - you just need a clean restart to pick up the changes.

---

**After restarting, try the execute button again. It should work!** 🚀





