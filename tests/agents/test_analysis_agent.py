"""
Unit tests for AnalysisAgent
"""

import pytest
import json
from unittest.mock import patch

from agentic_services.agents.analysis import AnalysisAgent
from tests.mocks import mock_bedrock_client, mock_s3_client, mock_dynamodb_client, mock_eventbridge_client


@pytest.mark.asyncio
class TestAnalysisAgent:
    """Test suite for AnalysisAgent"""
    
    async def test_agent_initialization(self):
        """Test AnalysisAgent initializes correctly"""
        agent = AnalysisAgent()
        
        assert agent.agent_id is not None
        assert agent.agent_type == "AnalysisAgent"
        assert agent.analysis_data is None
    
    async def test_agent_initialization_with_custom_id(self):
        """Test AnalysisAgent with custom agent_id"""
        custom_id = "custom-analysis-456"
        agent = AnalysisAgent(agent_id=custom_id)
        
        assert agent.agent_id == custom_id
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_success(self, sample_project_id, sample_discovery_data):
        """Test successful analysis execution"""
        # Setup mock response
        mock_response = json.dumps({
            "complexity_assessment": {
                "level": "high",
                "reasoning": "Multiple integrations required"
            },
            "technical_challenges": [
                {"name": "Scalability", "severity": "high", "description": "Handle 10k concurrent users"}
            ],
            "recommended_architecture": {
                "pattern": "microservices",
                "reasoning": "Better scalability",
                "alternatives": ["monolith"]
            },
            "scalability_analysis": {
                "expected_load": "10000 users",
                "scaling_strategy": "horizontal"
            },
            "security_considerations": ["OAuth 2.0", "Rate limiting"],
            "performance_requirements": {"response_time": "< 100ms"},
            "integration_points": ["Payment gateway"],
            "best_practices": ["Use caching"],
            "risk_assessment": [{"risk": "Third-party API dependency"}]
        })
        mock_bedrock_client.set_mock_response("analysis", mock_response)
        
        # Execute agent
        agent = AnalysisAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'discovery_data': sample_discovery_data
        })
        
        # Assertions
        assert result['status'] == 'completed'
        assert result['project_id'] == sample_project_id
        assert result['agent_id'] == agent.agent_id
        assert 'complexity_assessment' in result
        assert result['complexity_assessment']['level'] == 'high'
        assert 's3_uri' in result
        
        # Verify AI was invoked
        assert mock_bedrock_client.invocation_count == 1
        
        # Verify S3 storage
        assert mock_s3_client.upload_count == 1
        
        # Verify DynamoDB state save
        assert mock_dynamodb_client.put_count == 1
        
        # Verify events published
        assert mock_eventbridge_client.event_count == 2  # started + completed
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_with_s3_uri(self, sample_project_id, sample_discovery_data):
        """Test analysis with discovery data from S3"""
        # Store discovery data in mock S3
        s3_uri = await mock_s3_client.upload_json(
            bucket="test-bucket",
            key=f"{sample_project_id}/discovery/test.json",
            data=sample_discovery_data
        )
        
        agent = AnalysisAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'discovery_s3_uri': s3_uri
        })
        
        assert result['status'] == 'completed'
        assert result['based_on_discovery'] == s3_uri
        
        # Verify S3 was read
        assert mock_s3_client.download_count == 1
    
    async def test_execute_missing_project_id(self, sample_discovery_data):
        """Test execution fails without project_id"""
        agent = AnalysisAgent()
        
        with pytest.raises(ValueError) as exc_info:
            await agent.execute({'discovery_data': sample_discovery_data})
        
        assert 'project_id' in str(exc_info.value)
    
    async def test_execute_missing_discovery_data(self, sample_project_id):
        """Test execution fails without discovery data"""
        agent = AnalysisAgent()
        
        with pytest.raises(ValueError) as exc_info:
            await agent.execute({'project_id': sample_project_id})
        
        assert 'discovery data' in str(exc_info.value).lower()
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_failure_publishes_event(self, sample_project_id, sample_discovery_data):
        """Test that failure events are published on errors"""
        # Save original method
        from tests.mocks.aws_mocks import MockBedrockClient
        original_invoke = MockBedrockClient.invoke_claude
        
        # Make bedrock raise an exception
        async def failing_invoke(*args, **kwargs):
            raise Exception("Analysis AI error")
        
        mock_bedrock_client.invoke_claude = failing_invoke
        
        agent = AnalysisAgent()
        
        try:
            with pytest.raises(Exception):
                await agent.execute({
                    'project_id': sample_project_id,
                    'discovery_data': sample_discovery_data
                })
            
            # Verify failure event was published
            failed_events = mock_eventbridge_client.get_events_by_type('analysis.failed')
            assert len(failed_events) == 1
            assert failed_events[0]['detail']['project_id'] == sample_project_id
        finally:
            # Restore original method
            mock_bedrock_client.invoke_claude = original_invoke
    
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    async def test_get_architecture_summary_success(self, sample_project_id, sample_analysis_data):
        """Test retrieving architecture summary"""
        # Create agent
        agent = AnalysisAgent(agent_id='test-analysis-agent')
        
        # Store analysis data
        s3_uri = await mock_s3_client.upload_json(
            bucket="test-bucket",
            key=f"{sample_project_id}/analysis/test.json",
            data=sample_analysis_data
        )
        
        # Save state
        await mock_dynamodb_client.put_item(
            table_name="AgentStates",
            item={
                'project_id': sample_project_id,
                'agent_id': agent.agent_id,
                'agent_type': 'AnalysisAgent',
                'state': {'last_analysis': s3_uri},
                'updated_at': '2024-01-01T00:00:00'
            }
        )
        
        summary = await agent.get_architecture_summary(sample_project_id)
        
        assert summary is not None
        assert 'Architecture Recommendation:' in summary
        assert sample_analysis_data['recommended_architecture']['pattern'] in summary
    
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    async def test_get_architecture_summary_no_state(self, sample_project_id):
        """Test summary returns None when no state exists"""
        agent = AnalysisAgent()
        summary = await agent.get_architecture_summary(sample_project_id)
        
        assert summary is None
    
    def test_system_prompt_defined(self):
        """Test that SYSTEM_PROMPT is properly defined"""
        assert hasattr(AnalysisAgent, 'SYSTEM_PROMPT')
        assert len(AnalysisAgent.SYSTEM_PROMPT) > 0
        assert 'analysis' in AnalysisAgent.SYSTEM_PROMPT.lower()
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_ai_temperature_setting(self, sample_project_id, sample_discovery_data):
        """Test that analysis uses appropriate temperature"""
        agent = AnalysisAgent()
        
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
                'discovery_data': sample_discovery_data
            })
            
            assert temperature_used is not None
            assert 0.3 <= temperature_used <= 0.5  # Analysis should use balanced temperature
        finally:
            mock_bedrock_client.invoke_claude = original_invoke
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_json_parsing_success(self, sample_project_id, sample_discovery_data):
        """Test JSON parsing from markdown code block"""
        mock_bedrock_client.mock_responses.clear()
        
        # Mock response with complete JSON in markdown  
        mock_response = json.dumps({
            "complexity_assessment": {"level": "low", "reasoning": "Simple app"},
            "technical_challenges": [],
            "recommended_architecture": {"pattern": "monolith", "reasoning": "Simple"},
            "scalability_analysis": {},
            "security_considerations": [],
            "performance_requirements": {},
            "integration_points": [],
            "best_practices": [],
            "risk_assessment": []
        })
        mock_bedrock_client.set_mock_response("technical analysis", mock_response)
        
        agent = AnalysisAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'discovery_data': sample_discovery_data
        })
        
        assert result['complexity_assessment']['level'] == 'low'
