"""
Application configuration using Pydantic Settings.
Loads from environment variables and .env file.
"""
from typing import List
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Nagarro Agentic Services Portal"
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )
    
    # Database
    database_url: str = Field(
        default="postgresql://agentic:agentic123@localhost:5432/agentic_portal",
        env="DATABASE_URL"
    )
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AWS Configuration
    aws_region: str = Field(default="eu-central-1", env="AWS_REGION")
    aws_access_key_id: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    
    # AWS Resources (from main agentic-services platform)
    agentic_services_api_endpoint: str = Field(
        default="",
        env="AGENTIC_SERVICES_API_ENDPOINT"
    )
    s3_discovery_bucket: str = "agentic-services-discovery"
    s3_artifacts_bucket: str = "agentic-services-artifacts"
    s3_quick_assess_bucket: str = Field(
        default="agentic-services-quick-assess",
        env="S3_QUICK_ASSESS_BUCKET"
    )
    dynamodb_table_prefix: str = "agentic-services"
    dynamodb_quick_assess_table: str = Field(
        default="agentic-services-quick-assess",
        env="DYNAMODB_QUICK_ASSESS_TABLE"
    )
    dynamodb_quick_assess_errors_table: str = Field(
        default="agentic-services-quick-assess-errors",
        env="DYNAMODB_QUICK_ASSESS_ERRORS_TABLE"
    )
    quick_assess_api_key: str = Field(..., env="QUICK_ASSESS_API_KEY")
    default_user_id: str = Field(default="quick-assess-user", env="DEFAULT_USER_ID")
    
    # Demo Mode
    demo_mode: bool = Field(default=False, env="DEMO_MODE")
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
