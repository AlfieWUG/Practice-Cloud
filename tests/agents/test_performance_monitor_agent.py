"""
Tests for PerformanceMonitorAgent
Tests performance monitoring, baseline establishment, and anomaly detection
"""

import pytest
import json
from unittest.mock import patch
from agentic_services.agents.performance_monitor import PerformanceMonitorAgent
from tests.mocks import mock_bedrock_client, mock_s3_client, mock_dynamodb_client, mock_eventbridge_client


@pytest.mark.asyncio
class TestPerformanceMonitorAgent:
    """Test suite for PerformanceMonitorAgent"""
    
    async def test_initialization(self):
        """Test agent initializes correctly"""
        agent = PerformanceMonitorAgent()
        
        assert agent.agent_id is not None
        assert agent.agent_type == "performance_monitor"
        assert agent.monitoring_data is None
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_success(self, sample_project_id):
        """Test successful performance monitoring"""
        agent = PerformanceMonitorAgent()
        
        # Mock AI response with monitoring data
        monitoring_data = {
            "metrics": {
                "response_time": {
                    "current_avg_ms": 145,
                    "baseline_avg_ms": 120,
                    "p50_ms": 95,
                    "p95_ms": 380,
                    "p99_ms": 725,
                    "trend": "increasing"
                },
                "throughput": {
                    "current_rps": 1150,
                    "baseline_rps": 1200,
                    "peak_rps": 2800,
                    "trend": "stable"
                },
                "error_rate": {
                    "current_percent": 0.8,
                    "baseline_percent": 0.5,
                    "trend": "increasing"
                },
                "cpu_usage": {
                    "current_percent": 62,
                    "baseline_percent": 55,
                    "peak_percent": 89
                },
                "memory_usage": {
                    "current_mb": 3200,
                    "baseline_mb": 2800,
                    "peak_mb": 4100
                }
            },
            "monitoring_duration_hours": 24,
            "data_points_collected": 1440,
            "baseline_established": True
        }
        
        mock_bedrock_client.set_mock_response(
            "performance monitoring",
            json.dumps(monitoring_data)
        )
        
        # Execute monitoring
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_systems': ['web-app', 'api-service'],
            'monitoring_duration_hours': 24
        })
        
        # Verify results
        assert result['status'] == 'completed'
        assert result['project_id'] == sample_project_id
        assert 'metrics' in result
        assert result['baseline_established'] == True
        assert result['data_points_collected'] == 1440
        
        # Verify S3 storage
        assert 's3_uri' in result
        assert 'performance_metrics' in result['s3_uri']
        
        # Verify events emitted
        events = mock_eventbridge_client.get_events()
        assert len(events) >= 2
        assert any(e['DetailType'] == 'monitoring.started' for e in events)
        assert any(e['DetailType'] == 'monitoring.completed' for e in events)
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_with_anomaly_detection(self, sample_project_id):
        """Test monitoring with anomaly detection"""
        agent = PerformanceMonitorAgent()
        
        monitoring_data = {
            "metrics": {
                "response_time": {
                    "current_avg_ms": 850,
                    "baseline_avg_ms": 120
                }
            },
            "anomalies": [
                {
                    "type": "response_time_spike",
                    "severity": "high",
                    "description": "Response time 7x above baseline",
                    "detected_at": "2025-01-15 14:23:00 UTC",
                    "duration_minutes": 45,
                    "impact": "User experience degraded",
                    "possible_causes": ["Database connection pool exhaustion", "Memory leak"]
                },
                {
                    "type": "error_rate_spike",
                    "severity": "critical",
                    "description": "Error rate jumped from 0.5% to 12%",
                    "detected_at": "2025-01-15 15:10:00 UTC",
                    "duration_minutes": 20,
                    "impact": "Multiple transaction failures"
                }
            ],
            "baseline_established": True,
            "total_anomalies": 2
        }
        
        mock_bedrock_client.set_mock_response(
            "anomaly detection",
            json.dumps(monitoring_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_systems': ['app-01'],
            'detect_anomalies': True
        })
        
        assert result['status'] == 'completed'
        assert 'anomalies' in result
        assert result['total_anomalies'] == 2
        assert result['anomalies'][0]['severity'] == 'high'
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_baseline_establishment(self, sample_project_id):
        """Test establishing performance baseline"""
        agent = PerformanceMonitorAgent()
        
        monitoring_data = {
            "metrics": {
                "response_time": {
                    "avg_ms": 125,
                    "p50_ms": 95,
                    "p95_ms": 320,
                    "p99_ms": 650,
                    "min_ms": 15,
                    "max_ms": 1200
                },
                "throughput": {
                    "avg_rps": 1180,
                    "min_rps": 450,
                    "max_rps": 2950
                },
                "availability": {
                    "uptime_percent": 99.92,
                    "downtime_minutes": 12
                }
            },
            "baseline_established": True,
            "baseline_confidence": "high",
            "monitoring_duration_hours": 72,
            "recommendation": "Baseline established with high confidence. Ready for migration."
        }
        
        mock_bedrock_client.set_mock_response(
            "baseline",
            json.dumps(monitoring_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_systems': ['prod-app'],
            'establish_baseline': True,
            'monitoring_duration_hours': 72
        })
        
        assert result['status'] == 'completed'
        assert result['baseline_established'] == True
        assert result['baseline_confidence'] == 'high'
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_post_migration_validation(self, sample_project_id):
        """Test post-migration performance validation"""
        agent = PerformanceMonitorAgent()
        
        monitoring_data = {
            "pre_migration_metrics": {
                "response_time_ms": 120,
                "throughput_rps": 1200,
                "error_rate_percent": 0.5
            },
            "post_migration_metrics": {
                "response_time_ms": 95,
                "throughput_rps": 1450,
                "error_rate_percent": 0.3
            },
            "comparison": {
                "response_time_improvement_percent": 20.8,
                "throughput_improvement_percent": 20.8,
                "error_rate_improvement_percent": 40.0,
                "overall_verdict": "performance_improved"
            },
            "validation_passed": True,
            "sla_compliance": {
                "response_time_sla": "passed",
                "availability_sla": "passed",
                "error_rate_sla": "passed"
            }
        }
        
        mock_bedrock_client.set_mock_response(
            "validation",
            json.dumps(monitoring_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_systems': ['migrated-app'],
            'validate_post_migration': True,
            'baseline_s3_uri': 's3://bucket/baseline.json'
        })
        
        assert result['status'] == 'completed'
        assert result['validation_passed'] == True
        assert result['comparison']['overall_verdict'] == 'performance_improved'
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_with_sla_monitoring(self, sample_project_id):
        """Test SLA compliance monitoring"""
        agent = PerformanceMonitorAgent()
        
        monitoring_data = {
            "metrics": {
                "response_time": {"current_avg_ms": 145},
                "availability": {"uptime_percent": 99.95}
            },
            "sla_compliance": {
                "response_time": {
                    "sla_threshold_ms": 200,
                    "current_ms": 145,
                    "status": "compliant",
                    "margin_percent": 27.5
                },
                "availability": {
                    "sla_threshold_percent": 99.9,
                    "current_percent": 99.95,
                    "status": "compliant",
                    "margin_percent": 0.05
                },
                "overall_compliance": "compliant"
            },
            "baseline_established": True
        }
        
        mock_bedrock_client.set_mock_response(
            "sla monitoring",
            json.dumps(monitoring_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_systems': ['production'],
            'monitor_sla_compliance': True,
            'sla_thresholds': {
                'response_time_ms': 200,
                'availability_percent': 99.9
            }
        })
        
        assert result['status'] == 'completed'
        assert 'sla_compliance' in result
        assert result['sla_compliance']['overall_compliance'] == 'compliant'
    
    async def test_missing_project_id(self):
        """Test error handling when project_id is missing"""
        agent = PerformanceMonitorAgent()
        
        with pytest.raises(ValueError, match="project_id"):
            await agent.execute({
                'target_systems': ['system-01']
            })
    
    async def test_missing_target_systems(self):
        """Test error handling when target_systems is missing"""
        agent = PerformanceMonitorAgent()
        
        with pytest.raises(ValueError, match="target_systems"):
            await agent.execute({
                'project_id': 'test-project'
            })
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_failure(self, sample_project_id):
        """Test failure handling during monitoring"""
        agent = PerformanceMonitorAgent()
        
        # Mock AI to raise exception
        mock_bedrock_client.should_fail = True
        
        with pytest.raises(Exception):
            await agent.execute({
                'project_id': sample_project_id,
                'target_systems': ['system-01']
            })
        
        # Verify failure event was emitted
        events = mock_eventbridge_client.get_events()
        assert any(e['DetailType'] == 'monitoring.failed' for e in events)
        
        mock_bedrock_client.should_fail = False
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_json_parsing_fallback(self, sample_project_id):
        """Test JSON parsing fallback when AI returns markdown"""
        agent = PerformanceMonitorAgent()
        
        monitoring_data = {
            "metrics": {"response_time": {"current_avg_ms": 120}},
            "baseline_established": True
        }
        
        # Return JSON in markdown code block
        markdown_response = f"```json\n{json.dumps(monitoring_data)}\n```"
        mock_bedrock_client.set_mock_response("monitoring", markdown_response)
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_systems': ['system-01']
        })
        
        assert result['status'] == 'completed'
        assert 'metrics' in result
        assert result['baseline_established'] == True
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    async def test_state_persistence(self, sample_project_id):
        """Test that monitoring results are persisted to state"""
        agent = PerformanceMonitorAgent()
        
        monitoring_data = {
            "metrics": {"response_time": {"current_avg_ms": 100}},
            "baseline_established": True
        }
        
        mock_bedrock_client.set_mock_response("monitoring", json.dumps(monitoring_data))
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_systems': ['system-01']
        })
        
        # Verify state was saved
        state = mock_dynamodb_client.get_state(sample_project_id, agent.agent_id)
        assert state is not None
        assert 'last_monitoring' in state
        assert state['last_monitoring'] == result['s3_uri']
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_trend_analysis(self, sample_project_id):
        """Test performance trend analysis"""
        agent = PerformanceMonitorAgent()
        
        monitoring_data = {
            "metrics": {
                "response_time": {
                    "current_avg_ms": 145,
                    "trend": "increasing",
                    "trend_rate_percent": 8.5
                },
                "memory_usage": {
                    "current_mb": 3500,
                    "trend": "increasing",
                    "trend_rate_percent": 12.3,
                    "projection_30days_mb": 4200
                }
            },
            "trends": {
                "overall_health": "degrading",
                "concerning_metrics": ["response_time", "memory_usage"],
                "recommendations": [
                    "Investigate memory leak - 12% growth rate",
                    "Optimize slow queries causing response time increase"
                ]
            },
            "baseline_established": True
        }
        
        mock_bedrock_client.set_mock_response(
            "trend analysis",
            json.dumps(monitoring_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_systems': ['app-01'],
            'analyze_trends': True
        })
        
        assert result['status'] == 'completed'
        assert 'trends' in result
        assert result['trends']['overall_health'] == 'degrading'
        assert len(result['trends']['concerning_metrics']) == 2
    
    async def test_agent_type(self):
        """Test that agent reports correct type"""
        agent = PerformanceMonitorAgent()
        assert agent.agent_type == "performance_monitor"
    
    async def test_custom_agent_id(self):
        """Test initialization with custom agent ID"""
        custom_id = "custom-monitor-789"
        agent = PerformanceMonitorAgent(agent_id=custom_id)
        assert agent.agent_id == custom_id
