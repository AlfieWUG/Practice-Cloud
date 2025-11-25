"""
Unit tests for ArtifactGenerationAgent
"""

import pytest
import json
from unittest.mock import patch

from agentic_services.agents.artifact_generation import ArtifactGenerationAgent
from tests.mocks import mock_bedrock_client, mock_s3_client, mock_dynamodb_client, mock_eventbridge_client


@pytest.mark.asyncio
class TestArtifactGenerationAgent:
    """Test suite for ArtifactGenerationAgent"""
    
    async def test_agent_initialization(self):
        """Test ArtifactGenerationAgent initializes correctly"""
        agent = ArtifactGenerationAgent()
        
        assert agent.agent_id is not None
        assert agent.agent_type == "ArtifactGenerationAgent"
        assert agent.generated_artifacts is None
    
    async def test_agent_initialization_with_custom_id(self):
        """Test ArtifactGenerationAgent with custom agent_id"""
        custom_id = "custom-artifact-999"
        agent = ArtifactGenerationAgent(agent_id=custom_id)
        
        assert agent.agent_id == custom_id
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_success(self, sample_project_id, sample_planning_data):
        """Test successful artifact generation execution"""
        # Setup mock response
        mock_response = json.dumps({
            "artifacts": [
                {"type": "code", "filename": "main.py", "content": "# Main app", "description": "Entry point"},
                {"type": "documentation", "filename": "README.md", "content": "# Project", "description": "Main docs"}
            ],
            "structure": {
                "src": ["main.py", "config.py"],
                "tests": ["test_main.py"],
                "docs": ["README.md"]
            },
            "documentation": {
                "readme": "# My Project\n\nDescription here",
                "api_docs": "## API\n\nEndpoints...",
                "architecture_docs": "## Architecture\n\nDiagrams..."
            },
            "configurations": {
                "docker": {"Dockerfile": "FROM python:3.11"},
                "ci_cd": {".gitlab-ci.yml": "stages: [test, deploy]"},
                "environment_configs": {".env.example": "API_KEY=xxx"}
            },
            "code_templates": [
                {"language": "python", "path": "src/main.py", "content": "def main(): pass"}
            ],
            "database_schemas": [
                {"name": "users", "columns": ["id", "name", "email"]}
            ],
            "api_specifications": {"openapi": "3.0", "paths": {}},
            "testing_templates": [
                {"type": "unit", "framework": "pytest", "content": "def test_example(): assert True"}
            ]
        })
        mock_bedrock_client.set_mock_response("artifact", mock_response)
        
        # Execute agent
        agent = ArtifactGenerationAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'planning_data': sample_planning_data
        })
        
        # Assertions
        assert result['status'] == 'completed'
        assert result['project_id'] == sample_project_id
        assert result['agent_id'] == agent.agent_id
        assert 'artifacts' in result
        assert len(result['artifacts']) == 2
        assert 's3_uri' in result
        
        # Verify AI was invoked
        assert mock_bedrock_client.invocation_count == 1
        
        # Verify S3 storage (uses artifacts bucket)
        assert mock_s3_client.upload_count == 1
        
        # Verify DynamoDB state save
        assert mock_dynamodb_client.put_count == 1
        
        # Verify events published
        assert mock_eventbridge_client.event_count == 2  # started + completed
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_with_artifact_types(self, sample_project_id, sample_planning_data):
        """Test artifact generation with specific types"""
        artifact_types = ["code", "documentation", "ci_cd"]
        
        agent = ArtifactGenerationAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'planning_data': sample_planning_data,
            'artifact_types': artifact_types
        })
        
        assert result['status'] == 'completed'
        assert result['artifact_types_generated'] == artifact_types
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_with_s3_uri(self, sample_project_id, sample_planning_data):
        """Test artifact generation with planning data from S3"""
        # Store planning data in mock S3
        s3_uri = await mock_s3_client.upload_json(
            bucket="test-bucket",
            key=f"{sample_project_id}/planning/test.json",
            data=sample_planning_data
        )
        
        agent = ArtifactGenerationAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'planning_s3_uri': s3_uri
        })
        
        assert result['status'] == 'completed'
        
        # Verify S3 was read
        assert mock_s3_client.download_count == 1
    
    async def test_execute_missing_project_id(self, sample_planning_data):
        """Test execution fails without project_id"""
        agent = ArtifactGenerationAgent()
        
        with pytest.raises(ValueError) as exc_info:
            await agent.execute({'planning_data': sample_planning_data})
        
        assert 'project_id' in str(exc_info.value)
    
    async def test_execute_missing_planning_data(self, sample_project_id):
        """Test execution fails without planning data"""
        agent = ArtifactGenerationAgent()
        
        with pytest.raises(ValueError) as exc_info:
            await agent.execute({'project_id': sample_project_id})
        
        assert 'planning data' in str(exc_info.value).lower()
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_failure_publishes_event(self, sample_project_id, sample_planning_data):
        """Test that failure events are published on errors"""
        # Save original method
        from tests.mocks.aws_mocks import MockBedrockClient
        original_invoke = MockBedrockClient.invoke_claude
        
        # Make bedrock raise an exception
        async def failing_invoke(*args, **kwargs):
            raise Exception("Artifact generation AI error")
        
        mock_bedrock_client.invoke_claude = failing_invoke
        
        agent = ArtifactGenerationAgent()
        
        try:
            with pytest.raises(Exception):
                await agent.execute({
                    'project_id': sample_project_id,
                    'planning_data': sample_planning_data
                })
            
            # Verify failure event was published
            failed_events = mock_eventbridge_client.get_events_by_type('artifact_generation.failed')
            assert len(failed_events) == 1
            assert failed_events[0]['detail']['project_id'] == sample_project_id
        finally:
            # Restore original method
            mock_bedrock_client.invoke_claude = original_invoke
    
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    async def test_get_artifact_by_type(self, sample_project_id):
        """Test retrieving specific artifact types"""
        # Create agent
        agent = ArtifactGenerationAgent(agent_id='test-artifact-agent')
        
        # Create test artifacts data
        artifacts_data = {
            "artifacts": [
                {"type": "code", "filename": "main.py", "content": "# Code"},
                {"type": "documentation", "filename": "README.md", "content": "# Docs"},
                {"type": "code", "filename": "utils.py", "content": "# Utils"}
            ]
        }
        
        # Store artifacts data
        s3_uri = await mock_s3_client.upload_json(
            bucket="test-bucket",
            key=f"{sample_project_id}/artifacts/test.json",
            data=artifacts_data
        )
        
        # Save state
        await mock_dynamodb_client.put_item(
            table_name="AgentStates",
            item={
                'project_id': sample_project_id,
                'agent_id': agent.agent_id,
                'agent_type': 'ArtifactGenerationAgent',
                'state': {'last_artifacts': s3_uri},
                'updated_at': '2024-01-01T00:00:00'
            }
        )
        
        # Get code artifacts
        code_artifacts = await agent.get_artifact_by_type(sample_project_id, 'code')
        
        assert code_artifacts is not None
        assert len(code_artifacts) == 2
        assert all(a['type'] == 'code' for a in code_artifacts)
    
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    async def test_get_artifact_by_type_no_state(self, sample_project_id):
        """Test get_artifact returns None when no state exists"""
        agent = ArtifactGenerationAgent()
        artifacts = await agent.get_artifact_by_type(sample_project_id, 'code')
        
        assert artifacts is None
    
    def test_system_prompt_defined(self):
        """Test that SYSTEM_PROMPT is properly defined"""
        assert hasattr(ArtifactGenerationAgent, 'SYSTEM_PROMPT')
        assert len(ArtifactGenerationAgent.SYSTEM_PROMPT) > 0
        assert 'artifact' in ArtifactGenerationAgent.SYSTEM_PROMPT.lower()
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_ai_temperature_setting(self, sample_project_id, sample_planning_data):
        """Test that artifact generation uses low temperature"""
        agent = ArtifactGenerationAgent()
        
        # Capture temperature used
        from tests.mocks.aws_mocks import MockBedrockClient
        original_invoke = MockBedrockClient.invoke_claude
        temperature_used = None
        
        async def capture_temperature(self_mock, *args, **kwargs):
            nonlocal temperature_used
            temperature_used = kwargs.get('temperature', 0.7)
            return await original_invoke(self_mock, *args, **kwargs)
        
        mock_bedrock_client.invoke_claude = lambda *args, **kwargs: capture_temperature(mock_bedrock_client, *args, **kwargs)
        
        try:
            await agent.execute({
                'project_id': sample_project_id,
                'planning_data': sample_planning_data
            })
            
            assert temperature_used is not None
            assert temperature_used <= 0.3  # Artifact generation should use low temperature for consistent code
        finally:
            mock_bedrock_client.invoke_claude = original_invoke
