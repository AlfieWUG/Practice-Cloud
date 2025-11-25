#!/usr/bin/env python3
"""
Quick test script for Dashboard authentication
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agentic_services.auth import DashboardAuth

def test_auth():
    """Test authentication functionality"""
    print("=" * 60)
    print("Testing Dashboard Authentication")
    print("=" * 60)
    
    auth = DashboardAuth()
    
    print(f"\nDemo Mode: {auth.demo_mode}")
    print(f"Use AWS Secrets: {auth.use_aws_secrets}")
    
    # Get credentials
    credentials = auth.get_credentials()
    print(f"\nLoaded {len(credentials)} user(s)")
    
    # Test valid credentials
    print("\n--- Test 1: Valid credentials ---")
    username = os.getenv("DASHBOARD_USERNAME")
    password = os.getenv("DASHBOARD_PASSWORD")
    
    if not username or not password:
        print("✗ ERROR: DASHBOARD_USERNAME and DASHBOARD_PASSWORD must be set in .env")
        return
    
    result = auth.authenticate(username, password)
    print(f"Username: {username}")
    print(f"Result: {'✓ SUCCESS' if result else '✗ FAILED'}")
    
    # Test invalid credentials
    print("\n--- Test 2: Invalid credentials ---")
    result = auth.authenticate("wrong", "password")
    print(f"Username: wrong")
    print(f"Result: {'✓ CORRECTLY REJECTED' if not result else '✗ SHOULD HAVE FAILED'}")
    
    print("\n" + "=" * 60)
    print("Authentication tests complete!")
    print("=" * 60)
    
    print(f"\n✓ Dashboard is running at: http://192.168.2.146:8501")
    print(f"  Credentials configured via environment variables")
    print()

if __name__ == "__main__":
    # Load .env if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    test_auth()
