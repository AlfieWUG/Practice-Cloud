#!/bin/bash
# =============================================================================
# Agentic Services - Development Startup Script
# =============================================================================
# Quick startup script to get your development environment ready
# Run this script each morning to ensure everything is properly configured
# =============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "======================================================================"
echo "  🚀 Agentic Services - Development Environment Startup"
echo "======================================================================"
echo ""

# Step 1: Check current directory
if [ ! -f "app_streamlit.py" ]; then
    echo -e "${YELLOW}⚠️  Not in project root. Changing to project directory...${NC}"
    cd /Users/aaldertoosthuizen/Projects/agentic-services
fi

echo -e "${GREEN}✓ Project directory:${NC} $(pwd)"
echo ""

# Step 2: Check Python environment
echo "Checking Python environment..."
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Please create one:${NC}"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not activated. Activating...${NC}"
    source venv/bin/activate
fi

echo -e "${GREEN}✓ Python environment:${NC} $(which python)"
echo -e "${GREEN}✓ Python version:${NC} $(python --version)"
echo ""

# Step 3: Check required dependencies
echo "Checking key dependencies..."
python -c "import streamlit" 2>/dev/null && echo -e "${GREEN}✓ Streamlit installed${NC}" || echo -e "${YELLOW}⚠️  Streamlit not found - run: pip install -r requirements.txt${NC}"
python -c "import pandas" 2>/dev/null && echo -e "${GREEN}✓ Pandas installed${NC}" || echo -e "${YELLOW}⚠️  Pandas not found${NC}"
python -c "import anthropic" 2>/dev/null && echo -e "${GREEN}✓ Anthropic SDK installed${NC}" || echo -e "${YELLOW}⚠️  Anthropic SDK not found${NC}"
echo ""

# Step 4: Check environment variables
echo "Checking environment configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file found${NC}"
    # Check for critical env vars without exposing values
    if grep -q "ANTHROPIC_API_KEY" .env 2>/dev/null; then
        echo -e "${GREEN}✓ ANTHROPIC_API_KEY configured${NC}"
    else
        echo -e "${YELLOW}⚠️  ANTHROPIC_API_KEY not found in .env${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "   Create .env file with required API keys"
fi
echo ""

# Step 5: Check GCP authentication
echo "Checking GCP authentication..."
if command -v gcloud &> /dev/null; then
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || echo "")
    if [ -n "$ACTIVE_ACCOUNT" ]; then
        echo -e "${GREEN}✓ GCP authenticated:${NC} ${ACTIVE_ACCOUNT}"
        CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
        echo -e "${GREEN}✓ GCP project:${NC} ${CURRENT_PROJECT}"
    else
        echo -e "${YELLOW}⚠️  GCP not authenticated. Run: gcloud auth login${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  gcloud CLI not installed${NC}"
fi
echo ""

# Step 6: Show git status
echo "Checking version control status..."
if [ -d ".git" ]; then
    BRANCH=$(git branch --show-current)
    echo -e "${GREEN}✓ Git branch:${NC} ${BRANCH}"
    
    # Check for uncommitted changes
    if [[ -n $(git status -s) ]]; then
        echo -e "${YELLOW}⚠️  You have uncommitted changes:${NC}"
        git status -s | head -5
        if [ $(git status -s | wc -l) -gt 5 ]; then
            echo "   ... and $(( $(git status -s | wc -l) - 5 )) more files"
        fi
    else
        echo -e "${GREEN}✓ Working directory clean${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Not a git repository${NC}"
fi
echo ""

# Step 7: Summary and next steps
echo "======================================================================"
echo -e "  ${GREEN}✅ Startup Complete!${NC}"
echo "======================================================================"
echo ""
echo -e "${BLUE}📋 Quick Reference Commands:${NC}"
echo ""
echo "  🖥️  Start Dashboard (local):"
echo "     streamlit run app_streamlit.py"
echo ""
echo "  🚀 Deploy to GCP Cloud Run:"
echo "     ./deploy-gcp.sh"
echo ""
echo "  🧪 Run tests:"
echo "     pytest tests/"
echo ""
echo "  📊 View current deployment:"
echo "     https://nagarro-agentic-demo-759248510963.europe-west3.run.app"
echo ""
echo "  📁 Project structure:"
echo "     - app_streamlit.py         → Main dashboard entry point"
echo "     - src/agentic_services/    → Core application code"
echo "     - infrastructure/          → Terraform & Lambda code"
echo "     - deploy-gcp.sh            → GCP deployment script"
echo ""
echo -e "${BLUE}📝 Current Work Status:${NC}"
echo "  ✅ Dashboard redesign complete (emoji removal, animations, 3-col grid)"
echo "  ✅ Deployed to GCP Cloud Run"
echo "  ⏸️  AWS Lambda + API Gateway infrastructure ready (not deployed)"
echo ""
echo -e "${BLUE}🔜 Next Steps (for tomorrow):${NC}"
echo "  • Review dashboard performance and user feedback"
echo "  • Consider AWS deployment if needed"
echo "  • Add new agents or enhance existing ones"
echo "  • Additional UX improvements based on usage"
echo ""
echo "======================================================================"
echo ""
