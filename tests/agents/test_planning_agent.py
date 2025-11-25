"""
Unit tests for PlanningAgent
"""

import pytest
import json
from unittest.mock import patch

from agentic_services.agents.planning import PlanningAgent
from tests.mocks import mock_bedrock_client, mock_s3_client, mock_dynamodb_client, mock_eventbridge_client


@pytest.mark.asyncio
class TestPlanningAgent:
    """Test suite for PlanningAgent"""
    
    async def test_agent_initialization(self):
        """Test PlanningAgent initializes correctly"""
        agent = PlanningAgent()
        
        assert agent.agent_id is not None
        assert agent.agent_type == "PlanningAgent"
        assert agent.planning_data is None
    
    async def test_agent_initialization_with_custom_id(self):
        """Test PlanningAgent with custom agent_id"""
        custom_id = "custom-planning-789"
        agent = PlanningAgent(agent_id=custom_id)
        
        assert agent.agent_id == custom_id
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_success(self, sample_project_id, sample_analysis_data):
        """Test successful planning execution"""
        # Setup mock response
        mock_response = json.dumps({
            "phases": [
                {"name": "Phase 1", "duration": "4 weeks", "goals": ["Setup"]},
                {"name": "Phase 2", "duration": "8 weeks", "goals": ["Development"]}
            ],
            "sprints": [
                {"sprint_number": 1, "duration": "2 weeks", "story_points": 34, "deliverables": ["API skeleton"]}
            ],
            "milestones": [
                {"name": "MVP", "date": "2024-12-15", "deliverables": ["Core features"], "success_criteria": ["Tests pass"]}
            ],
            "prioritization": {
                "must_have": ["User auth"],
                "should_have": ["Dashboard"],
                "could_have": ["Analytics"],
                "wont_have": ["Mobile app"]
            },
            "effort_estimation": {
                "total_story_points": 144,
                "total_hours": 1152,
                "confidence_level": "high"
            },
            "dependencies": [{"task": "API", "depends_on": ["Database"]}],
            "team_requirements": {
                "roles": ["Backend Dev", "Frontend Dev"],
                "skills": ["Python", "React"],
                "team_size": 3
            },
            "timeline": {
                "start_date": "2024-11-01",
                "end_date": "2025-02-28",
                "total_weeks": 16,
                "buffer_weeks": 2
            },
            "risks_timeline": [{"risk": "Resource shortage", "when": "Week 8"}]
        })
        mock_bedrock_client.set_mock_response("plan", mock_response)
        
        # Execute agent
        agent = PlanningAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'analysis_data': sample_analysis_data
        })
        
        # Assertions
        assert result['status'] == 'completed'
        assert result['project_id'] == sample_project_id
        assert result['agent_id'] == agent.agent_id
        assert 'phases' in result
        assert len(result['phases']) == 2
        assert 'sprints' in result
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
    async def test_execute_with_constraints(self, sample_project_id, sample_analysis_data):
        """Test planning with time/budget constraints"""
        constraints = {
            "budget": 50000,
            "timeline_weeks": 12,
            "team_size": 2
        }
        
        agent = PlanningAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'analysis_data': sample_analysis_data,
            'constraints': constraints
        })
        
        assert result['status'] == 'completed'
        assert result['constraints_applied'] == constraints
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_with_s3_uri(self, sample_project_id, sample_analysis_data):
        """Test planning with analysis data from S3"""
        # Store analysis data in mock S3
        s3_uri = await mock_s3_client.upload_json(
            bucket="test-bucket",
            key=f"{sample_project_id}/analysis/test.json",
            data=sample_analysis_data
        )
        
        agent = PlanningAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'analysis_s3_uri': s3_uri
        })
        
        assert result['status'] == 'completed'
        
        # Verify S3 was read
        assert mock_s3_client.download_count == 1
    
    async def test_execute_missing_project_id(self, sample_analysis_data):
        """Test execution fails without project_id"""
        agent = PlanningAgent()
        
        with pytest.raises(ValueError) as exc_info:
            await agent.execute({'analysis_data': sample_analysis_data})
        
        assert 'project_id' in str(exc_info.value)
    
    async def test_execute_missing_analysis_data(self, sample_project_id):
        """Test execution fails without analysis data"""
        agent = PlanningAgent()
        
        with pytest.raises(ValueError) as exc_info:
            await agent.execute({'project_id': sample_project_id})
        
        assert 'analysis data' in str(exc_info.value).lower()
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_failure_publishes_event(self, sample_project_id, sample_analysis_data):
        """Test that failure events are published on errors"""
        # Save original method
        from tests.mocks.aws_mocks import MockBedrockClient
        original_invoke = MockBedrockClient.invoke_claude
        
        # Make bedrock raise an exception
        async def failing_invoke(*args, **kwargs):
            raise Exception("Planning AI error")
        
        mock_bedrock_client.invoke_claude = failing_invoke
        
        agent = PlanningAgent()
        
        try:
            with pytest.raises(Exception):
                await agent.execute({
                    'project_id': sample_project_id,
                    'analysis_data': sample_analysis_data
                })
            
            # Verify failure event was published
            failed_events = mock_eventbridge_client.get_events_by_type('planning.failed')
            assert len(failed_events) == 1
            assert failed_events[0]['detail']['project_id'] == sample_project_id
        finally:
            # Restore original method
            mock_bedrock_client.invoke_claude = original_invoke
    
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    async def test_get_roadmap_summary_success(self, sample_project_id, sample_planning_data):
        """Test retrieving roadmap summary"""
        # Create agent
        agent = PlanningAgent(agent_id='test-planning-agent')
        
        # Store planning data
        s3_uri = await mock_s3_client.upload_json(
            bucket="test-bucket",
            key=f"{sample_project_id}/planning/test.json",
            data=sample_planning_data
        )
        
        # Save state
        await mock_dynamodb_client.put_item(
            table_name="AgentStates",
            item={
                'project_id': sample_project_id,
                'agent_id': agent.agent_id,
                'agent_type': 'PlanningAgent',
                'state': {'last_planning': s3_uri},
                'updated_at': '2024-01-01T00:00:00'
            }
        )
        
        summary = await agent.get_roadmap_summary(sample_project_id)
        
        assert summary is not None
        assert 'Implementation Roadmap:' in summary
        assert 'Duration:' in summary
    
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    async def test_get_roadmap_summary_no_state(self, sample_project_id):
        """Test summary returns None when no state exists"""
        agent = PlanningAgent()
        summary = await agent.get_roadmap_summary(sample_project_id)
        
        assert summary is None
    
    def test_system_prompt_defined(self):
        """Test that SYSTEM_PROMPT is properly defined"""
        assert hasattr(PlanningAgent, 'SYSTEM_PROMPT')
        assert len(PlanningAgent.SYSTEM_PROMPT) > 0
        assert 'planning' in PlanningAgent.SYSTEM_PROMPT.lower()
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_ai_temperature_setting(self, sample_project_id, sample_analysis_data):
        """Test that planning uses appropriate temperature"""
        agent = PlanningAgent()
        
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
                'analysis_data': sample_analysis_data
            })
            
            assert temperature_used is not None
            assert 0.4 <= temperature_used <= 0.6  # Planning should use balanced temperature
        finally:
            mock_bedrock_client.invoke_claude = original_invoke
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_json_parsing_success(self, sample_project_id, sample_analysis_data):
        """Test JSON parsing success"""
        mock_bedrock_client.mock_responses.clear()
        
        # Mock complete response
        mock_response = json.dumps({
            "phases": [{"name": "Phase 1", "duration": "2 weeks", "goals": ["Setup"]}],
            "sprints": [{"sprint_number": 1, "story_points": 21}],
            "milestones": [{"name": "MVP", "date": "2024-12-01"}],
            "prioritization": {"must_have": [], "should_have": [], "could_have": [], "wont_have": []},
            "effort_estimation": {"total_story_points": 89, "confidence_level": "medium"},
            "dependencies": [],
            "team_requirements": {"team_size": 3},
            "timeline": {"total_weeks": 12},
            "risks_timeline": []
        })
        mock_bedrock_client.set_mock_response("roadmap", mock_response)
        
        agent = PlanningAgent()
        result = await agent.execute({
            'project_id': sample_project_id,
            'analysis_data': sample_analysis_data
        })
        
        assert len(result['phases']) == 1
        assert result['phases'][0]['name'] == 'Phase 1'
