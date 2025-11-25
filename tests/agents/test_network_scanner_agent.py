"""
Tests for NetworkScannerAgent
Tests network topology discovery, server identification, and service detection
"""

import pytest
import json
from unittest.mock import patch, AsyncMock
from agentic_services.agents.network_scanner import NetworkScannerAgent
from tests.mocks import mock_bedrock_client, mock_s3_client, mock_dynamodb_client, mock_eventbridge_client


@pytest.mark.asyncio
class TestNetworkScannerAgent:
    """Test suite for NetworkScannerAgent"""
    
    async def test_initialization(self):
        """Test agent initializes correctly"""
        agent = NetworkScannerAgent()
        
        assert agent.agent_id is not None
        assert agent.agent_type == "network_scanner"
        assert agent.scan_results is None
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_success(self, sample_project_id):
        """Test successful network scan execution"""
        agent = NetworkScannerAgent()
        
        # Mock AI response with network scan results
        scan_data = {
            "network_topology": {
                "subnets": ["10.0.1.0/24", "10.0.2.0/24"],
                "gateways": ["10.0.1.1", "10.0.2.1"]
            },
            "discovered_servers": [
                {
                    "hostname": "web-server-01",
                    "ip_address": "10.0.1.10",
                    "os": "Ubuntu 22.04",
                    "open_ports": [22, 80, 443]
                },
                {
                    "hostname": "db-server-01",
                    "ip_address": "10.0.1.20",
                    "os": "CentOS 7",
                    "open_ports": [22, 3306]
                }
            ],
            "services": [
                {
                    "name": "nginx",
                    "port": 80,
                    "server": "web-server-01",
                    "version": "1.18.0"
                },
                {
                    "name": "mysql",
                    "port": 3306,
                    "server": "db-server-01",
                    "version": "8.0.32"
                }
            ],
            "total_servers": 2,
            "total_services": 2
        }
        
        mock_bedrock_client.set_mock_response(
            "network scan",
            json.dumps(scan_data)
        )
        
        # Execute network scan
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_network': '10.0.0.0/16',
            'scan_type': 'comprehensive'
        })
        
        # Verify results
        assert result['status'] == 'completed'
        assert result['project_id'] == sample_project_id
        assert 'network_topology' in result
        assert 'discovered_servers' in result
        assert 'services' in result
        assert result['total_servers'] == 2
        assert len(result['discovered_servers']) == 2
        
        # Verify S3 storage
        assert 's3_uri' in result
        assert 'network_scan' in result['s3_uri']
        
        # Verify events emitted
        events = mock_eventbridge_client.get_events()
        assert len(events) >= 2
        assert any(e['DetailType'] == 'network_scan.started' for e in events)
        assert any(e['DetailType'] == 'network_scan.completed' for e in events)
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_with_port_scanning(self, sample_project_id):
        """Test network scan with detailed port scanning"""
        agent = NetworkScannerAgent()
        
        scan_data = {
            "network_topology": {
                "subnets": ["192.168.1.0/24"]
            },
            "discovered_servers": [
                {
                    "hostname": "app-server",
                    "ip_address": "192.168.1.100",
                    "open_ports": [22, 80, 443, 8080, 9090],
                    "closed_ports": [21, 23, 25],
                    "filtered_ports": [3389]
                }
            ],
            "services": [
                {
                    "name": "ssh",
                    "port": 22,
                    "protocol": "tcp",
                    "banner": "OpenSSH_8.2p1"
                },
                {
                    "name": "http",
                    "port": 8080,
                    "protocol": "tcp",
                    "banner": "Apache Tomcat/9.0"
                }
            ],
            "total_servers": 1,
            "total_open_ports": 5
        }
        
        mock_bedrock_client.set_mock_response(
            "port scan",
            json.dumps(scan_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_network': '192.168.1.0/24',
            'scan_type': 'port_scan',
            'port_range': '1-65535'
        })
        
        assert result['status'] == 'completed'
        assert 'total_open_ports' in result
        assert result['total_open_ports'] == 5
        assert len(result['discovered_servers'][0]['open_ports']) == 5
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_with_service_identification(self, sample_project_id):
        """Test service identification and version detection"""
        agent = NetworkScannerAgent()
        
        scan_data = {
            "discovered_servers": [
                {
                    "hostname": "web-01",
                    "ip_address": "10.10.1.5"
                }
            ],
            "services": [
                {
                    "name": "nginx",
                    "port": 80,
                    "version": "1.20.2",
                    "ssl_enabled": True,
                    "ssl_certificate": {
                        "valid_until": "2025-12-31",
                        "issuer": "Let's Encrypt"
                    }
                },
                {
                    "name": "postgresql",
                    "port": 5432,
                    "version": "14.5",
                    "authentication": "md5"
                }
            ],
            "vulnerabilities": [
                {
                    "service": "nginx",
                    "cve": "CVE-2023-12345",
                    "severity": "medium",
                    "description": "Outdated version"
                }
            ],
            "total_services": 2
        }
        
        mock_bedrock_client.set_mock_response(
            "service identification",
            json.dumps(scan_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_network': '10.10.1.0/24',
            'scan_type': 'service_identification',
            'include_vulnerabilities': True
        })
        
        assert result['status'] == 'completed'
        assert 'services' in result
        assert 'vulnerabilities' in result
        assert len(result['services']) == 2
        assert result['services'][0]['ssl_enabled'] == True
    
    async def test_missing_project_id(self):
        """Test error handling when project_id is missing"""
        agent = NetworkScannerAgent()
        
        with pytest.raises(ValueError, match="project_id"):
            await agent.execute({
                'target_network': '10.0.0.0/16'
            })
    
    async def test_missing_target_network(self):
        """Test error handling when target_network is missing"""
        agent = NetworkScannerAgent()
        
        with pytest.raises(ValueError, match="target_network"):
            await agent.execute({
                'project_id': 'test-project'
            })
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_failure(self, sample_project_id):
        """Test failure handling during network scan"""
        agent = NetworkScannerAgent()
        
        # Mock AI to raise exception
        mock_bedrock_client.should_fail = True
        
        with pytest.raises(Exception):
            await agent.execute({
                'project_id': sample_project_id,
                'target_network': '10.0.0.0/16'
            })
        
        # Verify failure event was emitted
        events = mock_eventbridge_client.get_events()
        assert any(e['DetailType'] == 'network_scan.failed' for e in events)
        
        mock_bedrock_client.should_fail = False
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_json_parsing_fallback(self, sample_project_id):
        """Test JSON parsing fallback when AI returns markdown"""
        agent = NetworkScannerAgent()
        
        scan_data = {
            "discovered_servers": [{"hostname": "test-server", "ip_address": "10.0.0.1"}],
            "total_servers": 1
        }
        
        # Return JSON in markdown code block
        markdown_response = f"```json\n{json.dumps(scan_data)}\n```"
        mock_bedrock_client.set_mock_response("network", markdown_response)
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_network': '10.0.0.0/24'
        })
        
        assert result['status'] == 'completed'
        assert 'discovered_servers' in result
        assert result['total_servers'] == 1
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_empty_network_scan(self, sample_project_id):
        """Test handling of network with no discovered servers"""
        agent = NetworkScannerAgent()
        
        scan_data = {
            "network_topology": {
                "subnets": ["172.16.0.0/24"]
            },
            "discovered_servers": [],
            "services": [],
            "total_servers": 0,
            "scan_status": "completed",
            "message": "No active servers found in target network"
        }
        
        mock_bedrock_client.set_mock_response(
            "network scan",
            json.dumps(scan_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_network': '172.16.0.0/24'
        })
        
        assert result['status'] == 'completed'
        assert result['total_servers'] == 0
        assert len(result['discovered_servers']) == 0
        assert 'message' in result
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_scan_with_credentials(self, sample_project_id):
        """Test network scan with authentication credentials"""
        agent = NetworkScannerAgent()
        
        scan_data = {
            "discovered_servers": [
                {
                    "hostname": "secure-server",
                    "ip_address": "10.0.1.50",
                    "authenticated": True,
                    "os_details": {
                        "name": "Ubuntu Server",
                        "version": "20.04 LTS",
                        "kernel": "5.4.0-150-generic"
                    }
                }
            ],
            "total_servers": 1
        }
        
        mock_bedrock_client.set_mock_response(
            "authenticated scan",
            json.dumps(scan_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_network': '10.0.1.0/24',
            'credentials': {
                'username': 'admin',
                'key_file': 's3://keys/admin.pem'
            }
        })
        
        assert result['status'] == 'completed'
        assert result['discovered_servers'][0]['authenticated'] == True
        assert 'os_details' in result['discovered_servers'][0]
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    async def test_state_persistence(self, sample_project_id):
        """Test that scan results are persisted to state"""
        agent = NetworkScannerAgent()
        
        scan_data = {
            "discovered_servers": [{"hostname": "server-01", "ip_address": "10.0.0.5"}],
            "total_servers": 1
        }
        
        mock_bedrock_client.set_mock_response("network", json.dumps(scan_data))
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'target_network': '10.0.0.0/24'
        })
        
        # Verify state was saved
        state = mock_dynamodb_client.get_state(sample_project_id, agent.agent_id)
        assert state is not None
        assert 'last_scan' in state
        assert state['last_scan'] == result['s3_uri']
    
    async def test_agent_type(self):
        """Test that agent reports correct type"""
        agent = NetworkScannerAgent()
        assert agent.agent_type == "network_scanner"
    
    async def test_custom_agent_id(self):
        """Test initialization with custom agent ID"""
        custom_id = "custom-scanner-123"
        agent = NetworkScannerAgent(agent_id=custom_id)
        assert agent.agent_id == custom_id
