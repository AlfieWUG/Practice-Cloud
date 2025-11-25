"""
Analysis Agent for Nagarro Agentic Services Platform
Performs deep technical analysis on discovery data
"""

import logging
from typing import Dict, Any, Optional, List

from agentic_services.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class AnalysisAgent(BaseAgent):
    """
    Analysis Agent - Second agent in the workflow
    
    Responsibilities:
    - Deep dive into technical requirements
    - Identify technical challenges and risks
    - Recommend architecture patterns
    - Analyze scalability and performance needs
    - Security and compliance considerations
    """
    
    SYSTEM_PROMPT = """You are an Analysis Agent specialized in deep technical analysis of software projects.

Your tasks:
1. Analyze the technical complexity and feasibility
2. Identify potential technical challenges and risks
3. Recommend appropriate architecture patterns (monolith, microservices, serverless, etc.)
4. Evaluate scalability and performance requirements
5. Assess security and compliance needs
6. Recommend best practices and design patterns
7. Identify integration points and APIs needed

Return structured JSON with:
- complexity_assessment: object with level (low/medium/high) and reasoning
- technical_challenges: list of identified challenges with severity
- recommended_architecture: object with pattern, reasoning, and alternatives
- scalability_analysis: object with expected_load, scaling_strategy, bottlenecks
- security_considerations: list of security requirements and recommendations
- performance_requirements: object with targets and optimization strategies
- integration_points: list of external systems and APIs
- best_practices: list of recommended practices specific to this project
- risk_assessment: list of technical risks with mitigation strategies

Be thorough, practical, and prioritize real-world considerations."""

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.analysis_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute technical analysis
        
        Args:
            task: Must contain:
                - project_id: Unique project identifier
                - discovery_data: Discovery results (or s3_uri to load)
        
        Returns:
            Analysis results with technical recommendations
        """
        try:
            # Validate inputs
            self.validate_task(task, ['project_id'])
            
            project_id = task['project_id']
            
            logger.info(f"Starting analysis for project: {project_id}")
            
            # Load discovery data
            discovery_data = await self._load_discovery_data(task)
            
            # Emit start event
            await self.emit_event(
                event_type='analysis.started',
                detail={'project_id': project_id},
                project_id=project_id
            )
            
            # Perform technical analysis
            analysis_results = await self._perform_analysis(discovery_data)
            
            # Enrich with metadata
            analysis_results['project_id'] = project_id
            analysis_results['agent_id'] = self.agent_id
            analysis_results['status'] = 'completed'
            analysis_results['based_on_discovery'] = task.get('discovery_s3_uri', 'inline')
            
            # Store analysis data in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='analysis',
                data=analysis_results
            )
            
            analysis_results['s3_uri'] = s3_uri
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={
                    'last_analysis': s3_uri,
                    'complexity_level': analysis_results.get('complexity_assessment', {}).get('level')
                }
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='analysis.completed',
                detail={
                    'project_id': project_id,
                    's3_uri': s3_uri,
                    'complexity': analysis_results.get('complexity_assessment', {}).get('level'),
                    'architecture': analysis_results.get('recommended_architecture', {}).get('pattern')
                },
                project_id=project_id
            )
            
            logger.info(f"Analysis completed for project: {project_id}")
            self.analysis_data = analysis_results
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            
            # Emit failure event
            await self.emit_event(
                event_type='analysis.failed',
                detail={
                    'project_id': task.get('project_id'),
                    'error': str(e)
                },
                project_id=task.get('project_id')
            )
            
            raise
    
    async def _load_discovery_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load discovery data from task or S3
        
        Args:
            task: Task data containing discovery info
            
        Returns:
            Discovery data dictionary
        """
        # Check if discovery data is directly provided
        if 'discovery_data' in task:
            return task['discovery_data']
        
        # Check if S3 URI is provided
        if 'discovery_s3_uri' in task:
            return await self.load_data(task['discovery_s3_uri'])
        
        # Try to load from state
        project_id = task['project_id']
        state = await self.load_state(project_id)
        
        if state and 'last_discovery' in state:
            return await self.load_data(state['last_discovery'])
        
        raise ValueError("No discovery data available. Run DiscoveryAgent first.")
    
    async def _perform_analysis(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform deep technical analysis using AI
        
        Args:
            discovery_data: Discovery results
            
        Returns:
            Structured analysis data
        """
        import json
        
        # Build comprehensive analysis prompt
        prompt = f"""Perform a deep technical analysis based on the following discovery data:

DISCOVERY DATA:
{json.dumps(discovery_data, indent=2)}

Provide a comprehensive technical analysis in JSON format as specified.
Focus on practical, actionable recommendations."""
        
        # Invoke AI for analysis
        ai_response = await self.invoke_ai(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.4  # Balanced creativity and determinism
        )
        
        # Parse AI response
        import re
        try:
            analysis_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback: extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group(1))
            else:
                # Last resort: structured fallback
                analysis_data = {
                    'raw_analysis': ai_response,
                    'complexity_assessment': {'level': 'medium', 'reasoning': 'Unable to parse'},
                    'technical_challenges': [],
                    'recommended_architecture': {'pattern': 'unknown'},
                    'scalability_analysis': {},
                    'security_considerations': [],
                    'performance_requirements': {},
                    'integration_points': [],
                    'best_practices': [],
                    'risk_assessment': []
                }
        
        return analysis_data
    
    async def get_architecture_summary(self, project_id: str) -> Optional[str]:
        """
        Get a summary of architecture recommendations
        
        Args:
            project_id: Project identifier
            
        Returns:
            Human-readable architecture summary
        """
        state = await self.load_state(project_id)
        if not state or 'last_analysis' not in state:
            return None
        
        analysis_data = await self.load_data(state['last_analysis'])
        
        arch = analysis_data.get('recommended_architecture', {})
        complexity = analysis_data.get('complexity_assessment', {})
        
        summary = f"""Architecture Recommendation:
Pattern: {arch.get('pattern', 'N/A')}
Complexity: {complexity.get('level', 'N/A')}
Reasoning: {arch.get('reasoning', 'N/A')}

Key Considerations:
{self._format_list(analysis_data.get('technical_challenges', [])[:3])}

Security:
{self._format_list(analysis_data.get('security_considerations', [])[:3])}
"""
        return summary
    
    def _format_list(self, items: List) -> str:
        """Format list items for display"""
        if not items:
            return "  - None specified"
        formatted = []
        for item in items:
            if isinstance(item, dict):
                formatted.append(f"  - {item.get('name', item.get('description', str(item)))}")
            else:
                formatted.append(f"  - {item}")
        return '\n'.join(formatted)
