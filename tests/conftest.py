"""Pytest configuration and fixtures"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tests.mocks import (
    mock_bedrock_client,
    mock_s3_client,
    mock_dynamodb_client,
    mock_eventbridge_client,
    reset_all_mocks,
)


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks before each test"""
    reset_all_mocks()
    yield
    reset_all_mocks()


@pytest.fixture
def mock_aws_credentials(monkeypatch):
    """Mock AWS credentials for testing"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_REGION", "eu-central-1")
    monkeypatch.setenv("S3_DISCOVERY_BUCKET", "test-discovery-bucket")
    monkeypatch.setenv("S3_ARTIFACTS_BUCKET", "test-artifacts-bucket")


@pytest.fixture
def mock_aws_clients():
    """Patch AWS clients with mocks"""
    with patch('agentic_services.tools.aws_helper.bedrock_client', mock_bedrock_client), \
         patch('agentic_services.tools.aws_helper.s3_client', mock_s3_client), \
         patch('agentic_services.tools.aws_helper.dynamodb_client', mock_dynamodb_client), \
         patch('agentic_services.tools.aws_helper.eventbridge_client', mock_eventbridge_client):
        yield {
            'bedrock': mock_bedrock_client,
            's3': mock_s3_client,
            'dynamodb': mock_dynamodb_client,
            'eventbridge': mock_eventbridge_client,
        }


@pytest.fixture
def sample_project_id():
    """Sample project ID for testing"""
    return "test-project-123"


@pytest.fixture
def sample_requirements():
    """Sample project requirements"""
    return """Build a REST API for a task management system with the following features:
- User authentication and authorization
- Create, read, update, delete tasks
- Task assignment to users
- Task status tracking (todo, in-progress, done)
- Due dates and reminders
- PostgreSQL database
- Deploy to AWS
"""


@pytest.fixture
def sample_discovery_data():
    """Sample discovery results"""
    return {
        "project_id": "test-project-123",
        "project_type": "web_application",
        "technology_stack": {
            "languages": ["Python"],
            "frameworks": ["FastAPI"],
            "databases": ["PostgreSQL"],
            "cloud_services": ["AWS"]
        },
        "components": ["REST API", "Database", "Authentication Service"],
        "requirements": {
            "functional": ["User Authentication", "Task CRUD Operations"],
            "non_functional": ["Scalability", "Security"]
        },
        "dependencies": ["AWS RDS", "Docker"],
        "constraints": ["Budget: $5000/month"],
        "assumptions": ["Cloud-native deployment"]
    }


@pytest.fixture
def sample_analysis_data():
    """Sample analysis results"""
    return {
        "project_id": "test-project-123",
        "complexity_assessment": {
            "level": "medium",
            "reasoning": "Standard web application"
        },
        "technical_challenges": [{"name": "Scalability", "severity": "medium"}],
        "recommended_architecture": {
            "pattern": "microservices",
            "reasoning": "Better scalability"
        },
        "security_considerations": ["JWT authentication", "HTTPS only"],
        "risk_assessment": [{"risk": "Database bottleneck"}]
    }


@pytest.fixture
def sample_planning_data():
    """Sample planning results"""
    return {
        "project_id": "test-project-123",
        "phases": [{"name": "Setup", "duration": "2 weeks"}],
        "sprints": [{"sprint_number": 1, "story_points": 21}],
        "milestones": [{"name": "MVP", "date": "2024-12-15"}],
        "prioritization": {
            "must_have": ["User Auth"],
            "should_have": ["Task Assignment"]
        },
        "effort_estimation": {
            "total_story_points": 89,
            "confidence_level": "medium"
        },
        "team_requirements": {"team_size": 3}
    }
