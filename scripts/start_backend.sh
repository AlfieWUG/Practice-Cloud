#!/usr/bin/env bash
# Quick Assess Backend Startup Script
set -e
PROJECT_ROOT="/Users/aaldertoosthuizen/Projects/agentic-services"
BACKEND_DIR="$PROJECT_ROOT/onboarding-portal/backend"
VENV_DIR="$PROJECT_ROOT/venv"
echo "🚀 Starting Quick Assess Backend..."
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Error: Backend directory not found"
    exit 1
fi
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Error: Virtual environment not found"
    exit 1
fi
source "$VENV_DIR/bin/activate"
export APP_ENV=development
export SECRET_KEY=some-dev-secret
export QUICK_ASSESS_API_KEY=demo-key
export DYNAMODB_ENDPOINT=http://localhost:8001
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_REGION=us-east-1
export CORS_ORIGINS='["http://localhost:5173","http://localhost:3000","http://localhost:8000","http://localhost:8501"]'
cd "$BACKEND_DIR"
echo "🌐 Starting FastAPI server on http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000




