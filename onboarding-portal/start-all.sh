#!/bin/bash

echo "🚀 Starting Nagarro Agentic Services Portal"
echo "==========================================="
echo ""
echo "Starting Backend and Frontend..."
echo ""
echo "Backend will be at:  http://localhost:8000"
echo "Frontend will be at: http://localhost:3000"
echo "API Docs at:         http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Start backend in background
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend in background
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait
