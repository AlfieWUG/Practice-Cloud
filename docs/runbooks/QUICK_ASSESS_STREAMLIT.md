# Quick Assess - Streamlit Integration Guide

## ✅ What's Been Added

1. **Quick Assess Page** (`pages/10_Quick_Assess.py`)
   - Full workflow: Upload → Execute → Status → Results
   - Three tabs: New Assessment, Recent Assessments, History

2. **Navigation Menu** (Updated `src/agentic_services/ui/unified_navigation.py`)
   - Added "Quick Assess" button in sidebar under "⚡ Quick Assess" section

3. **Dashboard Widgets** (Updated `app_streamlit.py`)
   - "Start Assessment" button in Quick Actions
   - "Recent Quick Assessments" widget on home page

4. **API Client** (`src/agentic_services/utils/quick_assess_client.py`)
   - Handles all backend API calls

5. **Startup Script** (`scripts/start_backend.sh`)
   - One-command backend startup

---

## 🚀 How to Start Everything

### Step 1: Start DynamoDB Local (if not already running)
```bash
docker run -p 8001:8000 amazon/dynamodb-local
```
Leave this running in one terminal.

### Step 2: Start FastAPI Backend
```bash
cd /Users/aaldertoosthuizen/Projects/agentic-services
./scripts/start_backend.sh
```
Or manually:
```bash
cd /Users/aaldertoosthuizen/Projects/agentic-services
source venv/bin/activate
cd onboarding-portal/backend
export APP_ENV=development SECRET_KEY=some-dev-secret QUICK_ASSESS_API_KEY=demo-key
export DYNAMODB_ENDPOINT=http://localhost:8001 AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_REGION=us-east-1
uvicorn main:app --reload --port 8000
```

### Step 3: Start Streamlit Dashboard
```bash
cd /Users/aaldertoosthuizen/Projects/agentic-services
source venv/bin/activate
streamlit run app_streamlit.py
```

The dashboard will open at **http://localhost:8501**

---

## 📍 Where to Find Quick Assess

1. **In the Sidebar**: Look for "⚡ Quick Assess" section → Click "Quick Assess"
2. **On Home Page**: Click "Start Assessment" button in Quick Actions
3. **Direct URL**: Navigate to the page manually (Streamlit will show it in sidebar automatically)

---

## 🧪 Testing Quick Assess

1. **Upload Files**:
   - Go to Quick Assess page
   - Click "New Assessment" tab
   - Upload test files (.docx, .pdf, .vsdx, .drawio, .xml)
   - Click "🚀 Execute Assessment"

2. **Monitor Status**:
   - Watch progress bar update
   - See current stage (ingestion → parsing → analysis → report)

3. **View Results**:
   - When status shows "completed"
   - See Cloud Readiness Score
   - View key findings
   - Download PDF report
   - Download JSON results

4. **Check History**:
   - Go to "Recent Assessments" tab
   - See list of all assessments
   - Click "View" to see details

---

## ⚠️ Troubleshooting

### "Quick Assess" not showing in navigation
- Make sure you've restarted Streamlit after the changes
- Check that `pages/10_Quick_Assess.py` exists
- Verify `src/agentic_services/ui/unified_navigation.py` was updated

### Backend connection errors
- Make sure FastAPI is running on port 8000
- Check that DynamoDB Local is running on port 8001
- Verify environment variables are set correctly

### Import errors
```bash
pip install -e .
```

### DynamoDB tables missing
If you see "ResourceNotFoundException", create the tables:
```bash
aws dynamodb create-table \
  --endpoint-url http://localhost:8001 \
  --table-name agentic-services-quick-assess \
  --attribute-definitions AttributeName=assessment_id,AttributeType=S \
  --key-schema AttributeName=assessment_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws dynamodb create-table \
  --endpoint-url http://localhost:8001 \
  --table-name agentic-services-quick-assess-errors \
  --attribute-definitions AttributeName=assessment_id,AttributeType=S \
  --key-schema AttributeName=assessment_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

---

## 📝 Files Changed/Created

- ✅ `pages/10_Quick_Assess.py` - Main Quick Assess page
- ✅ `src/agentic_services/utils/quick_assess_client.py` - API client
- ✅ `src/agentic_services/ui/unified_navigation.py` - Added Quick Assess menu item
- ✅ `app_streamlit.py` - Added Quick Assess widgets to home page
- ✅ `scripts/start_backend.sh` - Backend startup script
- ✅ `QUICK_ASSESS_STREAMLIT.md` - This guide

---

**Status**: ✅ Ready to use!  
**Access**: http://localhost:8501 → Sidebar → "⚡ Quick Assess" → "Quick Assess"





