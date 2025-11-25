#!/bin/bash
# =============================================================================
# Deploy Agentic Services Dashboard to GCP Cloud Run
# =============================================================================

set -e

# Configuration
PROJECT_ID="nagarro-agentic-demo-475806"
SERVICE_NAME="nagarro-agentic-demo"
REGION="europe-west3"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "======================================================================"
echo "  Deploying Agentic Services Dashboard to GCP Cloud Run"
echo "======================================================================"
echo ""
echo "Project ID: ${PROJECT_ID}"
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo ""

# Step 1: Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✓ gcloud CLI found"

# Step 2: Check authentication
echo ""
echo "Checking GCP authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "⚠️  Not authenticated. Running gcloud auth login..."
    gcloud auth login
fi

ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
echo "✓ Authenticated as: ${ACTIVE_ACCOUNT}"

# Step 3: Set project
echo ""
echo "Setting GCP project..."
gcloud config set project ${PROJECT_ID}
echo "✓ Project set to: ${PROJECT_ID}"

# Step 4: Enable required APIs (if not already enabled)
echo ""
echo "Ensuring required APIs are enabled..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
echo "✓ APIs enabled"

# Step 5: Build Docker image
echo ""
echo "======================================================================"
echo "  Building Docker image..."
echo "======================================================================"
echo ""
gcloud builds submit --tag ${IMAGE_NAME}:latest --timeout=20m

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Docker image built successfully"
else
    echo ""
    echo "❌ Docker build failed"
    exit 1
fi

# Step 6: Deploy to Cloud Run
echo ""
echo "======================================================================"
echo "  Deploying to Cloud Run..."
echo "======================================================================"
echo ""

gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 3600 \
    --min-instances 0 \
    --max-instances 10 \
    --port 8080

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "  ✅ Deployment Successful!"
    echo "======================================================================"
    echo ""
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format="value(status.url)")
    
    echo "🌐 Service URL: ${SERVICE_URL}"
    echo ""
    echo "You can also view your service in the console:"
    echo "https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}"
    echo ""
    echo "======================================================================"
else
    echo ""
    echo "❌ Deployment failed"
    exit 1
fi
