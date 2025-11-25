"""
Configuration management for Nagarro Agentic Services Platform
Loads settings from environment variables with validation
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "eu-central-1")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # AWS Bedrock
    BEDROCK_MODEL_ID: str = os.getenv(
        "BEDROCK_MODEL_ID", 
        "anthropic.claude-3-sonnet-20240229-v1:0"
    )
    BEDROCK_MAX_TOKENS: int = int(os.getenv("BEDROCK_MAX_TOKENS", "10000"))
    BEDROCK_DOCUMENT_PARSER_MODEL_ID: str = os.getenv(
        "BEDROCK_DOCUMENT_PARSER_MODEL_ID",
        "anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
    
    # Application
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database (DynamoDB)
    DYNAMODB_TABLE_PREFIX: str = os.getenv("DYNAMODB_TABLE_PREFIX", "agentic-services")
    DYNAMODB_ENDPOINT: Optional[str] = os.getenv("DYNAMODB_ENDPOINT")
    DYNAMODB_QUICK_ASSESS_TABLE: str = os.getenv(
        "DYNAMODB_QUICK_ASSESS_TABLE",
        f"{DYNAMODB_TABLE_PREFIX}-quick-assess"
    )
    DYNAMODB_QUICK_ASSESS_ERRORS_TABLE: str = os.getenv(
        "DYNAMODB_QUICK_ASSESS_ERRORS_TABLE",
        f"{DYNAMODB_TABLE_PREFIX}-quick-assess-errors"
    )
    
    # S3 Buckets
    S3_DISCOVERY_BUCKET: str = os.getenv("S3_DISCOVERY_BUCKET", "nagarro-agentic-discovery-dev")
    S3_ARTIFACTS_BUCKET: str = os.getenv("S3_ARTIFACTS_BUCKET", "nagarro-agentic-artifacts-dev")
    S3_LOGS_BUCKET: str = os.getenv("S3_LOGS_BUCKET", "nagarro-agentic-logs-dev")
    S3_QUICK_ASSESS_BUCKET: str = os.getenv("S3_QUICK_ASSESS_BUCKET", "nagarro-agentic-quick-assess-dev")
    
    # VPC Configuration
    VPC_ID: Optional[str] = os.getenv("VPC_ID")
    PRIVATE_SUBNET_IDS: Optional[str] = os.getenv("PRIVATE_SUBNET_IDS")
    SECURITY_GROUP_ID: Optional[str] = os.getenv("SECURITY_GROUP_ID")
    
    # ECS Configuration
    ECS_CLUSTER_NAME: str = os.getenv("ECS_CLUSTER_NAME", "agentic-services-cluster")
    ECS_TASK_EXECUTION_ROLE_ARN: Optional[str] = os.getenv("ECS_TASK_EXECUTION_ROLE_ARN")
    
    # EventBridge
    EVENT_BUS_NAME: str = os.getenv("EVENT_BUS_NAME", "agentic-services-event-bus")
    
    # Secrets Manager
    SECRETS_MANAGER_PREFIX: str = os.getenv("SECRETS_MANAGER_PREFIX", "agentic-services/")
    
    # API Configuration
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://api.nagarro-agentic.com/v1")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # Redis/ElastiCache
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # Monitoring
    CLOUDWATCH_LOG_GROUP: str = os.getenv("CLOUDWATCH_LOG_GROUP", "/aws/agentic-services")
    XRAY_ENABLED: bool = os.getenv("XRAY_ENABLED", "true").lower() == "true"
    
    # Demo Mode
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() == "true"
    DEMO_DATA_PATH: str = os.getenv("DEMO_DATA_PATH", "demo/artifacts")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required settings are present"""
        if cls.APP_ENV == "production":
            required = [
                cls.AWS_ACCESS_KEY_ID,
                cls.AWS_SECRET_ACCESS_KEY,
                cls.VPC_ID,
            ]
            if not all(required):
                raise ValueError("Missing required AWS configuration for production")
        return True
    
    @classmethod
    def get_dynamodb_table_name(cls, table_name: str) -> str:
        """Get full DynamoDB table name with prefix"""
        return f"{cls.DYNAMODB_TABLE_PREFIX}-{table_name}"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.APP_ENV == "production"
    
    @classmethod
    def is_demo_mode(cls) -> bool:
        """Check if demo mode is enabled"""
        return cls.DEMO_MODE


# Create singleton instance
settings = Settings()
