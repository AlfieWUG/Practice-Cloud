#!/bin/bash

# Local Setup Script (No Docker Required)
# This script sets up the portal to run locally for demo/testing

echo "🚀 Nagarro Agentic Services Portal - Local Setup"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Python version: $(python3 --version)"
echo "✅ Node.js version: $(node --version)"
echo ""

# Setup Backend
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "  Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "  Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "  Creating .env file..."
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update .env with SQLite and demo mode
    cat > .env << EOF
APP_NAME="Nagarro Agentic Services Portal"
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

API_V1_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Using SQLite for local development (no PostgreSQL needed)
DATABASE_URL=sqlite:///./agentic_portal.db

SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS Configuration (not needed in demo mode)
AWS_REGION=eu-central-1

# Demo Mode (no AWS required)
DEMO_MODE=true

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
EOF
fi

echo "✅ Backend setup complete!"
cd ..

# Setup Frontend
echo ""
echo "📦 Setting up Frontend..."
cd frontend

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo "  Installing Node.js dependencies (this may take a few minutes)..."
    npm install --silent
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "  Creating .env file..."
    cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_ENV=development
EOF
fi

echo "✅ Frontend setup complete!"
cd ..

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "To start the portal:"
echo "  1. Backend:  ./start-backend.sh"
echo "  2. Frontend: ./start-frontend.sh"
echo ""
echo "Or run both: ./start-all.sh"
echo ""
