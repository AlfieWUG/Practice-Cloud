"""
ConfigurationAgent - Migrates data to cloud
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseAgent, bedrock_client, s3_client, dynamodb_client, eventbridge_client


class ConfigurationAgent(BaseAgent):
    """
    Agent responsible for data migration to cloud.
    
    Capabilities:
    - Database migration (schema + data)
    - File system migration
    - Object storage migration
    - Data validation and integrity checks
    - Incremental migration support
    - Minimal downtime strategies
    - Data transformation during migration
    - Migration progress tracking
    """
    
    SYSTEM_PROMPT = """You are a data migration expert specializing in cloud data migrations.

Your responsibilities:
1. Plan and execute resource configuration
2. Migrate file systems and object storage
3. Ensure data integrity and validation
4. Implement incremental migration strategies
5. Minimize downtime during migration
6. Handle data transformation requirements
7. Track migration progress and status
8. Provide rollback procedures

Generate comprehensive data migration plans with specific steps, validation procedures, and rollback strategies."""

    def __init__(self, agent_id: Optional[str] = None):
        """Initialize ConfigurationAgent"""
        super().__init__(agent_id)
        self.agent_type = "configuration"
        self.migration_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data migration planning"""
        project_id = task.get('project_id')
        if not project_id:
            raise ValueError("project_id is required")
        
        resources = task.get('resources')
        if not resources:
            raise ValueError("resources is required")
        
        try:
            await self.emit_event(
                event_type='configuration.started',
                detail={},
                project_id=project_id
            )
            
            migration_results = await self._plan_configuration(project_id, resources, task)
            migration_results['status'] = 'completed'
            migration_results['agent_id'] = self.agent_id
            migration_results['project_id'] = project_id
            migration_results['timestamp'] = datetime.utcnow().isoformat()
            
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='configuration',
                data=migration_results
            )
            
            result = {
                'status': 'completed',
                'agent_id': self.agent_id,
                'project_id': project_id,
                'migration_plan': migration_results.get('migration_plan', {}),
                'validation_procedures': migration_results.get('validation_procedures', []),
                'estimated_duration': migration_results.get('estimated_duration', ''),
                'recommendations': migration_results.get('recommendations', []),
                's3_uri': s3_uri,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.save_state(
                project_id=project_id,
                state={'last_migration': result, 'timestamp': datetime.utcnow().isoformat()}
            )
            
            await self.emit_event(
                event_type='configuration.completed',
                detail={},
                project_id=project_id
            )
            
            self.migration_data = result
            return result
            
        except Exception as e:
            await self.emit_event(
                event_type='configuration.failed',
                detail={'error': str(e)},
                project_id=project_id
            )
            raise
    
    async def _plan_configuration(self, project_id: str, resources: Any, task: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to plan data migration"""
        prompt = f"""Plan comprehensive data migration:

Data Sources:
{json.dumps(resources, indent=2)}

Provide migration plan in JSON format with:
1. migration_plan: Detailed migration steps
2. validation_procedures: Data validation steps
3. estimated_duration: Time estimate
4. recommendations: Best practices"""

        response = await self.invoke_ai(prompt=prompt, system_prompt=self.SYSTEM_PROMPT, temperature=0.2)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            else:
                return {'migration_plan': {}, 'validation_procedures': [], 'estimated_duration': 'unknown', 'recommendations': [], 'raw_analysis': response}
        except json.JSONDecodeError:
            return {'migration_plan': {}, 'validation_procedures': [], 'estimated_duration': 'unknown', 'recommendations': [], 'raw_analysis': response}
    
    def get_migration_data(self) -> Optional[Dict[str, Any]]:
        """Get the most recent migration plan data"""
        return self.migration_data
