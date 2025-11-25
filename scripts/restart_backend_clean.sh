#!/usr/bin/env bash
# Force clean restart of backend - kills old processes and clears cache

set -e

PROJECT_ROOT="/Users/aaldertoosthuizen/Projects/agentic-services"
BACKEND_DIR="$PROJECT_ROOT/onboarding-portal/backend"

echo "🔄 Force restarting backend with cache clear..."
echo ""

# Kill any existing uvicorn processes
echo "1. Stopping existing backend processes..."
pkill -f "uvicorn main:app" || echo "   (no processes to kill)"

# Clear Python cache
echo "2. Clearing Python cache..."
find "$PROJECT_ROOT/src" -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find "$PROJECT_ROOT/src" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$BACKEND_DIR" -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find "$BACKEND_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

echo "   ✅ Cache cleared"

# Wait a moment
sleep 1

# Start backend
echo ""
echo "3. Starting backend..."
cd "$PROJECT_ROOT"
source venv/bin/activate
cd "$BACKEND_DIR"

export APP_ENV=development
export SECRET_KEY=some-dev-secret
export QUICK_ASSESS_API_KEY=demo-key
export DYNAMODB_ENDPOINT=http://localhost:8001
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_REGION=us-east-1
export CORS_ORIGINS='["http://localhost:5173","http://localhost:3000","http://localhost:8000","http://localhost:8501"]'

echo "   🌐 Starting FastAPI server on http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000





