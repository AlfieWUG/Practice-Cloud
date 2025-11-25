"""
Base Agent class for Nagarro Agentic Services Platform
All specialized agents inherit from this base class
"""

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from agentic_services.tools.aws_helper import (
    bedrock_client,
    s3_client,
    dynamodb_client,
    eventbridge_client
)
from agentic_services.config.settings import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all AI agents
    
    Provides common functionality:
    - AWS service clients (Bedrock, S3, DynamoDB, EventBridge)
    - State management
    - Event publishing
    - Logging
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        """
        Initialize base agent
        
        Args:
            agent_id: Unique agent identifier (generated if not provided)
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.agent_type = self.__class__.__name__
        
        # AWS clients
        self.bedrock = bedrock_client
        self.s3 = s3_client
        self.dynamodb = dynamodb_client
        self.eventbridge = eventbridge_client
        
        logger.info(f"Initialized {self.agent_type} with ID: {self.agent_id}")
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main task
        
        Args:
            task: Task configuration and input data
            
        Returns:
            Task execution results
        """
        pass
    
    async def save_state(
        self,
        project_id: str,
        state: Dict[str, Any]
    ) -> bool:
        """
        Persist agent state to DynamoDB
        
        Args:
            project_id: Project identifier
            state: State data to save
            
        Returns:
            Success status
        """
        try:
            item = {
                'project_id': project_id,
                'agent_id': self.agent_id,
                'agent_type': self.agent_type,
                'state': state,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            await self.dynamodb.put_item('AgentStates', item)
            logger.info(f"Saved state for {self.agent_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            return False
    
    async def load_state(
        self,
        project_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load agent state from DynamoDB
        
        Args:
            project_id: Project identifier
            
        Returns:
            Saved state or None if not found
        """
        try:
            item = await self.dynamodb.get_item(
                'AgentStates',
                {'project_id': project_id, 'agent_id': self.agent_id}
            )
            
            if item:
                return item.get('state')
            return None
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None
    
    async def emit_event(
        self,
        event_type: str,
        detail: Dict[str, Any],
        project_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Emit event to EventBridge
        
        Args:
            event_type: Event type (e.g., 'discovery.completed')
            detail: Event payload
            project_id: Optional project identifier
            
        Returns:
            Event ID if successful
        """
        try:
            source = f"agent.{self.agent_type.lower()}"
            
            event_detail = {
                'agent_id': self.agent_id,
                'agent_type': self.agent_type,
                'timestamp': datetime.utcnow().isoformat(),
                **detail
            }
            
            if project_id:
                event_detail['project_id'] = project_id
            
            event_id = await self.eventbridge.publish_event(
                source=source,
                detail_type=event_type,
                detail=event_detail
            )
            
            logger.info(f"Published event: {event_type} (ID: {event_id})")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to emit event: {e}")
            return None
    
    async def invoke_ai(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Invoke Claude AI via Bedrock
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            temperature: Sampling temperature
            
        Returns:
            AI response text
        """
        try:
            response = await self.bedrock.invoke_claude(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature
            )
            
            logger.debug(f"AI invocation completed. Tokens: {response['usage']}")
            return response['text']
            
        except Exception as e:
            logger.error(f"AI invocation failed: {e}")
            raise
    
    async def store_data(
        self,
        project_id: str,
        data_type: str,
        data: Dict[str, Any],
        bucket: Optional[str] = None
    ) -> str:
        """
        Store data in S3
        
        Args:
            project_id: Project identifier
            data_type: Type of data (e.g., 'discovery', 'analysis')
            data: Data to store
            bucket: Optional bucket override
            
        Returns:
            S3 URI of stored data
        """
        try:
            bucket = bucket or self.s3.discovery_bucket
            timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
            key = f"{project_id}/{data_type}/{self.agent_type}_{timestamp}.json"
            
            s3_uri = await self.s3.upload_json(
                bucket=bucket,
                key=key,
                data=data,
                metadata={
                    'agent_type': self.agent_type,
                    'agent_id': self.agent_id,
                    'project_id': project_id
                }
            )
            
            logger.info(f"Stored data: {s3_uri}")
            return s3_uri
            
        except Exception as e:
            logger.error(f"Failed to store data: {e}")
            raise
    
    async def load_data(
        self,
        s3_uri: str
    ) -> Dict[str, Any]:
        """
        Load data from S3
        
        Args:
            s3_uri: S3 URI (s3://bucket/key)
            
        Returns:
            Loaded data
        """
        try:
            # Parse S3 URI
            parts = s3_uri.replace('s3://', '').split('/', 1)
            bucket, key = parts[0], parts[1]
            
            data = await self.s3.download_json(bucket=bucket, key=key)
            logger.info(f"Loaded data from: {s3_uri}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise
    
    def validate_task(self, task: Dict[str, Any], required_fields: list) -> bool:
        """
        Validate task configuration
        
        Args:
            task: Task configuration
            required_fields: List of required field names
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        missing = [field for field in required_fields if field not in task]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        return True
    
    def __repr__(self) -> str:
        return f"<{self.agent_type} id={self.agent_id}>"
