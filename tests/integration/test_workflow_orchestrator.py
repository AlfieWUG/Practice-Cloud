"""
Integration tests for WorkflowOrchestrator
"""

import pytest
import json
from unittest.mock import patch

from agentic_services.orchestrator.workflow import WorkflowOrchestrator, WorkflowStatus
from tests.mocks import (
    mock_bedrock_client,
    mock_s3_client,
    mock_dynamodb_client,
    mock_eventbridge_client,
)


@pytest.mark.asyncio
class TestWorkflowOrchestrator:
    """End-to-end workflow tests using mock AWS services"""

    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_full_workflow_success(self, sample_requirements):
        """Run full workflow and verify chaining and outputs"""
        project_id = "wf-proj-001"

        # Configure Bedrock mock responses for each agent
        mock_bedrock_client.mock_responses.clear()

        # Discovery matches on 'project requirements'
        mock_bedrock_client.set_mock_response(
            "project requirements",
            json.dumps({
                "project_type": "web_app",
                "technology_stack": {"languages": ["Python"], "frameworks": ["FastAPI"], "databases": ["PostgreSQL"]},
                "components": ["API", "DB"],
                "requirements": {"functional": ["Auth"], "non_functional": ["Security"]},
                "dependencies": ["Docker"],
                "constraints": [],
                "assumptions": []
            })
        )

        # Analysis matches on 'technical analysis'
        mock_bedrock_client.set_mock_response(
            "technical analysis",
            json.dumps({
                "complexity_assessment": {"level": "medium", "reasoning": "Standard app"},
                "technical_challenges": [],
                "recommended_architecture": {"pattern": "microservices", "reasoning": "scalability"},
                "scalability_analysis": {},
                "security_considerations": [],
                "performance_requirements": {},
                "integration_points": [],
                "best_practices": [],
                "risk_assessment": []
            })
        )

        # Planning matches on 'implementation plan'
        mock_bedrock_client.set_mock_response(
            "implementation plan",
            json.dumps({
                "phases": [{"name": "Phase 1", "duration": "2 weeks", "goals": ["Setup"]}],
                "sprints": [{"sprint_number": 1, "story_points": 13}],
                "milestones": [{"name": "MVP", "date": "2025-01-01"}],
                "prioritization": {"must_have": ["Auth"], "should_have": [], "could_have": [], "wont_have": []},
                "effort_estimation": {"total_story_points": 55, "total_hours": 440, "confidence_level": "medium"},
                "dependencies": [],
                "team_requirements": {"team_size": 2},
                "timeline": {"total_weeks": 8},
                "risks_timeline": []
            })
        )

        # Artifacts matches on 'project artifacts'
        mock_bedrock_client.set_mock_response(
            "project artifacts",
            json.dumps({
                "artifacts": [
                    {"type": "code", "filename": "main.py", "content": "print('ok')"}
                ],
                "structure": {},
                "documentation": {},
                "configurations": {},
                "code_templates": [],
                "database_schemas": [],
                "api_specifications": {},
                "testing_templates": []
            })
        )

        orch = WorkflowOrchestrator()
        results = await orch.execute_full_workflow(
            project_id=project_id,
            requirements=sample_requirements,
            context="demo",
            constraints={"timeline_weeks": 8}
        )

        # Assertions
        assert results["status"] == WorkflowStatus.COMPLETED.value
        assert results["project_id"] == project_id
        assert results["agents_executed"] == [
            'DiscoveryAgent', 'AnalysisAgent', 'PlanningAgent', 'ArtifactGenerationAgent'
        ]

        # Ensure each phase produced outputs with s3_uri
        assert results["discovery"]["s3_uri"].startswith("s3://")
        assert results["analysis"]["s3_uri"].startswith("s3://")
        assert results["planning"]["s3_uri"].startswith("s3://")
        assert results["artifacts"]["s3_uri"].startswith("s3://")

        # EventBridge: each agent emits started+completed => 8 events
        assert mock_eventbridge_client.event_count >= 8

        # Orchestrator execution log has 4 completed steps
        assert len(results["execution_log"]) == 4
        assert all(step["status"] == "completed" for step in results["execution_log"])

    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_full_workflow_failure_in_analysis_sets_failed(self, sample_requirements):
        """Force analysis failure and verify orchestrator status and logging"""
        project_id = "wf-proj-err"

        # Discovery successful
        mock_bedrock_client.mock_responses.clear()
        mock_bedrock_client.set_mock_response(
            "project requirements",
            json.dumps({
                "project_type": "web_app",
                "technology_stack": {"languages": ["Python"]},
                "components": [],
                "requirements": {"functional": [], "non_functional": []},
                "dependencies": [],
                "constraints": [],
                "assumptions": []
            })
        )

        # Make analysis invocation raise
        from tests.mocks.aws_mocks import MockBedrockClient
        original_invoke = MockBedrockClient.invoke_claude

        async def failing_invoke(self_mock, *args, **kwargs):
            raise Exception("Simulated analysis failure")

        # Bind failing method
        mock_bedrock_client.invoke_claude = lambda *args, **kwargs: failing_invoke(mock_bedrock_client, *args, **kwargs)

        orch = WorkflowOrchestrator()
        with pytest.raises(Exception):
            await orch.execute_full_workflow(
                project_id=project_id,
                requirements=sample_requirements
            )

        # Orchestrator should be in FAILED state
        assert orch.status == WorkflowStatus.FAILED

        # Restore
        mock_bedrock_client.invoke_claude = original_invoke.__get__(mock_bedrock_client, MockBedrockClient)
