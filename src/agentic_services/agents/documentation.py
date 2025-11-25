"""
DocumentationAgent - Optimizes application and infrastructure documentation
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseAgent, bedrock_client, s3_client, dynamodb_client, eventbridge_client


class DocumentationAgent(BaseAgent):
    """
    Agent responsible for documentation optimization post-migration.
    
    Capabilities:
    - Documentation bottleneck identification
    - Resource right-sizing recommendations
    - Caching strategy optimization
    - Database query optimization
    - CDN and edge optimization
    - Application code optimization suggestions
    - Load balancing optimization
    - Auto-scaling tuning
    """
    
    SYSTEM_PROMPT = """You are a documentation optimization expert specializing in cloud infrastructure and applications.

Your responsibilities:
1. Identify documentation bottlenecks
2. Recommend resource right-sizing
3. Optimize caching strategies
4. Improve database query documentation
5. Configure CDN and edge caching
6. Suggest application code improvements
7. Optimize load balancing
8. Tune auto-scaling policies

Provide specific, actionable documentation optimization recommendations with expected impact and implementation effort."""

    def __init__(self, agent_id: Optional[str] = None):
        """Initialize DocumentationAgent"""
        super().__init__(agent_id)
        self.agent_type = "documentation"
        self.optimization_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation optimization analysis"""
        project_id = task.get('project_id')
        if not project_id:
            raise ValueError("project_id is required")
        
        documentation_scope = task.get('documentation_scope')
        if not documentation_scope:
            raise ValueError("documentation_scope is required")
        
        try:
            await self.emit_event(
                event_type='documentation.started',
                detail={},
                project_id=project_id
            )
            
            optimization_results = await self._analyze_documentation(project_id, documentation_scope, task)
            optimization_results['status'] = 'completed'
            optimization_results['agent_id'] = self.agent_id
            optimization_results['project_id'] = project_id
            optimization_results['timestamp'] = datetime.utcnow().isoformat()
            
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='documentation',
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
                event_type='documentation.completed',
                detail={'optimization_count': len(result.get('optimizations', []))},
                project_id=project_id
            )
            
            self.optimization_data = result
            return result
            
        except Exception as e:
            await self.emit_event(
                event_type='documentation.failed',
                detail={'error': str(e)},
                project_id=project_id
            )
            raise
    
    async def _analyze_documentation(self, project_id: str, documentation_scope: Any, task: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze documentation and generate optimizations"""
        prompt = f"""Analyze documentation metrics and provide optimization recommendations:

Documentation Metrics:
{json.dumps(documentation_scope, indent=2)}

Provide optimization plan in JSON format with:
1. bottlenecks: Identified documentation bottlenecks
2. optimizations: Specific optimization recommendations
3. expected_improvements: Expected documentation improvements
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
