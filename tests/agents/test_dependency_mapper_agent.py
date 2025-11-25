"""
Tests for DependencyMapperAgent
"""

import pytest
from unittest.mock import patch
from agentic_services.agents.dependency_mapper import DependencyMapperAgent
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
async def test_dependency_mapper_agent_initialization():
    """Test that DependencyMapperAgent initializes correctly"""
    agent = DependencyMapperAgent()
    
    assert agent.agent_id is not None
    assert agent.agent_type == "dependency_mapper"
    assert agent.dependency_data is None


@pytest.mark.asyncio
async def test_dependency_mapper_agent_with_custom_id():
    """Test DependencyMapperAgent initialization with custom agent_id"""
    custom_id = "test-dependency-mapper-123"
    agent = DependencyMapperAgent(agent_id=custom_id)
    
    assert agent.agent_id == custom_id
    assert agent.agent_type == "dependency_mapper"


@pytest.mark.asyncio
async def test_dependency_mapping_execution():
    """Test successful dependency mapping execution"""
    agent = DependencyMapperAgent()
    
    task = {
        'project_id': 'project-123',
        'applications': [
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
    assert 'applications' in result
    assert 'dependency_graph' in result
    assert 'recommendations' in result
    assert 'total_dependencies' in result
    assert 's3_uri' in result
    assert 'timestamp' in result


@pytest.mark.asyncio
async def test_dependency_mapping_with_transitive_deps():
    """Test dependency mapping including transitive dependencies"""
    agent = DependencyMapperAgent()
    
    task = {
        'project_id': 'project-456',
        'applications': [{
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
async def test_dependency_mapping_circular_detection():
    """Test circular dependency detection"""
    agent = DependencyMapperAgent()
    
    task = {
        'project_id': 'project-789',
        'applications': [{
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
async def test_dependency_mapping_compatibility_assessment():
    """Test cloud compatibility assessment"""
    agent = DependencyMapperAgent()
    
    task = {
        'project_id': 'project-101',
        'applications': [{
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
async def test_dependency_mapping_vulnerability_check():
    """Test security vulnerability identification"""
    agent = DependencyMapperAgent()
    
    task = {
        'project_id': 'project-202',
        'applications': [{
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
async def test_dependency_mapping_critical_paths():
    """Test critical path identification"""
    agent = DependencyMapperAgent()
    
    task = {
        'project_id': 'project-303',
        'applications': [{
            'name': 'app-1',
            'depends_on': ['database', 'cache', 'auth-service']
        }]
    }
    
    result = await agent.execute(task)
    
    assert result['status'] == 'completed'
    assert 'critical_paths' in result


@pytest.mark.asyncio
async def test_dependency_mapping_missing_project_id():
    """Test error handling when project_id is missing"""
    agent = DependencyMapperAgent()
    
    task = {
        'applications': [{'name': 'app'}]
    }
    
    with pytest.raises(ValueError, match="project_id is required"):
        await agent.execute(task)


@pytest.mark.asyncio
async def test_dependency_mapping_missing_applications():
    """Test error handling when applications are missing"""
    agent = DependencyMapperAgent()
    
    task = {
        'project_id': 'project-404'
    }
    
    with pytest.raises(ValueError, match="applications is required"):
        await agent.execute(task)


@pytest.mark.asyncio
async def test_dependency_mapping_empty_applications():
    """Test handling of empty applications list"""
    agent = DependencyMapperAgent()
    
    task = {
        'project_id': 'project-505',
        'applications': []
    }
    
    with pytest.raises(ValueError, match="applications is required"):
        await agent.execute(task)


@pytest.mark.asyncio
async def test_dependency_mapping_state_persistence():
    """Test that mapping state is persisted to DynamoDB"""
    agent = DependencyMapperAgent()
    
    task = {
        'project_id': 'project-606',
        'applications': [{'name': 'test-app'}]
    }
    
    result = await agent.execute(task)
    
    # Verify state was saved
    mock_dynamodb = agent.dynamodb
    saved_state = mock_dynamodb.get_state('project-606', agent.agent_id)
    
    assert saved_state is not None
    assert saved_state['last_mapping']['project_id'] == 'project-606'
    assert saved_state['application_count'] == 1


@pytest.mark.asyncio
async def test_dependency_mapping_event_emission():
    """Test that appropriate events are emitted during mapping"""
    agent = DependencyMapperAgent()
    
    task = {
        'project_id': 'project-707',
        'applications': [{'name': 'app-1'}, {'name': 'app-2'}]
    }
    
    result = await agent.execute(task)
    
    # Verify events were emitted
    mock_eventbridge = agent.eventbridge
    events = mock_eventbridge.get_events()
    
    event_types = [e['DetailType'] for e in events]
    assert 'dependency_mapping.started' in event_types
    assert 'dependency_mapping.completed' in event_types


@pytest.mark.asyncio
async def test_dependency_mapping_error_event():
    """Test that error events are emitted on failure"""
    agent = DependencyMapperAgent()
    
    # Make Bedrock fail
    agent.bedrock.should_fail = True
    
    task = {
        'project_id': 'project-808',
        'applications': [{'name': 'app'}]
    }
    
    with pytest.raises(Exception):
        await agent.execute(task)
    
    # Verify error event was emitted
    mock_eventbridge = agent.eventbridge
    events = mock_eventbridge.get_events()
    
    error_events = [e for e in events if 'failed' in e['DetailType']]
    assert len(error_events) > 0


@pytest.mark.asyncio
async def test_get_dependency_data():
    """Test retrieving dependency mapping data"""
    agent = DependencyMapperAgent()
    
    # Before execution
    assert agent.get_dependency_data() is None
    
    # After execution
    task = {
        'project_id': 'project-909',
        'applications': [{'name': 'app'}]
    }
    
    result = await agent.execute(task)
    
    dependency_data = agent.get_dependency_data()
    assert dependency_data is not None
    assert dependency_data['project_id'] == 'project-909'
    assert dependency_data == result
