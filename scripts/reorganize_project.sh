#!/bin/bash
# Script to reorganize agentic-services project to proper Python package structure

set -e

echo "🚀 Reorganizing Nagarro Agentic Services Platform..."

# Create src/agentic_services directory structure
mkdir -p src/agentic_services/{agents,orchestrator,tools,ui,config}
mkdir -p tests/{agents,orchestrator,tools,unit,integration,fixtures}
mkdir -p infrastructure/{terraform,cdk}
mkdir -p scripts/{deployment,utils}
mkdir -p data

# Move existing code to src/
echo "📦 Moving existing code to src/agentic_services/..."

# Move agents
if [ -f "agents/__init__.py" ]; then
    cp -r agents/* src/agentic_services/agents/ 2>/dev/null || true
fi

# Move orchestrator
if [ -f "orchestrator/__init__.py" ]; then
    cp -r orchestrator/* src/agentic_services/orchestrator/ 2>/dev/null || true
fi

# Move tools
if [ -f "tools/__init__.py" ]; then
    cp -r tools/* src/agentic_services/tools/ 2>/dev/null || true
fi

# Move UI
if [ -f "ui/__init__.py" ]; then
    cp -r ui/* src/agentic_services/ui/ 2>/dev/null || true
fi

# Move config
if [ -f "config/__init__.py" ]; then
    cp -r config/* src/agentic_services/config/ 2>/dev/null || true
fi

# Move pages to src
if [ -d "pages" ]; then
    cp -r pages src/agentic_services/ 2>/dev/null || true
fi

# Move main app
if [ -f "app_streamlit.py" ]; then
    cp app_streamlit.py src/agentic_services/
fi

# Create __init__.py files
echo "📝 Creating __init__.py files..."
touch src/agentic_services/__init__.py
touch src/agentic_services/agents/__init__.py
touch src/agentic_services/orchestrator/__init__.py
touch src/agentic_services/tools/__init__.py
touch src/agentic_services/ui/__init__.py
touch src/agentic_services/config/__init__.py
touch src/agentic_services/pages/__init__.py
touch tests/__init__.py
touch tests/agents/__init__.py
touch tests/orchestrator/__init__.py
touch tests/tools/__init__.py

# Create .gitkeep for empty directories
touch data/.gitkeep
touch logs/.gitkeep

# Create test configuration files
echo "🧪 Creating test configuration..."
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --cov=src/agentic_services
    --cov-report=html
    --cov-report=term-missing
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
EOF

# Create conftest.py for pytest
cat > tests/conftest.py << 'EOF'
"""Pytest configuration and fixtures"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def mock_aws_credentials(monkeypatch):
    """Mock AWS credentials for testing"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_REGION", "eu-central-1")

@pytest.fixture
def mock_bedrock_response():
    """Mock AWS Bedrock response"""
    return {
        "content": [{
            "text": "Mocked AI response"
        }]
    }
EOF

echo "✅ Project reorganization complete!"
echo ""
echo "Next steps:"
echo "1. Review the new structure in src/"
echo "2. Update import statements in your code"
echo "3. Run: pip install -e \".[dev]\""
echo "4. Run tests: pytest"
