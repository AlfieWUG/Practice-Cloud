#!/bin/bash

# Nagarro Agentic Services - Onboarding Portal Bootstrap Script
# This script creates the complete MVP Phase 1 structure

set -e

echo "🚀 Bootstrap Nagarro Agentic Services Onboarding Portal"
echo "========================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Creating directory structure..."

# Backend structure
mkdir -p backend/app/{api,models,services,schemas}
mkdir -p backend/tests
mkdir -p backend/alembic/versions

# Frontend structure
mkdir -p frontend/src/{pages,components,hooks,services,store,types,utils}
mkdir -p frontend/public

# Deployment
mkdir -p deployment/terraform

echo "✅ Directory structure created"
echo ""

echo "📝 Next steps:"
echo ""
echo "1. Review the README.md for complete documentation"
echo "2. I'll create starter files for:"
echo "   - Backend API (FastAPI)"
echo "   - Frontend app (React + TypeScript)"
echo "   - Docker setup"
echo "   - Database models"
echo ""
echo "3. Once files are ready, run:"
echo "   cd onboarding-portal"
echo "   docker-compose up"
echo ""
echo "✨ Portal structure ready!"
