#!/bin/bash
# =============================================================================
# Lambda Build Script
# =============================================================================
# Creates deployment package and dependencies layer for Lambda functions
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 Building Lambda packages..."
echo "Script directory: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"
echo ""

# -----------------------------------------------------------------------------
# Clean previous builds
# -----------------------------------------------------------------------------
echo "🧹 Cleaning previous builds..."
rm -rf "$SCRIPT_DIR/build"
rm -f "$SCRIPT_DIR/deployment.zip"
rm -f "$SCRIPT_DIR/layer.zip"

mkdir -p "$SCRIPT_DIR/build/deployment"
mkdir -p "$SCRIPT_DIR/build/layer/python"

# -----------------------------------------------------------------------------
# Build Dependencies Layer
# -----------------------------------------------------------------------------
echo ""
echo "📦 Building dependencies layer..."

# Install dependencies to layer directory
pip install \
    boto3 \
    botocore \
    anthropic \
    openai \
    pydantic \
    requests \
    python-dotenv \
    -t "$SCRIPT_DIR/build/layer/python" \
    --upgrade \
    --platform manylinux2014_x86_64 \
    --python-version 3.11 \
    --only-binary=:all:

# Remove unnecessary files to reduce size
cd "$SCRIPT_DIR/build/layer/python"
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true

# Create layer zip
cd "$SCRIPT_DIR/build/layer"
zip -r "$SCRIPT_DIR/layer.zip" . -q

LAYER_SIZE=$(du -h "$SCRIPT_DIR/layer.zip" | cut -f1)
echo "✅ Dependencies layer created: layer.zip ($LAYER_SIZE)"

# -----------------------------------------------------------------------------
# Build Deployment Package
# -----------------------------------------------------------------------------
echo ""
echo "📦 Building deployment package..."

# Copy handler
cp "$SCRIPT_DIR/handler.py" "$SCRIPT_DIR/build/deployment/"

# Copy agent source code
cp -r "$PROJECT_ROOT/src/agentic_services" "$SCRIPT_DIR/build/deployment/"

# Remove test files and cache
cd "$SCRIPT_DIR/build/deployment"
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Create deployment zip
zip -r "$SCRIPT_DIR/deployment.zip" . -q

DEPLOY_SIZE=$(du -h "$SCRIPT_DIR/deployment.zip" | cut -f1)
echo "✅ Deployment package created: deployment.zip ($DEPLOY_SIZE)"

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "✨ Build complete!"
echo ""
echo "📋 Summary:"
echo "  - Layer package: $SCRIPT_DIR/layer.zip ($LAYER_SIZE)"
echo "  - Deployment package: $SCRIPT_DIR/deployment.zip ($DEPLOY_SIZE)"
echo ""
echo "Next steps:"
echo "  1. cd $PROJECT_ROOT/infrastructure/terraform"
echo "  2. terraform init"
echo "  3. terraform plan"
echo "  4. terraform apply"
echo ""
