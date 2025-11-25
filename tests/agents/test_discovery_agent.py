"""
Unit tests for DiscoveryAgent
"""

import pytest
import json
from unittest.mock import patch

from agentic_services.agents.discovery import DiscoveryAgent
from tests.mocks import mock_bedrock_client, mock_s3_client, mock_dynamodb_client, mock_eventbridge_client


@pytest.mark.asyncio
class TestDiscoveryAgent:
    """Test suite for DiscoveryAgent"""
    
    async def test_agent_initialization(self):
        """Test DiscoveryAgent initializes correctly"""
        agent = DiscoveryAgent()
        
        assert agent.agent_id is not None
        assert agent.agent_type == "DiscoveryAgent"
        assert agent.discovery_data is None
    
    async def test_agent_initialization_with_custom_id(self):
        """Test DiscoveryAgent with custom agent_id"""
        custom_id = "custom-discovery-123"
        agent = DiscoveryAgent(agent_id=custom_id)
        
        assert agent.agent_id == custom_id
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_success(self, sample_project_id, sample_requirements):
        """Test successful discovery execution"""
        # Setup mock response
        mock_response = json.dumps({
            "project_type": "task_management_system",
            "technology_stack": {
                "languages": ["Python"],
                "frameworks": ["FastAPI"],
                "databases": ["PostgreSQL"]
            },
            "components": ["REST API", "Database", "Auth Service"],
            "requirements": {
                "functional": ["User auth", "Task CRUD"],
                "non_functional": ["Security", "Scalability"]
            },
            "dependencies": ["PostgreSQL", "JWT"],
            "constraints": ["Budget", "Timeline"],
            "assumptions": ["Cloud deployment"]
        })
        mock_bedrock_client.set_mock_response("requirements", mock_response)
        
        # Execute agent
        agent = DiscoveryAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'requirements': sample_requirements
        })
        
        # Assertions
        assert result['status'] == 'completed'
        assert result['project_id'] == sample_project_id
        assert result['agent_id'] == agent.agent_id
        assert 'project_type' in result
        assert result['project_type'] == 'task_management_system'
        assert 's3_uri' in result
        assert result['s3_uri'].startswith('s3://')
        
        # Verify AI was invoked
        assert mock_bedrock_client.invocation_count == 1
        assert 'requirements' in mock_bedrock_client.last_prompt.lower()
        
        # Verify S3 storage
        assert mock_s3_client.upload_count == 1
        
        # Verify DynamoDB state save
        assert mock_dynamodb_client.put_count == 1
        
        # Verify events published
        assert mock_eventbridge_client.event_count == 2  # started + completed
        started_events = mock_eventbridge_client.get_events_by_type('discovery.started')
        completed_events = mock_eventbridge_client.get_events_by_type('discovery.completed')
        assert len(started_events) == 1
        assert len(completed_events) == 1
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_with_context(self, sample_project_id, sample_requirements):
        """Test discovery with additional context"""
        context = "Target deployment: AWS ECS with Fargate"
        
        agent = DiscoveryAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'requirements': sample_requirements,
            'context': context
        })
        
        assert result['status'] == 'completed'
        assert context.lower() in mock_bedrock_client.last_prompt.lower() or 'context' in mock_bedrock_client.last_prompt.lower()
    
    async def test_execute_missing_project_id(self, sample_requirements):
        """Test execution fails without project_id"""
        agent = DiscoveryAgent()
        
        with pytest.raises(ValueError) as exc_info:
            await agent.execute({'requirements': sample_requirements})
        
        assert 'project_id' in str(exc_info.value)
    
    async def test_execute_missing_requirements(self, sample_project_id):
        """Test execution fails without requirements"""
        agent = DiscoveryAgent()
        
        with pytest.raises(ValueError) as exc_info:
            await agent.execute({'project_id': sample_project_id})
        
        assert 'requirements' in str(exc_info.value)
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_ai_failure_publishes_failed_event(self, sample_project_id, sample_requirements):
        """Test that failure events are published on AI errors"""
        # Save original method
        from tests.mocks.aws_mocks import MockBedrockClient
        original_invoke = MockBedrockClient.invoke_claude
        
        # Make bedrock raise an exception
        async def failing_invoke(*args, **kwargs):
            raise Exception("AI service unavailable")
        
        mock_bedrock_client.invoke_claude = failing_invoke
        
        agent = DiscoveryAgent()
        
        try:
            with pytest.raises(Exception):
                await agent.execute({
                    'project_id': sample_project_id,
                    'requirements': sample_requirements
                })
            
            # Verify failure event was published
            failed_events = mock_eventbridge_client.get_events_by_type('discovery.failed')
            assert len(failed_events) == 1
            assert failed_events[0]['detail']['project_id'] == sample_project_id
        finally:
            # Restore original method
            mock_bedrock_client.invoke_claude = original_invoke
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_json_parsing_fallback(self, sample_project_id, sample_requirements):
        """Test JSON parsing with markdown code blocks"""
        # Clear any previous mock responses
        mock_bedrock_client.mock_responses.clear()
        
        # Mock response with JSON in markdown
        mock_response = '''```json
{
    "project_type": "web_app",
    "technology_stack": {},
    "components": [],
    "requirements": {"functional": [], "non_functional": []},
    "dependencies": [],
    "constraints": [],
    "assumptions": []
}
```'''
        mock_bedrock_client.set_mock_response("analyze", mock_response)
        
        agent = DiscoveryAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'requirements': sample_requirements
        })
        
        assert result['project_type'] == 'web_app'
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_json_parsing_failure_fallback(self, sample_project_id, sample_requirements):
        """Test fallback when JSON parsing completely fails"""
        # Clear any previous mock responses
        mock_bedrock_client.mock_responses.clear()
        
        # Mock non-JSON response
        mock_response = "This is just plain text without any JSON"
        mock_bedrock_client.set_mock_response("analyze", mock_response)
        
        agent = DiscoveryAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'requirements': sample_requirements
        })
        
        # Should have fallback structure
        assert 'project_type' in result
        assert result['project_type'] == 'unknown'
        assert 'raw_analysis' in result
    
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    async def test_get_project_summary_success(self, sample_project_id, sample_discovery_data):
        """Test retrieving project summary"""
        # Create agent first to get consistent agent_id
        agent = DiscoveryAgent(agent_id='test-agent-summary')
        
        # Store discovery data
        s3_uri = await mock_s3_client.upload_json(
            bucket="test-bucket",
            key=f"{sample_project_id}/discovery/test.json",
            data=sample_discovery_data
        )
        
        # Save state with correct agent_id
        await mock_dynamodb_client.put_item(
            table_name="AgentStates",
            item={
                'project_id': sample_project_id,
                'agent_id': agent.agent_id,
                'agent_type': 'DiscoveryAgent',
                'state': {'last_discovery': s3_uri},
                'updated_at': '2024-01-01T00:00:00'
            }
        )
        
        summary = await agent.get_project_summary(sample_project_id)
        
        assert summary is not None
        assert 'Project Type:' in summary
        assert sample_discovery_data['project_type'] in summary
    
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    async def test_get_project_summary_no_state(self, sample_project_id):
        """Test summary returns None when no state exists"""
        agent = DiscoveryAgent()
        summary = await agent.get_project_summary(sample_project_id)
        
        assert summary is None
    
    def test_system_prompt_defined(self):
        """Test that SYSTEM_PROMPT is properly defined"""
        assert hasattr(DiscoveryAgent, 'SYSTEM_PROMPT')
        assert len(DiscoveryAgent.SYSTEM_PROMPT) > 0
        assert 'discovery' in DiscoveryAgent.SYSTEM_PROMPT.lower()
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_ai_invocation_uses_low_temperature(self, sample_project_id, sample_requirements):
        """Test that discovery uses low temperature for deterministic results"""
        agent = DiscoveryAgent()
        
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
                'requirements': sample_requirements
            })
            
            assert temperature_used is not None
            assert temperature_used <= 0.3  # Discovery should use low temperature
        finally:
            # Restore original
            mock_bedrock_client.invoke_claude = original_invoke
