"""
Mock AWS services for testing without actual AWS costs
Provides in-memory implementations of Bedrock, S3, DynamoDB, EventBridge
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from unittest.mock import AsyncMock


class MockBedrockClient:
    """Mock AWS Bedrock client for testing"""
    
    def __init__(self):
        self.invocation_count = 0
        self.last_prompt = None
        self.mock_responses = {}
        self.last_response = None  # Track most recent response set
        self.should_fail = False
    
    def set_mock_response(self, prompt_pattern: str, response: str):
        """Set a mock response for a specific prompt pattern"""
        self.mock_responses[prompt_pattern] = response
        self.last_response = response  # Track for fallback
    
    async def invoke_claude(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 10000
    ) -> Dict[str, Any]:
        """Mock Claude invocation"""
        if self.should_fail:
            raise Exception("Simulated AI failure")
        
        self.invocation_count += 1
        self.last_prompt = prompt
        
        # Find matching mock response with flexible matching
        response_text = None
        prompt_lower = prompt.lower()
        
        # Try exact pattern match first
        for pattern, response in self.mock_responses.items():
            if pattern.lower() in prompt_lower:
                response_text = response
                break
        
        # Fallback: try word-by-word matching
        if not response_text:
            best_match = None
            best_count = 0
            
            for pattern, response in self.mock_responses.items():
                pattern_words = set(pattern.lower().split())
                prompt_words = set(prompt_lower.split())
                match_count = len(pattern_words & prompt_words)
                
                if match_count > best_count:
                    best_count = match_count
                    best_match = response
            
            if best_count >= 2:  # At least 2 words match
                response_text = best_match
        
        # Last fallback: use the most recently set response
        if not response_text and self.last_response:
            response_text = self.last_response
        
        # Default response
        if not response_text:
            response_text = json.dumps({
                "project_type": "web_application",
                "technology_stack": {
                    "languages": ["Python"],
                    "frameworks": ["FastAPI"],
                    "databases": ["PostgreSQL"]
                },
                "components": ["API", "Database", "Frontend"],
                "requirements": {
                    "functional": ["REST API", "User Authentication"],
                    "non_functional": ["Scalability", "Security"]
                },
                "dependencies": ["AWS", "Docker"],
                "constraints": ["Budget", "Timeline"],
                "assumptions": ["Cloud deployment"]
            })
        
        return {
            "text": response_text,
            "usage": {
                "input_tokens": len(prompt.split()),
                "output_tokens": len(response_text.split()),
                "total_tokens": len(prompt.split()) + len(response_text.split())
            },
            "stop_reason": "end_turn"
        }


class MockS3Client:
    """Mock AWS S3 client for testing"""
    
    def __init__(self):
        self.storage: Dict[str, Dict[str, Any]] = {}
        self.discovery_bucket = "test-discovery-bucket"
        self.artifacts_bucket = "test-artifacts-bucket"
        self.upload_count = 0
        self.download_count = 0
    
    async def upload_json(
        self,
        bucket: str,
        key: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Mock S3 upload"""
        self.upload_count += 1
        s3_uri = f"s3://{bucket}/{key}"
        
        self.storage[s3_uri] = {
            "data": data,
            "metadata": metadata or {},
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        return s3_uri
    
    async def download_json(
        self,
        bucket: str,
        key: str
    ) -> Dict[str, Any]:
        """Mock S3 download"""
        self.download_count += 1
        s3_uri = f"s3://{bucket}/{key}"
        
        if s3_uri not in self.storage:
            raise FileNotFoundError(f"Object not found: {s3_uri}")
        
        return self.storage[s3_uri]["data"]
    
    def clear(self):
        """Clear all stored data"""
        self.storage.clear()
        self.upload_count = 0
        self.download_count = 0


class MockDynamoDBClient:
    """Mock AWS DynamoDB client for testing"""
    
    def __init__(self):
        self.tables: Dict[str, Dict[str, Any]] = {}
        self.put_count = 0
        self.get_count = 0
    
    async def put_item(
        self,
        table_name: str,
        item: Dict[str, Any]
    ) -> bool:
        """Mock DynamoDB put_item"""
        self.put_count += 1
        
        if table_name not in self.tables:
            self.tables[table_name] = {}
        
        # Use project_id + agent_id as composite key
        key = f"{item.get('project_id')}#{item.get('agent_id')}"
        self.tables[table_name][key] = item
        
        return True
    
    async def get_item(
        self,
        table_name: str,
        key: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """Mock DynamoDB get_item"""
        self.get_count += 1
        
        if table_name not in self.tables:
            return None
        
        # Build composite key
        composite_key = f"{key.get('project_id')}#{key.get('agent_id')}"
        return self.tables[table_name].get(composite_key)
    
    def get_state(self, project_id: str, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get state for a specific project/agent combination"""
        table_name = "AgentStates"  # Match actual table name in base.py
        if table_name not in self.tables:
            return None
        
        composite_key = f"{project_id}#{agent_id}"
        item = self.tables[table_name].get(composite_key)
        if item:
            return item.get('state', {})
        return None
    
    def clear(self):
        """Clear all tables"""
        self.tables.clear()
        self.put_count = 0
        self.get_count = 0


class MockEventBridgeClient:
    """Mock AWS EventBridge client for testing"""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.event_count = 0
    
    async def publish_event(
        self,
        source: str,
        detail_type: str,
        detail: Dict[str, Any]
    ) -> str:
        """Mock EventBridge publish"""
        self.event_count += 1
        event_id = f"event-{self.event_count}"
        
        self.events.append({
            "id": event_id,
            "source": source,
            "detail_type": detail_type,
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return event_id
    
    def get_events_by_type(self, detail_type: str) -> List[Dict[str, Any]]:
        """Get all events of a specific type"""
        return [e for e in self.events if e["detail_type"] == detail_type]
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get all events"""
        # Return events with compatible structure for tests
        return [{
            "DetailType": e["detail_type"],
            "Detail": e["detail"],
            "Source": e["source"],
            "EventId": e["id"],
            "Time": e["timestamp"]
        } for e in self.events]
    
    def clear(self):
        """Clear all events"""
        self.events.clear()
        self.event_count = 0


# Singleton instances for testing
mock_bedrock_client = MockBedrockClient()
mock_s3_client = MockS3Client()
mock_dynamodb_client = MockDynamoDBClient()
mock_eventbridge_client = MockEventBridgeClient()


def reset_all_mocks():
    """Reset all mock clients to clean state"""
    mock_s3_client.clear()
    mock_dynamodb_client.clear()
    mock_eventbridge_client.clear()
    mock_bedrock_client.invocation_count = 0
    mock_bedrock_client.last_prompt = None
    mock_bedrock_client.mock_responses.clear()
    mock_bedrock_client.should_fail = False
    # Restore original invoke_claude method
    mock_bedrock_client.invoke_claude = MockBedrockClient.invoke_claude.__get__(mock_bedrock_client, MockBedrockClient)
