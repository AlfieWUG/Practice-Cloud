"""
MonitoringSetupAgent - Optimizes application and infrastructure monitoring
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseAgent, bedrock_client, s3_client, dynamodb_client, eventbridge_client


class MonitoringSetupAgent(BaseAgent):
    """
    Agent responsible for monitoring optimization post-migration.
    
    Capabilities:
    - Monitoring bottleneck identification
    - Resource right-sizing recommendations
    - Caching strategy optimization
    - Database query optimization
    - CDN and edge optimization
    - Application code optimization suggestions
    - Load balancing optimization
    - Auto-scaling tuning
    """
    
    SYSTEM_PROMPT = """You are a monitoring optimization expert specializing in cloud infrastructure and applications.

Your responsibilities:
1. Identify monitoring bottlenecks
2. Recommend resource right-sizing
3. Optimize caching strategies
4. Improve database query monitoring
5. Configure CDN and edge caching
6. Suggest application code improvements
7. Optimize load balancing
8. Tune auto-scaling policies

Provide specific, actionable monitoring optimization recommendations with expected impact and implementation effort."""

    def __init__(self, agent_id: Optional[str] = None):
        """Initialize MonitoringSetupAgent"""
        super().__init__(agent_id)
        self.agent_type = "monitoring_setup"
        self.optimization_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring optimization analysis"""
        project_id = task.get('project_id')
        if not project_id:
            raise ValueError("project_id is required")
        
        monitoring_requirements = task.get('monitoring_requirements')
        if not monitoring_requirements:
            raise ValueError("monitoring_requirements is required")
        
        try:
            await self.emit_event(
                event_type='monitoring_setup.started',
                detail={},
                project_id=project_id
            )
            
            optimization_results = await self._analyze_monitoring(project_id, monitoring_requirements, task)
            optimization_results['status'] = 'completed'
            optimization_results['agent_id'] = self.agent_id
            optimization_results['project_id'] = project_id
            optimization_results['timestamp'] = datetime.utcnow().isoformat()
            
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='monitoring_setup',
                data=optimization_results
            )
            
            result = {
                'status': 'completed',
                'agent_id': self.agent_id,
                'project_id': project_id,
                'bottlenecks': optimization_results.get('bottlenecks', []),
                'optimizations': optimization_results.get('optimizations', []),
                'expected_improvements': optimization_results.get('expected_improvements', {}),
                'recommendations': optimization_results.get('recommendations', []),
                's3_uri': s3_uri,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.save_state(
                project_id=project_id,
                state={'last_optimization': result, 'timestamp': datetime.utcnow().isoformat()}
            )
            
            await self.emit_event(
                event_type='monitoring_setup.completed',
                detail={'optimization_count': len(result.get('optimizations', []))},
                project_id=project_id
            )
            
            self.optimization_data = result
            return result
            
        except Exception as e:
            await self.emit_event(
                event_type='monitoring_setup.failed',
                detail={'error': str(e)},
                project_id=project_id
            )
            raise
    
    async def _analyze_monitoring(self, project_id: str, monitoring_requirements: Any, task: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze monitoring and generate optimizations"""
        prompt = f"""Analyze monitoring metrics and provide optimization recommendations:

Monitoring Metrics:
{json.dumps(monitoring_requirements, indent=2)}

Provide optimization plan in JSON format with:
1. bottlenecks: Identified monitoring bottlenecks
2. optimizations: Specific optimization recommendations
3. expected_improvements: Expected monitoring improvements
4. recommendations: Implementation recommendations"""

        response = await self.invoke_ai(prompt=prompt, system_prompt=self.SYSTEM_PROMPT, temperature=0.2)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            else:
                return {'bottlenecks': [], 'optimizations': [], 'expected_improvements': {}, 'recommendations': [], 'raw_analysis': response}
        except json.JSONDecodeError:
            return {'bottlenecks': [], 'optimizations': [], 'expected_improvements': {}, 'recommendations': [], 'raw_analysis': response}
    
    def get_optimization_data(self) -> Optional[Dict[str, Any]]:
        """Get the most recent optimization data"""
        return self.optimization_data
