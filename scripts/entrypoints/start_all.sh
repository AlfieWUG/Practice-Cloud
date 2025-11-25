#!/usr/bin/env bash
# Nagarro Agentic Services - Complete Startup Script
# Starts DynamoDB Local, FastAPI Backend, and Streamlit Dashboard

set -e

PROJECT_ROOT="/Users/aaldertoosthuizen/Projects/agentic-services"
BACKEND_DIR="$PROJECT_ROOT/onboarding-portal/backend"
VENV_DIR="$PROJECT_ROOT/venv"
DYNAMODB_PORT=8001
BACKEND_PORT=8000
STREAMLIT_PORT=8501

echo "🚀 Starting Nagarro Agentic Services Platform..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in the right directory
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Error: Backend directory not found"
    echo "   Please run this script from: $PROJECT_ROOT"
    exit 1
fi

# Check for virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "   Please create it first: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# ============================================================================
# STEP 1: Start DynamoDB Local
# ============================================================================
echo ""
echo "📊 Step 1: Starting DynamoDB Local..."

# Check if DynamoDB Local is already running
if curl -s http://localhost:$DYNAMODB_PORT > /dev/null 2>&1; then
    echo "   ✅ DynamoDB Local already running on port $DYNAMODB_PORT"
else
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        echo "   ⚠️  Docker not found. Skipping DynamoDB Local."
        echo "   ⚠️  Install Docker or start DynamoDB Local manually:"
        echo "      docker run -p $DYNAMODB_PORT:8000 amazon/dynamodb-local"
        DYNAMODB_RUNNING=false
    else
        echo "   🐳 Starting DynamoDB Local container..."
        docker run -d -p $DYNAMODB_PORT:8000 --name dynamodb-local amazon/dynamodb-local > /dev/null 2>&1 || {
            # Container might already exist, try to start it
            docker start dynamodb-local > /dev/null 2>&1 || {
                echo "   ⚠️  Could not start DynamoDB Local. Continuing anyway..."
                DYNAMODB_RUNNING=false
            }
        }
        sleep 2
        if curl -s http://localhost:$DYNAMODB_PORT > /dev/null 2>&1; then
            echo "   ✅ DynamoDB Local started on port $DYNAMODB_PORT"
            DYNAMODB_RUNNING=true
        else
            echo "   ⚠️  DynamoDB Local failed to start. Continuing anyway..."
            DYNAMODB_RUNNING=false
        fi
    fi
fi

    # Create tables if DynamoDB is running
    if [ "$DYNAMODB_RUNNING" != "false" ]; then
        echo "   📋 Creating DynamoDB tables..."
        export DYNAMODB_ENDPOINT=http://localhost:$DYNAMODB_PORT
        python3 "$PROJECT_ROOT/scripts/create_dynamodb_tables.py" || echo "   ⚠️  Could not create tables (might already exist)"
    fi

# ============================================================================
# STEP 2: Start FastAPI Backend
# ============================================================================
echo ""
echo "🔧 Step 2: Starting FastAPI Backend..."

# Check if backend is already running
if curl -s http://localhost:$BACKEND_PORT/docs > /dev/null 2>&1; then
    echo "   ✅ Backend already running on port $BACKEND_PORT"
else
    # Kill any existing backend processes first
    pkill -f "uvicorn main:app" 2>/dev/null || true
    sleep 1
    
    # Clear Python cache
    echo "   🧹 Clearing Python cache..."
    find "$PROJECT_ROOT/src" -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
    find "$BACKEND_DIR" -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
    
    # Set environment variables
    export APP_ENV=development
    export SECRET_KEY=some-dev-secret
    export QUICK_ASSESS_API_KEY=demo-key
    export DYNAMODB_ENDPOINT=http://localhost:$DYNAMODB_PORT
    export AWS_ACCESS_KEY_ID=test
    export AWS_SECRET_ACCESS_KEY=test
    export AWS_REGION=us-east-1
    export CORS_ORIGINS='["http://localhost:5173","http://localhost:3000","http://localhost:8000","http://localhost:8501"]'
    
    cd "$BACKEND_DIR"
    
    echo "   🌐 Starting FastAPI server on http://localhost:$BACKEND_PORT"
    echo "   📝 API docs will be available at http://localhost:$BACKEND_PORT/docs"
    
    # Start backend in background
    uvicorn main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    echo "   ⏳ Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:$BACKEND_PORT/docs > /dev/null 2>&1; then
            echo "   ✅ Backend started successfully (PID: $BACKEND_PID)"
            break
        fi
        sleep 1
    done
    
    if [ $i -eq 30 ]; then
        echo "   ⚠️  Backend might not have started. Check /tmp/backend.log"
        echo "   Last 10 lines of log:"
        tail -10 /tmp/backend.log 2>/dev/null || echo "   (no log file)"
    fi
    
    cd "$PROJECT_ROOT"
fi

# ============================================================================
# STEP 3: Start Streamlit Dashboard
# ============================================================================
echo ""
echo "📊 Step 3: Starting Streamlit Dashboard..."

# Check if Streamlit is already running
if curl -s http://localhost:$STREAMLIT_PORT > /dev/null 2>&1; then
    echo "   ✅ Streamlit already running on port $STREAMLIT_PORT"
else
    echo "   🌐 Starting Streamlit on http://localhost:$STREAMLIT_PORT"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ All services starting!"
    echo ""
    echo "📍 Access Points:"
    echo "   • Streamlit Dashboard: http://localhost:$STREAMLIT_PORT"
    echo "   • FastAPI Backend:     http://localhost:$BACKEND_PORT"
    echo "   • API Documentation:   http://localhost:$BACKEND_PORT/docs"
    echo "   • DynamoDB Local:      http://localhost:$DYNAMODB_PORT"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Start Streamlit (this will block)
    streamlit run app_streamlit.py --server.port $STREAMLIT_PORT --server.headless false
fi

