"""
Discovery Agent for Nagarro Agentic Services Platform
Analyzes project requirements, context, and prepares initial discovery data
"""

import logging
from typing import Dict, Any, Optional, List

from agentic_services.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class DiscoveryAgent(BaseAgent):
    """
    Discovery Agent - First agent in the workflow
    
    Responsibilities:
    - Parse and analyze project requirements
    - Identify project type and technology stack
    - Extract key components and dependencies
    - Prepare structured discovery data for downstream agents
    """
    
    SYSTEM_PROMPT = """You are a Discovery Agent specialized in analyzing software project requirements.

Your tasks:
1. Parse the project description and requirements
2. Identify the project type (web app, API, microservice, mobile app, etc.)
3. Extract the technology stack (languages, frameworks, databases, etc.)
4. Identify key components and modules
5. List dependencies and third-party services
6. Extract functional and non-functional requirements
7. Identify constraints and assumptions

Return structured JSON with:
- project_type: string
- technology_stack: object with languages, frameworks, databases, cloud_services
- components: list of identified modules/components
- requirements: object with functional and non_functional lists
- dependencies: list of external dependencies
- constraints: list of constraints
- assumptions: list of assumptions made

Be thorough but concise. Focus on actionable insights."""

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.discovery_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute discovery analysis
        
        Args:
            task: Must contain:
                - project_id: Unique project identifier
                - requirements: Project requirements text
                - context: Optional additional context
        
        Returns:
            Discovery results with structured project analysis
        """
        try:
            # Validate inputs
            self.validate_task(task, ['project_id', 'requirements'])
            
            project_id = task['project_id']
            requirements = task['requirements']
            context = task.get('context', '')
            
            logger.info(f"Starting discovery for project: {project_id}")
            
            # Emit start event
            await self.emit_event(
                event_type='discovery.started',
                detail={'project_id': project_id},
                project_id=project_id
            )
            
            # Perform discovery analysis
            discovery_results = await self._analyze_requirements(
                requirements=requirements,
                context=context
            )
            
            # Enrich with metadata
            discovery_results['project_id'] = project_id
            discovery_results['agent_id'] = self.agent_id
            discovery_results['status'] = 'completed'
            
            # Store discovery data in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='discovery',
                data=discovery_results
            )
            
            discovery_results['s3_uri'] = s3_uri
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={'last_discovery': s3_uri}
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='discovery.completed',
                detail={
                    'project_id': project_id,
                    's3_uri': s3_uri,
                    'project_type': discovery_results.get('project_type')
                },
                project_id=project_id
            )
            
            logger.info(f"Discovery completed for project: {project_id}")
            self.discovery_data = discovery_results
            
            return discovery_results
            
        except Exception as e:
            logger.error(f"Discovery failed: {e}", exc_info=True)
            
            # Emit failure event
            await self.emit_event(
                event_type='discovery.failed',
                detail={
                    'project_id': task.get('project_id'),
                    'error': str(e)
                },
                project_id=task.get('project_id')
            )
            
            raise
    
    async def _analyze_requirements(
        self,
        requirements: str,
        context: str = ''
    ) -> Dict[str, Any]:
        """
        Analyze project requirements using AI
        
        Args:
            requirements: Project requirements text
            context: Additional context
            
        Returns:
            Structured discovery data
        """
        # Build comprehensive prompt
        context_section = f'ADDITIONAL CONTEXT:\n{context}' if context else ''
        prompt = f"""Analyze the following project requirements:

PROJECT REQUIREMENTS:
{requirements}

{context_section}

Provide a comprehensive discovery analysis in JSON format as specified."""
        
        # Invoke AI for analysis
        ai_response = await self.invoke_ai(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3  # Lower temperature for more deterministic analysis
        )
        
        # Parse AI response (assume JSON format)
        import json
        try:
            discovery_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback: extract JSON from markdown code blocks if present
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                discovery_data = json.loads(json_match.group(1))
            else:
                # Last resort: treat as text and structure manually
                discovery_data = {
                    'raw_analysis': ai_response,
                    'project_type': 'unknown',
                    'technology_stack': {},
                    'components': [],
                    'requirements': {'functional': [], 'non_functional': []},
                    'dependencies': [],
                    'constraints': [],
                    'assumptions': []
                }
        
        return discovery_data
    
    async def get_project_summary(self, project_id: str) -> Optional[str]:
        """
        Get a text summary of the discovery results
        
        Args:
            project_id: Project identifier
            
        Returns:
            Human-readable summary
        """
        # Load state
        state = await self.load_state(project_id)
        if not state or 'last_discovery' not in state:
            return None
        
        # Load discovery data
        discovery_data = await self.load_data(state['last_discovery'])
        
        # Generate summary
        summary_parts = [
            f"Project Type: {discovery_data.get('project_type', 'Unknown')}",
            f"\nTechnology Stack:",
        ]
        
        tech_stack = discovery_data.get('technology_stack', {})
        for key, value in tech_stack.items():
            if isinstance(value, list):
                summary_parts.append(f"  - {key.title()}: {', '.join(value)}")
            else:
                summary_parts.append(f"  - {key.title()}: {value}")
        
        components = discovery_data.get('components', [])
        if components:
            summary_parts.append(f"\nKey Components ({len(components)}):")
            for comp in components[:5]:  # Top 5
                summary_parts.append(f"  - {comp}")
        
        return '\n'.join(summary_parts)
