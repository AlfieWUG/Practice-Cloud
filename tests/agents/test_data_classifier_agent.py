"""
Tests for DataClassifierAgent
Tests data classification, PII detection, and compliance mapping
"""

import pytest
import json
from unittest.mock import patch
from agentic_services.agents.data_classifier import DataClassifierAgent
from tests.mocks import mock_bedrock_client, mock_s3_client, mock_dynamodb_client, mock_eventbridge_client


@pytest.mark.asyncio
class TestDataClassifierAgent:
    """Test suite for DataClassifierAgent"""
    
    async def test_initialization(self):
        """Test agent initializes correctly"""
        agent = DataClassifierAgent()
        
        assert agent.agent_id is not None
        assert agent.agent_type == "data_classifier"
        assert agent.classification_data is None
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_success(self, sample_project_id):
        """Test successful data classification"""
        agent = DataClassifierAgent()
        
        classification_data = {
            "data_sources": [
                {
                    "name": "customer_database",
                    "type": "relational_database",
                    "technology": "PostgreSQL",
                    "tables": [
                        {
                            "name": "customers",
                            "classification": "sensitive",
                            "pii_detected": True,
                            "columns": [
                                {"name": "email", "type": "PII", "sensitivity": "high"},
                                {"name": "phone", "type": "PII", "sensitivity": "high"},
                                {"name": "ssn", "type": "PII", "sensitivity": "critical"}
                            ]
                        }
                    ]
                }
            ],
            "pii_summary": {
                "total_pii_fields": 3,
                "critical_pii": 1,
                "high_sensitivity": 2
            },
            "compliance_requirements": {
                "gdpr": True,
                "hipaa": False,
                "pci_dss": False
            },
            "total_data_sources": 1
        }
        
        mock_bedrock_client.set_mock_response(
            "data classification",
            json.dumps(classification_data)
        )
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'data_sources': ['customer_db', 'orders_db']
        })
        
        assert result['status'] == 'completed'
        assert result['project_id'] == sample_project_id
        assert 'data_sources' in result
        assert result['pii_summary']['total_pii_fields'] == 3
        assert result['compliance_requirements']['gdpr'] == True
        
        # Verify S3 storage
        assert 's3_uri' in result
        assert 'data_classification' in result['s3_uri']
        
        # Verify events
        events = mock_eventbridge_client.get_events()
        assert any(e['DetailType'] == 'classification.started' for e in events)
        assert any(e['DetailType'] == 'classification.completed' for e in events)
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_pii_detection(self, sample_project_id):
        """Test PII detection capabilities"""
        agent = DataClassifierAgent()
        
        classification_data = {
            "data_sources": [
                {
                    "name": "user_data",
                    "pii_types_found": [
                        {"type": "email_address", "count": 1500, "sensitivity": "high"},
                        {"type": "phone_number", "count": 1200, "sensitivity": "high"},
                        {"type": "social_security_number", "count": 1500, "sensitivity": "critical"},
                        {"type": "credit_card", "count": 0, "sensitivity": "critical"},
                        {"type": "date_of_birth", "count": 1500, "sensitivity": "medium"}
                    ]
                }
            ],
            "pii_summary": {
                "total_pii_types": 4,
                "total_pii_records": 5700,
                "critical_pii_types": 1
            },
            "total_data_sources": 1
        }
        
        mock_bedrock_client.set_mock_response("pii detection", json.dumps(classification_data))
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'data_sources': ['user_db'],
            'detect_pii': True
        })
        
        assert result['status'] == 'completed'
        assert result['pii_summary']['total_pii_types'] == 4
        assert result['pii_summary']['critical_pii_types'] == 1
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_compliance_mapping(self, sample_project_id):
        """Test compliance requirements mapping"""
        agent = DataClassifierAgent()
        
        classification_data = {
            "data_sources": [{"name": "patient_records"}],
            "compliance_requirements": {
                "gdpr": {
                    "applicable": True,
                    "reason": "EU customer data present",
                    "controls_required": ["data_encryption", "right_to_erasure", "consent_management"]
                },
                "hipaa": {
                    "applicable": True,
                    "reason": "Health information detected",
                    "controls_required": ["access_controls", "audit_logging", "data_encryption"]
                },
                "pci_dss": {
                    "applicable": False
                }
            },
            "data_residency": {
                "eu_data": True,
                "us_data": True,
                "requirements": ["EU data must stay in EU", "Implement data locality controls"]
            },
            "total_data_sources": 1
        }
        
        mock_bedrock_client.set_mock_response("compliance", json.dumps(classification_data))
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'data_sources': ['health_db'],
            'map_compliance': True
        })
        
        assert result['status'] == 'completed'
        assert result['compliance_requirements']['gdpr']['applicable'] == True
        assert result['compliance_requirements']['hipaa']['applicable'] == True
        assert len(result['compliance_requirements']['gdpr']['controls_required']) == 3
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_data_sensitivity_scoring(self, sample_project_id):
        """Test data sensitivity scoring"""
        agent = DataClassifierAgent()
        
        classification_data = {
            "data_sources": [
                {
                    "name": "analytics_db",
                    "sensitivity_score": 35,
                    "sensitivity_level": "low",
                    "classification": "public"
                },
                {
                    "name": "customer_db",
                    "sensitivity_score": 92,
                    "sensitivity_level": "critical",
                    "classification": "highly_confidential"
                }
            ],
            "overall_sensitivity": {
                "average_score": 63.5,
                "max_score": 92,
                "risk_level": "high"
            },
            "total_data_sources": 2
        }
        
        mock_bedrock_client.set_mock_response("sensitivity", json.dumps(classification_data))
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'data_sources': ['analytics_db', 'customer_db'],
            'score_sensitivity': True
        })
        
        assert result['status'] == 'completed'
        assert result['overall_sensitivity']['average_score'] == 63.5
        assert result['overall_sensitivity']['risk_level'] == 'high'
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_data_residency_requirements(self, sample_project_id):
        """Test data residency requirement identification"""
        agent = DataClassifierAgent()
        
        classification_data = {
            "data_sources": [{"name": "global_users"}],
            "data_residency": {
                "regions_detected": ["EU", "US", "APAC"],
                "requirements": {
                    "EU": {
                        "regulation": "GDPR",
                        "requirement": "Data must be stored in EU",
                        "current_location": "US",
                        "compliant": False,
                        "action_needed": "Migrate to EU region or implement data localization"
                    },
                    "US": {
                        "regulation": "State privacy laws",
                        "requirement": "Data can be stored in US",
                        "current_location": "US",
                        "compliant": True
                    }
                }
            },
            "total_data_sources": 1
        }
        
        mock_bedrock_client.set_mock_response("residency", json.dumps(classification_data))
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'data_sources': ['user_db'],
            'identify_residency_requirements': True
        })
        
        assert result['status'] == 'completed'
        assert 'data_residency' in result
        assert result['data_residency']['requirements']['EU']['compliant'] == False
    
    async def test_missing_project_id(self):
        """Test error handling when project_id is missing"""
        agent = DataClassifierAgent()
        
        with pytest.raises(ValueError, match="project_id"):
            await agent.execute({'data_sources': ['db1']})
    
    async def test_missing_data_sources(self):
        """Test error handling when data_sources is missing"""
        agent = DataClassifierAgent()
        
        with pytest.raises(ValueError, match="data_sources"):
            await agent.execute({'project_id': 'test-project'})
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_execute_failure(self, sample_project_id):
        """Test failure handling during classification"""
        agent = DataClassifierAgent()
        
        mock_bedrock_client.should_fail = True
        
        with pytest.raises(Exception):
            await agent.execute({
                'project_id': sample_project_id,
                'data_sources': ['db1']
            })
        
        events = mock_eventbridge_client.get_events()
        assert any(e['DetailType'] == 'classification.failed' for e in events)
        
        mock_bedrock_client.should_fail = False
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_json_parsing_fallback(self, sample_project_id):
        """Test JSON parsing fallback"""
        agent = DataClassifierAgent()
        
        classification_data = {
            "data_sources": [{"name": "test_db"}],
            "total_data_sources": 1
        }
        
        markdown_response = f"```json\n{json.dumps(classification_data)}\n```"
        mock_bedrock_client.set_mock_response("classification", markdown_response)
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'data_sources': ['test_db']
        })
        
        assert result['status'] == 'completed'
        assert result['total_data_sources'] == 1
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    async def test_state_persistence(self, sample_project_id):
        """Test that classification results are persisted"""
        agent = DataClassifierAgent()
        
        classification_data = {
            "data_sources": [{"name": "db1"}],
            "total_data_sources": 1
        }
        
        mock_bedrock_client.set_mock_response("classification", json.dumps(classification_data))
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'data_sources': ['db1']
        })
        
        state = mock_dynamodb_client.get_state(sample_project_id, agent.agent_id)
        assert state is not None
        assert 'last_classification' in state
    
    @patch('agentic_services.agents.base.bedrock_client', mock_bedrock_client)
    @patch('agentic_services.agents.base.s3_client', mock_s3_client)
    @patch('agentic_services.agents.base.dynamodb_client', mock_dynamodb_client)
    @patch('agentic_services.agents.base.eventbridge_client', mock_eventbridge_client)
    async def test_encryption_recommendations(self, sample_project_id):
        """Test encryption requirement recommendations"""
        agent = DataClassifierAgent()
        
        classification_data = {
            "data_sources": [
                {
                    "name": "payment_db",
                    "contains_pii": True,
                    "encryption_required": True,
                    "encryption_recommendations": {
                        "at_rest": "AES-256",
                        "in_transit": "TLS 1.3",
                        "key_management": "AWS KMS with automatic rotation"
                    }
                }
            ],
            "total_data_sources": 1
        }
        
        mock_bedrock_client.set_mock_response("encryption", json.dumps(classification_data))
        
        result = await agent.execute({
            'project_id': sample_project_id,
            'data_sources': ['payment_db'],
            'recommend_encryption': True
        })
        
        assert result['status'] == 'completed'
        assert result['data_sources'][0]['encryption_required'] == True
        assert result['data_sources'][0]['encryption_recommendations']['at_rest'] == 'AES-256'
    
    async def test_agent_type(self):
        """Test that agent reports correct type"""
        agent = DataClassifierAgent()
        assert agent.agent_type == "data_classifier"
    
    async def test_custom_agent_id(self):
        """Test initialization with custom agent ID"""
        custom_id = "custom-classifier-999"
        agent = DataClassifierAgent(agent_id=custom_id)
        assert agent.agent_id == custom_id
