# Quick Assess Troubleshooting

## 500 Error on Upload

If you're getting a 500 error when uploading files, try these steps:

### 1. Restart the Backend
The backend must be restarted after code changes:

```bash
# Stop the current backend (Ctrl+C in the terminal where it's running)
# Then restart:
cd /Users/aaldertoosthuizen/Projects/agentic-services
./scripts/start_backend.sh
```

### 2. Check Backend Logs
Look at the terminal where the backend is running - it should show the actual error message.

### 3. Verify Environment Variables
Make sure these are set when starting the backend:
```bash
export APP_ENV=development
export SECRET_KEY=some-dev-secret
export QUICK_ASSESS_API_KEY=demo-key
export DYNAMODB_ENDPOINT=http://localhost:8001
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_REGION=us-east-1
```

### 4. Check Local Storage Directory
The backend creates `/tmp/quick-assess-uploads` for local file storage. Make sure:
- The `/tmp` directory exists and is writable
- You have permissions to create directories

### 5. Test the Upload Endpoint Directly
```bash
curl -X POST http://localhost:8000/api/v1/quick-assess/upload \
  -H "X-API-Key: demo-key" \
  -F "files=@/path/to/test.pdf"
```

### Common Issues:

**Issue**: `ModuleNotFoundError` or import errors
**Fix**: Make sure you're in the virtual environment:
```bash
source venv/bin/activate
```

**Issue**: `StorageUploadError` or S3 connection errors
**Fix**: The code now uses local file storage when `APP_ENV=development` and no AWS credentials. This should work automatically.

**Issue**: `MetadataWriteError` or DynamoDB errors
**Fix**: Make sure DynamoDB Local is running:
```bash
docker run -p 8001:8000 amazon/dynamodb-local
```

And the tables are created (the startup script does this automatically).

---

**Most Common Fix**: Just restart the backend! 🚀





