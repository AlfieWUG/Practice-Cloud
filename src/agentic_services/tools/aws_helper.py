"""
AWS service helper utilities for Nagarro Agentic Services Platform
Provides wrappers for Bedrock, S3, DynamoDB, and EventBridge
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

from agentic_services.config.settings import settings

logger = logging.getLogger(__name__)


class BedrockClient:
    """AWS Bedrock client for Claude AI interactions"""
    
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=settings.AWS_REGION
        )
        self.model_id = settings.BEDROCK_MODEL_ID
        self.max_tokens = settings.BEDROCK_MAX_TOKENS
    
    async def invoke_claude(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke Claude model via Bedrock
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response from Claude including text and metadata
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens or self.max_tokens,
                "messages": messages,
                "temperature": temperature,
            }
            
            if system_prompt:
                body["system"] = system_prompt
            
            response = self.client.invoke_model(
                modelId=model_id or self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            
            return {
                "text": response_body["content"][0]["text"],
                "stop_reason": response_body.get("stop_reason"),
                "usage": response_body.get("usage", {}),
                "model": model_id or self.model_id
            }
            
        except ClientError as e:
            logger.error(f"Bedrock invocation failed: {e}")
            raise


class S3Client:
    """AWS S3 client for data storage"""
    
    def __init__(self):
        self.client = boto3.client('s3', region_name=settings.AWS_REGION)
        self.discovery_bucket = settings.S3_DISCOVERY_BUCKET
        self.artifacts_bucket = settings.S3_ARTIFACTS_BUCKET
        self.logs_bucket = settings.S3_LOGS_BUCKET
        self.quick_assess_bucket = settings.S3_QUICK_ASSESS_BUCKET
    
    async def upload_json(
        self,
        bucket: str,
        key: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Upload JSON data to S3"""
        try:
            self.client.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(data, indent=2),
                ContentType='application/json',
                Metadata=metadata or {}
            )
            return f"s3://{bucket}/{key}"
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise

    async def upload_bytes(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str = 'application/octet-stream',
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Upload arbitrary bytes to S3."""
        try:
            self.client.put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
                Metadata=metadata or {}
            )
            return f"s3://{bucket}/{key}"
        except ClientError as e:
            logger.error(f"S3 binary upload failed: {e}")
            raise
    
    async def download_json(self, bucket: str, key: str) -> Dict[str, Any]:
        """Download JSON data from S3"""
        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            data = json.loads(response['Body'].read())
            return data
        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            raise
    
    async def list_objects(
        self,
        bucket: str,
        prefix: str = ""
    ) -> List[Dict[str, Any]]:
        """List objects in S3 bucket"""
        try:
            response = self.client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix
            )
            return response.get('Contents', [])
        except ClientError as e:
            logger.error(f"S3 list failed: {e}")
            raise


class DynamoDBClient:
    """AWS DynamoDB client for metadata storage"""
    
    def __init__(self):
        config = {'region_name': settings.AWS_REGION}
        if settings.DYNAMODB_ENDPOINT:
            config['endpoint_url'] = settings.DYNAMODB_ENDPOINT
        
        self.resource = boto3.resource('dynamodb', **config)
        self.client = boto3.client('dynamodb', **config)
    
    def get_table(self, table_name: str):
        """Get DynamoDB table reference"""
        prefix = f"{settings.DYNAMODB_TABLE_PREFIX}-"
        full_name = table_name if table_name.startswith(prefix) else settings.get_dynamodb_table_name(table_name)
        return self.resource.Table(full_name)
    
    async def put_item(
        self,
        table_name: str,
        item: Dict[str, Any]
    ) -> bool:
        """Insert item into DynamoDB"""
        try:
            table = self.get_table(table_name)
            table.put_item(Item=item)
            return True
        except ClientError as e:
            logger.error(f"DynamoDB put_item failed: {e}")
            raise
    
    async def get_item(
        self,
        table_name: str,
        key: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get item from DynamoDB"""
        try:
            table = self.get_table(table_name)
            response = table.get_item(Key=key)
            return response.get('Item')
        except ClientError as e:
            logger.error(f"DynamoDB get_item failed: {e}")
            raise
    
    async def query_items(
        self,
        table_name: str,
        key_condition: str,
        expression_values: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Query items from DynamoDB"""
        try:
            table = self.get_table(table_name)
            response = table.query(
                KeyConditionExpression=key_condition,
                ExpressionAttributeValues=expression_values
            )
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"DynamoDB query failed: {e}")
            raise
    
    async def update_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        update_expression: str,
        expression_values: Dict[str, Any],
        expression_names: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Update item in DynamoDB"""
        try:
            table = self.get_table(table_name)
            response = table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ExpressionAttributeNames=expression_names or {},
                ReturnValues='ALL_NEW'
            )
            return response.get('Attributes', {})
        except ClientError as e:
            logger.error(f"DynamoDB update failed: {e}")
            raise


class EventBridgeClient:
    """AWS EventBridge client for event publishing"""
    
    def __init__(self):
        self.client = boto3.client('events', region_name=settings.AWS_REGION)
        self.event_bus_name = settings.EVENT_BUS_NAME
    
    async def publish_event(
        self,
        source: str,
        detail_type: str,
        detail: Dict[str, Any]
    ) -> str:
        """
        Publish event to EventBridge
        
        Args:
            source: Event source (e.g., 'agent.discovery')
            detail_type: Event type (e.g., 'discovery.completed')
            detail: Event payload
            
        Returns:
            Event ID
        """
        try:
            response = self.client.put_events(
                Entries=[{
                    'Source': source,
                    'DetailType': detail_type,
                    'Detail': json.dumps(detail),
                    'EventBusName': self.event_bus_name,
                    'Time': datetime.utcnow()
                }]
            )
            
            if response['FailedEntryCount'] > 0:
                raise Exception(f"Failed to publish event: {response['Entries'][0]}")
            
            return response['Entries'][0]['EventId']
            
        except ClientError as e:
            logger.error(f"EventBridge publish failed: {e}")
            raise


# Singleton instances
bedrock_client = BedrockClient()
s3_client = S3Client()
dynamodb_client = DynamoDBClient()
eventbridge_client = EventBridgeClient()
