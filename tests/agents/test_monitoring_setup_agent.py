"""
Tests for MonitoringSetupAgent
"""

import pytest
from unittest.mock import patch
from agentic_services.agents.monitoring_setup import MonitoringSetupAgent
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
async def test_monitoring_setup_agent_initialization():
    """Test that MonitoringSetupAgent initializes correctly"""
    agent = MonitoringSetupAgent()
    
    assert agent.agent_id is not None
    assert agent.agent_type == "monitoring_setup"
    assert agent.optimization_data is None


@pytest.mark.asyncio
async def test_monitoring_setup_agent_with_custom_id():
    """Test MonitoringSetupAgent initialization with custom agent_id"""
    custom_id = "test-dependency-mapper-123"
    agent = MonitoringSetupAgent(agent_id=custom_id)
    
    assert agent.agent_id == custom_id
    assert agent.agent_type == "monitoring_setup"


@pytest.mark.asyncio
async def test_monitoring_setup_execution():
    """Test successful dependency mapping execution"""
    agent = MonitoringSetupAgent()
    
    task = {
        'project_id': 'project-123',
        'monitoring_requirements': [
            {
                'name': 'web-app',
                'manifest_file': 'package.json',
                'dependencies': {
                    'express': '4.18.0',
                    'react': '18.2.0'
                }
            },
            {
                'name': 'api-service',
                'manifest_file': 'requirements.txt',
                'dependencies': {
                    'flask': '2.3.0',
                    'sqlalchemy': '2.0.0'
                }
            }
        ]
    }
    
    result = await agent.execute(task)
    
    # Verify result structure
    assert result['status'] == 'completed'
    assert result['agent_id'] == agent.agent_id
    assert result['project_id'] == 'project-123'
    assert 'monitoring_requirements' in result
    assert 'dependency_graph' in result
    assert 'recommendations' in result
    assert 'total_dependencies' in result
    assert 's3_uri' in result
    assert 'timestamp' in result


