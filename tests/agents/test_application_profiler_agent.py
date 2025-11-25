"""
Tests for ApplicationProfilerAgent
Tests application performance profiling, resource usage analysis, and scaling patterns
"""

import pytest
import json
from unittest.mock import patch
from agentic_services.agents.application_profiler import ApplicationProfilerAgent
from tests.mocks import mock_bedrock_client, mock_s3_client, mock_dynamodb_client, mock_eventbridge_client


@pytest.mark.asyncio
class TestApplicationProfilerAgent:
    """Test suite for ApplicationProfilerAgent"""
    
    async def test_initialization(self):
        """Test agent initializes correctly"""
        agent = ApplicationProfilerAgent()
        
        assert agent.agent_id is not None
        assert agent.agent_type == "application_profiler"
        assert agent.profile_data is None
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_success(self, sample_project_id):
        """Test successful application profiling"""
        agent = ApplicationProfilerAgent()
        
        # Mock AI response with profiling data
        profile_data = {
            "applications": [
                {
                    "name": "web-app",
                    "type": "web_application",
                    "technology": "Node.js",
                    "version": "18.16.0",
                    "performance": {
                        "avg_response_time_ms": 120,
                        "p95_response_time_ms": 450,
                        "p99_response_time_ms": 850,
                        "throughput_rps": 1200
                    },
                    "resource_usage": {
                        "cpu_avg_percent": 45,
                        "cpu_peak_percent": 78,
                        "memory_avg_mb": 2048,
                        "memory_peak_mb": 3584,
                        "disk_io_mbps": 25
                    }
                },
                {
                    "name": "api-service",
                    "type": "rest_api",
                    "technology": "Python/FastAPI",
                    "version": "0.95.0",
                    "performance": {
                        "avg_response_time_ms": 85,
                        "p95_response_time_ms": 280,
                        "throughput_rps": 2500
                    },
                    "resource_usage": {
                        "cpu_avg_percent": 32,
                        "memory_avg_mb": 1024
                    }
                }
            ],
            "total_applications": 2,
            "profiling_duration_hours": 24,
            "peak_load_time": "2025-01-15 14:00:00 UTC"
        }
        
        mock_bedrock_client.set_mock_response(
            "application profiling",
            json.dumps(profile_data)
        )
        
        # Execute profiling
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_servers': ['web-server-01', 'api-server-01'],
            'profiling_duration_hours': 24
        })
        
        # Verify results
        assert result['status'] == 'completed'
        assert result['project_id'] == sample_project_id
        assert 'applications' in result
        assert result['total_applications'] == 2
        assert len(result['applications']) == 2
        
        # Verify S3 storage
        assert 's3_uri' in result
        assert 'application_profile' in result['s3_uri']
        
        # Verify events emitted
        events = mock_eventbridge_client.get_events()
        assert len(events) >= 2
        assert any(e['DetailType'] == 'profiling.started' for e in events)
        assert any(e['DetailType'] == 'profiling.completed' for e in events)
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_with_scaling_analysis(self, sample_project_id):
        """Test profiling with scaling pattern analysis"""
        agent = ApplicationProfilerAgent()
        
        profile_data = {
            "applications": [
                {
                    "name": "ecommerce-app",
                    "scaling_patterns": {
                        "pattern_type": "predictable_peaks",
                        "peak_hours": [12, 13, 14, 18, 19, 20],
                        "baseline_rps": 500,
                        "peak_rps": 3500,
                        "scaling_factor": 7.0,
                        "recommended_autoscaling": {
                            "min_instances": 3,
                            "max_instances": 15,
                            "target_cpu_percent": 65
                        }
                    },
                    "resource_usage": {
                        "cpu_avg_percent": 55,
                        "memory_avg_mb": 4096
                    }
                }
            ],
            "total_applications": 1
        }
        
        mock_bedrock_client.set_mock_response(
            "scaling analysis",
            json.dumps(profile_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_servers': ['web-01'],
            'include_scaling_analysis': True
        })
        
        assert result['status'] == 'completed'
        assert 'scaling_patterns' in result['applications'][0]
        assert result['applications'][0]['scaling_patterns']['scaling_factor'] == 7.0
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_with_dependencies(self, sample_project_id):
        """Test profiling with dependency analysis"""
        agent = ApplicationProfilerAgent()
        
        profile_data = {
            "applications": [
                {
                    "name": "order-service",
                    "dependencies": {
                        "databases": [
                            {
                                "name": "orders_db",
                                "type": "PostgreSQL",
                                "query_frequency": 1500,
                                "avg_query_time_ms": 15
                            }
                        ],
                        "external_apis": [
                            {
                                "name": "payment-gateway",
                                "endpoint": "https://pay.example.com/api",
                                "call_frequency": 300,
                                "avg_response_time_ms": 250
                            }
                        ],
                        "internal_services": [
                            {
                                "name": "inventory-service",
                                "calls_per_minute": 800
                            }
                        ]
                    }
                }
            ],
            "total_applications": 1
        }
        
        mock_bedrock_client.set_mock_response(
            "dependency profiling",
            json.dumps(profile_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_servers': ['service-01'],
            'include_dependencies': True
        })
        
        assert result['status'] == 'completed'
        assert 'dependencies' in result['applications'][0]
        assert len(result['applications'][0]['dependencies']['databases']) == 1
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_with_bottlenecks(self, sample_project_id):
        """Test identification of performance bottlenecks"""
        agent = ApplicationProfilerAgent()
        
        profile_data = {
            "applications": [
                {
                    "name": "analytics-app",
                    "performance": {
                        "avg_response_time_ms": 1200,
                        "throughput_rps": 50
                    },
                    "bottlenecks": [
                        {
                            "type": "slow_database_queries",
                            "severity": "high",
                            "description": "Multiple N+1 query patterns detected",
                            "impact": "Adds 800ms average latency",
                            "recommendation": "Implement query result caching"
                        },
                        {
                            "type": "inefficient_algorithm",
                            "severity": "medium",
                            "description": "O(n²) sorting in data processing",
                            "impact": "CPU spikes to 95% on large datasets",
                            "recommendation": "Replace with optimized sorting algorithm"
                        }
                    ]
                }
            ],
            "total_applications": 1
        }
        
        mock_bedrock_client.set_mock_response(
            "bottleneck analysis",
            json.dumps(profile_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_servers': ['analytics-01'],
            'identify_bottlenecks': True
        })
        
        assert result['status'] == 'completed'
        assert 'bottlenecks' in result['applications'][0]
        assert len(result['applications'][0]['bottlenecks']) == 2
        assert result['applications'][0]['bottlenecks'][0]['severity'] == 'high'
    
    async def test_missing_project_id(self):
        """Test error handling when project_id is missing"""
        agent = ApplicationProfilerAgent()
        
        with pytest.raises(ValueError, match="project_id"):
            await agent.execute({
                'target_servers': ['server-01']
            })
    
    async def test_missing_target_servers(self):
        """Test error handling when target_servers is missing"""
        agent = ApplicationProfilerAgent()
        
        with pytest.raises(ValueError, match="target_servers"):
            await agent.execute({
                'project_id': 'test-project'
            })
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_failure(self, sample_project_id):
        """Test failure handling during profiling"""
        agent = ApplicationProfilerAgent()
        
        # Mock AI to raise exception
        mock_bedrock_client.should_fail = True
        
        with pytest.raises(Exception):
            await agent.execute({
                'project_id': sample_project_id,
                'target_servers': ['server-01']
            })
        
        # Verify failure event was emitted
        events = mock_eventbridge_client.get_events()
        assert any(e['DetailType'] == 'profiling.failed' for e in events)
        
        mock_bedrock_client.should_fail = False
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_json_parsing_fallback(self, sample_project_id):
        """Test JSON parsing fallback when AI returns markdown"""
        agent = ApplicationProfilerAgent()
        
        profile_data = {
            "applications": [{"name": "test-app", "type": "web"}],
            "total_applications": 1
        }
        
        # Return JSON in markdown code block
        markdown_response = f"```json\n{json.dumps(profile_data)}\n```"
        mock_bedrock_client.set_mock_response("profiling", markdown_response)
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_servers': ['server-01']
        })
        
        assert result['status'] == 'completed'
        assert 'applications' in result
        assert result['total_applications'] == 1
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_no_applications_found(self, sample_project_id):
        """Test handling when no applications are profiled"""
        agent = ApplicationProfilerAgent()
        
        profile_data = {
            "applications": [],
            "total_applications": 0,
            "message": "No running applications detected on target servers"
        }
        
        mock_bedrock_client.set_mock_response(
            "profiling",
            json.dumps(profile_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_servers': ['empty-server']
        })
        
        assert result['status'] == 'completed'
        assert result['total_applications'] == 0
        assert len(result['applications']) == 0
        assert 'message' in result
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    async def test_state_persistence(self, sample_project_id):
        """Test that profiling results are persisted to state"""
        agent = ApplicationProfilerAgent()
        
        profile_data = {
            "applications": [{"name": "app-01"}],
            "total_applications": 1
        }
        
        mock_bedrock_client.set_mock_response("profiling", json.dumps(profile_data))
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_servers': ['server-01']
        })
        
        # Verify state was saved
        state = mock_dynamodb_client.get_state(sample_project_id, agent.agent_id)
        assert state is not None
        assert 'last_profile' in state
        assert state['last_profile'] == result['s3_uri']
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_cloud_readiness_assessment(self, sample_project_id):
        """Test cloud readiness scoring"""
        agent = ApplicationProfilerAgent()
        
        profile_data = {
            "applications": [
                {
                    "name": "legacy-app",
                    "cloud_readiness": {
                        "score": 65,
                        "rating": "moderate",
                        "factors": {
                            "stateless": True,
                            "containerizable": True,
                            "horizontally_scalable": False,
                            "uses_local_storage": True,
                            "hardcoded_ips": True
                        },
                        "migration_complexity": "medium",
                        "recommended_strategy": "replatform"
                    }
                }
            ],
            "total_applications": 1
        }
        
        mock_bedrock_client.set_mock_response(
            "cloud readiness",
            json.dumps(profile_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_servers': ['legacy-01'],
            'assess_cloud_readiness': True
        })
        
        assert result['status'] == 'completed'
        assert 'cloud_readiness' in result['applications'][0]
        assert result['applications'][0]['cloud_readiness']['score'] == 65
    
    async def test_agent_type(self):
        """Test that agent reports correct type"""
        agent = ApplicationProfilerAgent()
        assert agent.agent_type == "application_profiler"
    
    async def test_custom_agent_id(self):
        """Test initialization with custom agent ID"""
        custom_id = "custom-profiler-456"
        agent = ApplicationProfilerAgent(agent_id=custom_id)
        assert agent.agent_id == custom_id
