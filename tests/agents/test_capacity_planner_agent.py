"""
Tests for CapacityPlannerAgent
"""

import pytest
import json
from unittest.mock import patch
from agentic_services.agents.capacity_planner import CapacityPlannerAgent
from tests.mocks import (
    mock_bedrock_client,
    mock_s3_client,
    mock_dynamodb_client,
    mock_eventbridge_client,
)


# Ensure BaseAgent references use mocks for all tests in this module
@pytest.fixture(autouse=True)
def patch_base_clients():
    with patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client), \
         patch('agentic_services.agents.base.s3_client', mock_s3_client), \
         patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client), \
         patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client):
        yield


@pytest.mark.asyncio
async def test_capacity_planner_initialization():
    """Test that CapacityPlannerAgent initializes correctly"""
    agent = CapacityPlannerAgent()
    
    assert agent.agent_id is not None
    assert agent.agent_type == "capacity_planner"
    assert agent.capacity_data is None


@pytest.mark.asyncio
async def test_capacity_planner_with_custom_id():
    """Test CapacityPlannerAgent initialization with custom agent_id"""
    custom_id = "test-compliance-checker-123"
    agent = CapacityPlannerAgent(agent_id=custom_id)
    
    assert agent.agent_id == custom_id
    assert agent.agent_type == "capacity_planner"


@pytest.mark.asyncio
async def test_capacity_planning_execution():
    """Test successful compliance checking execution"""
    agent = CapacityPlannerAgent()
    
    task = {
        'project_id': 'project-123',
        'current_capacity': {}, 'performance_requirements': {
            'pii_detected': True,
            'sensitive_data': True
        },
        'target_cloud': 'AWS'
    }
    
    result = await agent.execute(task)
    
    # Verify result structure
    assert result['status'] == 'completed'
    assert result['agent_id'] == agent.agent_id
    assert result['project_id'] == 'project-123'
    assert result['target_cloud'] == 'AWS'
    assert 'compliance_frameworks' in result
    assert 'gaps' in result
    assert 'overall_compliance_score' in result
    assert 'recommendations' in result
    assert 's3_uri' in result
    assert 'timestamp' in result