@pytest.mark.asyncio
async def test_monitoring_setup_with_transitive_deps():
    """Test dependency mapping including transitive dependencies"""
    agent = MonitoringSetupAgent()
    
    task = {
        'project_id': 'project-456',
        'monitoring_requirements': [{
            'name': 'complex-app',
            'dependencies': {
                'django': '4.2.0'
            }
        }],
        'include_transitive': True
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'
    assert result['project_id'] == 'project-456'


@pytest.mark.asyncio
async def test_monitoring_setup_circular_detection():
    """Test circular dependency detection"""
    agent = MonitoringSetupAgent()
    
    task = {
        'project_id': 'project-789',
        'monitoring_requirements': [{
            'name': 'service-a',
            'depends_on': ['service-b']
        }, {
            'name': 'service-b',
            'depends_on': ['service-c']
        }, {
            'name': 'service-c',
            'depends_on': ['service-a']  # Circular!
        }],
        'detect_circular': True
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'
    assert 'circular_dependencies' in result


@pytest.mark.asyncio
async def test_monitoring_setup_compatibility_assessment():
    """Test cloud compatibility assessment"""
    agent = MonitoringSetupAgent()
    
    task = {
        'project_id': 'project-101',
        'monitoring_requirements': [{
            'name': 'legacy-app',
            'dependencies': {
                'old-lib': '1.0.0'
            }
        }],
        'assess_compatibility': True
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'
    assert 'compatibility_assessment' in result


@pytest.mark.asyncio
async def test_monitoring_setup_vulnerability_check():
    """Test security vulnerability identification"""
    agent = MonitoringSetupAgent()
    
    task = {
        'project_id': 'project-202',
        'monitoring_requirements': [{
            'name': 'secure-app',
            'dependencies': {
                'vulnerable-lib': '0.9.0'
            }
        }],
        'identify_vulnerabilities': True
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'
    assert 'vulnerability_summary' in result


@pytest.mark.asyncio
async def test_monitoring_setup_critical_paths():
    """Test critical path identification"""
    agent = MonitoringSetupAgent()
    
    task = {
        'project_id': 'project-303',
        'monitoring_requirements': [{
            'name': 'app-1',
            'depends_on': ['database', 'cache', 'auth-service']
        }]
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'
    assert 'critical_paths' in result


@pytest.mark.asyncio
async def test_monitoring_setup_missing_project_id():
    """Test error handling when project_id is missing"""
    agent = MonitoringSetupAgent()
    
    task = {
        'monitoring_requirements': [{'name': 'app'}]
    }
    
    with pytest.raises(ValueError, match="project_id is required"):
        await agent.execute(task)


@pytest.mark.asyncio
async def test_monitoring_setup_missing_monitoring_requirements():
    """Test error handling when monitoring_requirements are missing"""
    agent = MonitoringSetupAgent()
    
    task = {
        'project_id': 'project-404'
    }
    
    with pytest.raises(ValueError, match="monitoring_requirements is required"):
        await agent.execute(task)


@pytest.mark.asyncio
async def test_monitoring_setup_empty_monitoring_requirements():
    """Test handling of empty monitoring_requirements list"""
    agent = MonitoringSetupAgent()
    
    task = {
        'project_id': 'project-505',
        'monitoring_requirements': []
    }
    
    with pytest.raises(ValueError, match="monitoring_requirements is required"):
        await agent.execute(task)


@pytest.mark.asyncio
async def test_monitoring_setup_state_persistence():
    """Test that mapping state is persisted to DynamoDB"""
    agent = MonitoringSetupAgent()
    
    task = {
        'project_id': 'project-606',
        'monitoring_requirements': [{'name': 'test-app'}]
    }
    
    result = await agent.execute(task)
    
    # Verify state was saved
    mock_dynamodb = agent.dynamodb
    saved_state = mock_dynamodb.get_state('project-606', agent.agent_id)
    
    assert saved_state is not None
    assert saved_state['last_mapping']['project_id'] == 'project-606'
    assert saved_state['application_count'] == 1


@pytest.mark.asyncio
async def test_monitoring_setup_event_emission():
    """Test that appropriate events are emitted during mapping"""
    agent = MonitoringSetupAgent()
    
    task = {
        'project_id': 'project-707',
        'monitoring_requirements': [{'name': 'app-1'}, {'name': 'app-2'}]
    }
    
    result = await agent.execute(task)
    
    # Verify events were emitted
    mock_eventbridge = agent.eventbridge
    events = mock_eventbridge.get_events()
    
    event_types = [e['DetailType'] for e in events]
    assert 'monitoring_setup.started' in event_types
    assert 'monitoring_setup.completed' in event_types


@pytest.mark.asyncio
async def test_monitoring_setup_error_event():
    """Test that error events are emitted on failure"""
    agent = MonitoringSetupAgent()
    
    # Make Bedrock fail
    agent.bedrock.should_fail = True
    
    task = {
        'project_id': 'project-808',
        'monitoring_requirements': [{'name': 'app'}]
    }
    
    with pytest.raises(Exception):
        await agent.execute(task)
    
    # Verify error event was emitted
    mock_eventbridge = agent.eventbridge
    events = mock_eventbridge.get_events()
    
    error_events = [e for e in events if 'failed' in e['DetailType']]
    assert len(error_events) > 0


@pytest.mark.asyncio
async def test_get_optimization_data():
    """Test retrieving dependency mapping data"""
    agent = MonitoringSetupAgent()
    
    # Before execution
    assert agent.get_optimization_data() is None
    
    # After execution
    task = {
        'project_id': 'project-909',
        'monitoring_requirements': [{'name': 'app'}]
    }
    
    result = await agent.execute(task)
    
    optimization_data = agent.get_optimization_data()
    assert optimization_data is not None
    assert optimization_data['project_id'] == 'project-909'
    assert optimization_data == result
