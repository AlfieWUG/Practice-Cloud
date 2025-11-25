#!/bin/bash
# =============================================================================
# AWS Credentials Configuration Script
# =============================================================================
# This script will securely configure your AWS credentials
# =============================================================================

echo "======================================================================"
echo "  AWS Credentials Configuration"
echo "======================================================================"
echo ""
echo "This will configure your AWS credentials securely."
echo "Credentials will be stored in ~/.aws/credentials (encrypted by macOS)"
echo ""

# Run AWS configure
aws configure

echo ""
echo "======================================================================"
echo "  ✅ Configuration Complete!"
echo "======================================================================"
echo ""
echo "Verifying credentials..."
aws sts get-caller-identity

echo ""
echo "If you see your AWS Account ID above, credentials are working!"
echo ""