@pytest.mark.asyncio
async def test_gdpr_capacity_planning():
    """Test GDPR compliance validation"""
    agent = CapacityPlannerAgent()
    
    capacity_data = {
        'compliance_frameworks': {
            'GDPR': {
                'applicable': True,
                'current_status': 'partial',
                'compliance_score': 65,
                'missing_controls': ['data_subject_rights', 'dpia']
            }
        },
        'gaps': [
            {
                'framework': 'GDPR',
                'requirement': 'Data subject rights',
                'severity': 'high'
            }
        ],
        'overall_compliance_score': 65
    }
    
    mock_bedrock_client.set_mock_response("compliance", json.dumps(capacity_data))
    
    task = {
        'project_id': 'project-456',
        'current_capacity': {}, 'performance_requirements': {'eu_data': True},
        'target_cloud': 'AWS',
        'check_gdpr': True
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'
    assert 'GDPR' in str(result['compliance_frameworks'])


@pytest.mark.asyncio
async def test_hipaa_capacity_planning():
    """Test HIPAA compliance validation"""
    agent = CapacityPlannerAgent()
    
    task = {
        'project_id': 'project-789',
        'current_capacity': {}, 'performance_requirements': {'phi_detected': True},
        'target_cloud': 'AWS',
        'check_hipaa': True,
        'industry': 'healthcare'
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'
    assert result['project_id'] == 'project-789'


@pytest.mark.asyncio
async def test_pci_dss_capacity_planning():
    """Test PCI-DSS compliance validation"""
    agent = CapacityPlannerAgent()
    
    task = {
        'project_id': 'project-101',
        'current_capacity': {}, 'performance_requirements': {'credit_card_data': True},
        'target_cloud': 'AWS',
        'check_pci_dss': True,
        'industry': 'finance'
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'


@pytest.mark.asyncio
async def test_soc2_capacity_planning():
    """Test SOC 2 compliance validation"""
    agent = CapacityPlannerAgent()
    
    task = {
        'project_id': 'project-202',
        'current_capacity': {}, 'performance_requirements': {'customer_data': True},
        'target_cloud': 'AWS',
        'check_soc2': True
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'


@pytest.mark.asyncio
async def test_multi_framework_check():
    """Test multiple compliance frameworks check"""
    agent = CapacityPlannerAgent()
    
    task = {
        'project_id': 'project-303',
        'current_capacity': {}, 'performance_requirements': {'pii': True, 'phi': True},
        'target_cloud': 'AWS',
        'check_gdpr': True,
        'check_hipaa': True,
        'check_soc2': True
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'


@pytest.mark.asyncio
async def test_compliance_missing_project_id():
    """Test error handling when project_id is missing"""
    agent = CapacityPlannerAgent()
    
    task = {
        'current_capacity': {}, 'performance_requirements': {}
    }
    
    with pytest.raises(ValueError, match="project_id is required"):
        await agent.execute(task)


@pytest.mark.asyncio
async def test_compliance_missing_current_capacity():
    """Test error handling when current_capacity is missing"""
    agent = CapacityPlannerAgent()
    
    task = {
        'project_id': 'project-404'
    }
    
    with pytest.raises(ValueError, match="current_capacity is required"):
        await agent.execute(task)


@pytest.mark.asyncio
async def test_compliance_state_persistence():
    """Test that compliance check state is persisted to DynamoDB"""
    agent = CapacityPlannerAgent()
    
    task = {
        'project_id': 'project-606',
        'current_capacity': {}, 'performance_requirements': {'data': 'test'}
    }
    
    result = await agent.execute(task)
    
    # Verify state was saved
    mock_dynamodb = agent.dynamodb
    saved_state = mock_dynamodb.get_state('project-606', agent.agent_id)
    
    assert saved_state is not None
    assert saved_state['last_check']['project_id'] == 'project-606'


@pytest.mark.asyncio
async def test_compliance_event_emission():
    """Test that appropriate events are emitted during compliance check"""
    agent = CapacityPlannerAgent()
    
    task = {
        'project_id': 'project-707',
        'current_capacity': {}, 'performance_requirements': {'test': 'data'},
        'target_cloud': 'Azure'
    }
    
    result = await agent.execute(task)
    
    # Verify events were emitted
    mock_eventbridge = agent.eventbridge
    events = mock_eventbridge.get_events()
    
    event_types = [e['DetailType'] for e in events]
    assert 'capacity_planning.started' in event_types
    assert 'capacity_planning.completed' in event_types


@pytest.mark.asyncio
async def test_compliance_error_event():
    """Test that error events are emitted on failure"""
    agent = CapacityPlannerAgent()
    
    # Make Bedrock fail
    agent.bedrock.should_fail = True
    
    task = {
        'project_id': 'project-808',
        'current_capacity': {}, 'performance_requirements': {'data': 'test'}
    }
    
    with pytest.raises(Exception):
        await agent.execute(task)
    
    # Verify error event was emitted
    mock_eventbridge = agent.eventbridge
    events = mock_eventbridge.get_events()
    
    error_events = [e for e in events if 'failed' in e['DetailType']]
    assert len(error_events) > 0


@pytest.mark.asyncio
async def test_get_capacity_data():
    """Test retrieving compliance check data"""
    agent = CapacityPlannerAgent()
    
    # Before execution
    assert agent.get_capacity_data() is None
    
    # After execution
    task = {
        'project_id': 'project-909',
        'current_capacity': {}, 'performance_requirements': {'data': 'test'}
    }
    
    result = await agent.execute(task)
    
    capacity_data = agent.get_capacity_data()
    assert capacity_data is not None
    assert capacity_data['project_id'] == 'project-909'
    assert capacity_data == result


@pytest.mark.asyncio
async def test_target_cloud_defaults_to_aws():
    """Test that target_cloud defaults to AWS if not specified"""
    agent = CapacityPlannerAgent()
    
    task = {
        'project_id': 'project-111',
        'current_capacity': {}, 'performance_requirements': {'data': 'test'}
    }
    
    result = await agent.execute(task)
    
    assert result['target_cloud'] == 'AWS'
