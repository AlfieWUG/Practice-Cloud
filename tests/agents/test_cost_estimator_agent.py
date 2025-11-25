"""
Tests for CostEstimatorAgent
"""

import pytest
import json
from unittest.mock import patch
from agentic_services.agents.cost_estimator import CostEstimatorAgent
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
async def test_cost_estimator_initialization():
    """Test that CostEstimatorAgent initializes correctly"""
    agent = CostEstimatorAgent()
    
    assert agent.agent_id is not None
    assert agent.agent_type == "cost_estimator"
    assert agent.cost_data is None


@pytest.mark.asyncio
async def test_cost_estimator_with_custom_id():
    """Test CostEstimatorAgent initialization with custom agent_id"""
    custom_id = "test-compliance-checker-123"
    agent = CostEstimatorAgent(agent_id=custom_id)
    
    assert agent.agent_id == custom_id
    assert agent.agent_type == "cost_estimator"


@pytest.mark.asyncio
async def test_cost_estimation_execution():
    """Test successful compliance checking execution"""
    agent = CostEstimatorAgent()
    
    task = {
        'project_id': 'project-123',
        'infrastructure': {
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
async def test_gdpr_cost_estimation():
    """Test GDPR compliance validation"""
    agent = CostEstimatorAgent()
    
    cost_data = {
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
    
    mock_bedrock_client.set_mock_response("compliance", json.dumps(cost_data))
    
    task = {
        'project_id': 'project-456',
        'infrastructure': {'eu_data': True},
        'target_cloud': 'AWS',
        'check_gdpr': True
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'
    assert 'GDPR' in str(result['compliance_frameworks'])


@pytest.mark.asyncio
async def test_hipaa_cost_estimation():
    """Test HIPAA compliance validation"""
    agent = CostEstimatorAgent()
    
    task = {
        'project_id': 'project-789',
        'infrastructure': {'phi_detected': True},
        'target_cloud': 'AWS',
        'check_hipaa': True,
        'industry': 'healthcare'
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'
    assert result['project_id'] == 'project-789'


@pytest.mark.asyncio
async def test_pci_dss_cost_estimation():
    """Test PCI-DSS compliance validation"""
    agent = CostEstimatorAgent()
    
    task = {
        'project_id': 'project-101',
        'infrastructure': {'credit_card_data': True},
        'target_cloud': 'AWS',
        'check_pci_dss': True,
        'industry': 'finance'
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'


@pytest.mark.asyncio
async def test_soc2_cost_estimation():
    """Test SOC 2 compliance validation"""
    agent = CostEstimatorAgent()
    
    task = {
        'project_id': 'project-202',
        'infrastructure': {'customer_data': True},
        'target_cloud': 'AWS',
        'check_soc2': True
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'


@pytest.mark.asyncio
async def test_multi_framework_check():
    """Test multiple compliance frameworks check"""
    agent = CostEstimatorAgent()
    
    task = {
        'project_id': 'project-303',
        'infrastructure': {'pii': True, 'phi': True},
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
    agent = CostEstimatorAgent()
    
    task = {
        'infrastructure': {}
    }
    
    with pytest.raises(ValueError, match="project_id is required"):
        await agent.execute(task)


@pytest.mark.asyncio
async def test_compliance_missing_infrastructure():
    """Test error handling when infrastructure is missing"""
    agent = CostEstimatorAgent()
    
    task = {
        'project_id': 'project-404'
    }
    
    with pytest.raises(ValueError, match="infrastructure is required"):
        await agent.execute(task)


@pytest.mark.asyncio
async def test_compliance_state_persistence():
    """Test that compliance check state is persisted to DynamoDB"""
    agent = CostEstimatorAgent()
    
    task = {
        'project_id': 'project-606',
        'infrastructure': {'data': 'test'}
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
    agent = CostEstimatorAgent()
    
    task = {
        'project_id': 'project-707',
        'infrastructure': {'test': 'data'},
        'target_cloud': 'Azure'
    }
    
    result = await agent.execute(task)
    
    # Verify events were emitted
    mock_eventbridge = agent.eventbridge
    events = mock_eventbridge.get_events()
    
    event_types = [e['DetailType'] for e in events]
    assert 'cost_estimation.started' in event_types
    assert 'cost_estimation.completed' in event_types


@pytest.mark.asyncio
async def test_compliance_error_event():
    """Test that error events are emitted on failure"""
    agent = CostEstimatorAgent()
    
    # Make Bedrock fail
    agent.bedrock.should_fail = True
    
    task = {
        'project_id': 'project-808',
        'infrastructure': {'data': 'test'}
    }
    
    with pytest.raises(Exception):
        await agent.execute(task)
    
    # Verify error event was emitted
    mock_eventbridge = agent.eventbridge
    events = mock_eventbridge.get_events()
    
    error_events = [e for e in events if 'failed' in e['DetailType']]
    assert len(error_events) > 0


@pytest.mark.asyncio
async def test_get_cost_data():
    """Test retrieving compliance check data"""
    agent = CostEstimatorAgent()
    
    # Before execution
    assert agent.get_cost_data() is None
    
    # After execution
    task = {
        'project_id': 'project-909',
        'infrastructure': {'data': 'test'}
    }
    
    result = await agent.execute(task)
    
    cost_data = agent.get_cost_data()
    assert cost_data is not None
    assert cost_data['project_id'] == 'project-909'
    assert cost_data == result


@pytest.mark.asyncio
async def test_target_cloud_defaults_to_aws():
    """Test that target_cloud defaults to AWS if not specified"""
    agent = CostEstimatorAgent()
    
    task = {
        'project_id': 'project-111',
        'infrastructure': {'data': 'test'}
    }
    
    result = await agent.execute(task)
    
    assert result['target_cloud'] == 'AWS'
