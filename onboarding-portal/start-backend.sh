#!/bin/bash

echo "🚀 Starting Backend API..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
