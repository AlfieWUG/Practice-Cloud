#!/usr/bin/env python3
"""Test script for Quick Assess execute endpoint."""
import requests
import sys

API_URL = "http://localhost:8000/api/v1/quick-assess"
API_KEY = "demo-key"

# Get assessment_id from command line or use a test one
assessment_id = sys.argv[1] if len(sys.argv) > 1 else "qa-83e94288d86540ab952f1ae2d776efb2"

print(f"🔍 Testing execute endpoint for assessment: {assessment_id}")
print("=" * 60)

headers = {"X-API-Key": API_KEY}

# First check if assessment exists
print("\n1. Checking if assessment exists...")
try:
    response = requests.get(
        f"{API_URL}/{assessment_id}/status",
        headers=headers,
        timeout=10
    )
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Assessment found: {data.get('status')}")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Try to execute
print(f"\n2. Executing assessment...")
try:
    response = requests.post(
        f"{API_URL}/{assessment_id}/execute",
        headers=headers,
        timeout=30
    )
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
    
    if response.status_code == 202:
        data = response.json()
        print(f"   ✅ Execution started!")
        print(f"   Workflow ID: {data.get('workflow_id')}")
    else:
        print(f"   ❌ Execution failed")
        if response.status_code == 500:
            print(f"\n   Full error response:")
            print(response.text)
            
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to backend")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)





