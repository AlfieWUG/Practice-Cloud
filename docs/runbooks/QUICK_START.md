# 🚀 Quick Start - One Command to Rule Them All

## Single Startup Script

Instead of starting each service separately, just run:

```bash
cd /Users/aaldertoosthuizen/Projects/agentic-services
./start_all.sh
```

This single script will:
1. ✅ **Start DynamoDB Local** (if Docker is available)
2. ✅ **Create DynamoDB tables** (if they don't exist)
3. ✅ **Start FastAPI Backend** (port 8000)
4. ✅ **Start Streamlit Dashboard** (port 8501)

## What You'll See

The script will:
- Check if services are already running (and skip if they are)
- Start DynamoDB Local in a Docker container
- Create the required DynamoDB tables automatically
- Start the FastAPI backend in the background
- Start Streamlit (this will block and show the dashboard)

## Access Points

Once everything is running:
- **Streamlit Dashboard**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **DynamoDB Local**: http://localhost:8001

## Stopping Services

Press `Ctrl+C` in the terminal where you ran `./start_all.sh` to stop Streamlit.

To stop other services:
```bash
# Stop backend
pkill -f "uvicorn main:app"

# Stop DynamoDB Local
docker stop dynamodb-local
```

## Troubleshooting

### "Docker not found"
- Install Docker Desktop or start DynamoDB Local manually:
  ```bash
  docker run -p 8001:8000 amazon/dynamodb-local
  ```

### "Backend already running"
- The script detects if services are already running and skips them
- To restart, stop the existing process first

### "Port already in use"
- Stop the service using that port:
  ```bash
  # Find what's using port 8000
  lsof -i :8000
  # Kill it
  kill -9 <PID>
  ```

### Backend logs
- Check `/tmp/backend.log` if the backend doesn't start

---

**That's it!** One command to start everything. 🎉





