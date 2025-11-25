#!/usr/bin/env python3
"""
Test script for Quick Assess upload functionality.
Tests the entire upload flow to identify issues.
"""
import os
import sys
import requests
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'onboarding-portal', 'backend'))

# Test configuration
API_URL = "http://localhost:8000/api/v1/quick-assess"
API_KEY = "demo-key"
TEST_FILE_CONTENT = b"This is a test PDF content for Quick Assess"

def test_backend_health():
    """Test if backend is running."""
    print("🔍 Step 1: Testing backend health...")
    try:
        response = requests.get(f"http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running")
            return True
        else:
            print(f"   ❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend is not running on port 8000")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_dynamodb_connection():
    """Test DynamoDB Local connection."""
    print("\n🔍 Step 2: Testing DynamoDB Local...")
    try:
        import boto3
        dynamodb = boto3.resource(
            "dynamodb",
            endpoint_url="http://localhost:8001",
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name="us-east-1",
        )
        table = dynamodb.Table("agentic-services-quick-assess")
        # Try to describe the table
        table.meta.client.describe_table(TableName="agentic-services-quick-assess")
        print("   ✅ DynamoDB Local is accessible and table exists")
        return True
    except Exception as e:
        print(f"   ❌ DynamoDB error: {e}")
        return False

def test_file_storage():
    """Test local file storage directory."""
    print("\n🔍 Step 3: Testing file storage...")
    storage_path = Path("/tmp/quick-assess-uploads")
    try:
        storage_path.mkdir(parents=True, exist_ok=True)
        test_file = storage_path / "test_write.txt"
        test_file.write_text("test")
        test_file.unlink()
        print(f"   ✅ File storage directory is writable: {storage_path}")
        return True
    except Exception as e:
        print(f"   ❌ File storage error: {e}")
        return False

def test_upload_endpoint():
    """Test the upload endpoint."""
    print("\n🔍 Step 4: Testing upload endpoint...")
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(TEST_FILE_CONTENT)
        tmp_file_path = tmp_file.name
    
    try:
        headers = {"X-API-Key": API_KEY}
        
        with open(tmp_file_path, "rb") as f:
            files = {"files": ("test.pdf", f, "application/pdf")}
            response = requests.post(
                f"{API_URL}/upload",
                headers=headers,
                files=files,
                timeout=30
            )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 201:
            print("   ✅ Upload successful!")
            data = response.json()
            print(f"   Assessment ID: {data.get('assessment_id')}")
            return True, data.get('assessment_id')
        else:
            print(f"   ❌ Upload failed")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend")
        return False, None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False, None
    finally:
        # Clean up
        try:
            os.unlink(tmp_file_path)
        except:
            pass

def main():
    print("=" * 60)
    print("Quick Assess Upload Test")
    print("=" * 60)
    
    # Run tests
    backend_ok = test_backend_health()
    if not backend_ok:
        print("\n❌ Backend is not running. Please start it first:")
        print("   ./scripts/start_backend.sh")
        return
    
    dynamodb_ok = test_dynamodb_connection()
    if not dynamodb_ok:
        print("\n⚠️  DynamoDB Local might not be running. Start it with:")
        print("   docker run -p 8001:8000 amazon/dynamodb-local")
    
    storage_ok = test_file_storage()
    
    upload_ok, assessment_id = test_upload_endpoint()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Backend Health:     {'✅' if backend_ok else '❌'}")
    print(f"DynamoDB Connection: {'✅' if dynamodb_ok else '❌'}")
    print(f"File Storage:        {'✅' if storage_ok else '❌'}")
    print(f"Upload Endpoint:     {'✅' if upload_ok else '❌'}")
    
    if upload_ok:
        print(f"\n🎉 Success! Assessment ID: {assessment_id}")
    else:
        print("\n❌ Upload failed. Check the error messages above.")
        print("\nNext steps:")
        print("1. Check backend logs for detailed error messages")
        print("2. Verify DynamoDB Local is running: docker ps | grep dynamodb")
        print("3. Verify backend has DYNAMODB_ENDPOINT=http://localhost:8001")

if __name__ == "__main__":
    main()





