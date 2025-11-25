"""
FastAPI application for Nagarro Agentic Services Onboarding Portal.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.api import projects, agents, quick_assess


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: Clean up resources
    pass


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Customer onboarding and agent execution portal for Nagarro Agentic Services",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix=settings.api_v1_prefix)
app.include_router(agents.router, prefix=settings.api_v1_prefix)
app.include_router(quick_assess.router, prefix=settings.api_v1_prefix)


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env,
        "demo_mode": settings.demo_mode,
        "docs": "/docs",
        "agents_available": 24
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.app_env,
        "demo_mode": settings.demo_mode
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
