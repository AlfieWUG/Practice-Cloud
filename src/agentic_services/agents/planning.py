"""
Planning Agent for Nagarro Agentic Services Platform
Creates implementation plans and roadmaps
"""

import logging
from typing import Dict, Any, Optional, List

from agentic_services.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class PlanningAgent(BaseAgent):
    """
    Planning Agent - Third agent in the workflow
    
    Responsibilities:
    - Create implementation roadmap
    - Break down project into phases and sprints
    - Define milestones and deliverables
    - Estimate effort and resources
    - Prioritize features and tasks
    """
    
    SYSTEM_PROMPT = """You are a Planning Agent specialized in creating software implementation roadmaps.

Your tasks:
1. Create a phased implementation plan
2. Break down work into sprints/iterations (2-week sprints)
3. Define clear milestones and deliverables
4. Estimate effort in story points or hours
5. Prioritize features using MoSCoW (Must/Should/Could/Won't)
6. Identify dependencies between tasks
7. Recommend team composition and skills needed
8. Create risk mitigation timeline

Return structured JSON with:
- phases: list of implementation phases with name, duration, goals
- sprints: list of sprints with tasks, story_points, deliverables
- milestones: list of key milestones with date, deliverables, success_criteria
- prioritization: object with must_have, should_have, could_have, wont_have lists
- effort_estimation: object with total_story_points, total_hours, confidence_level
- dependencies: list of task dependencies and critical path
- team_requirements: object with roles, skills, team_size
- timeline: object with start_date, end_date, buffer_weeks
- risks_timeline: list of time-sensitive risks and mitigation plans

Be realistic with estimates. Consider team velocity, holidays, and buffer time."""

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.planning_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute planning
        
        Args:
            task: Must contain:
                - project_id: Unique project identifier
                - analysis_data: Analysis results (or s3_uri to load)
                - constraints: Optional time/budget/team constraints
        
        Returns:
            Planning results with roadmap and estimates
        """
        try:
            # Validate inputs
            self.validate_task(task, ['project_id'])
            
            project_id = task['project_id']
            constraints = task.get('constraints', {})
            
            logger.info(f"Starting planning for project: {project_id}")
            
            # Load analysis data
            analysis_data = await self._load_analysis_data(task)
            
            # Emit start event
            await self.emit_event(
                event_type='planning.started',
                detail={'project_id': project_id},
                project_id=project_id
            )
            
            # Create implementation plan
            planning_results = await self._create_plan(analysis_data, constraints)
            
            # Enrich with metadata
            planning_results['project_id'] = project_id
            planning_results['agent_id'] = self.agent_id
            planning_results['status'] = 'completed'
            planning_results['constraints_applied'] = constraints
            
            # Store planning data in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='planning',
                data=planning_results
            )
            
            planning_results['s3_uri'] = s3_uri
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={
                    'last_planning': s3_uri,
                    'total_sprints': len(planning_results.get('sprints', [])),
                    'estimated_duration': planning_results.get('timeline', {}).get('total_weeks')
                }
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='planning.completed',
                detail={
                    'project_id': project_id,
                    's3_uri': s3_uri,
                    'total_sprints': len(planning_results.get('sprints', [])),
                    'total_story_points': planning_results.get('effort_estimation', {}).get('total_story_points')
                },
                project_id=project_id
            )
            
            logger.info(f"Planning completed for project: {project_id}")
            self.planning_data = planning_results
            
            return planning_results
            
        except Exception as e:
            logger.error(f"Planning failed: {e}", exc_info=True)
            
            # Emit failure event
            await self.emit_event(
                event_type='planning.failed',
                detail={
                    'project_id': task.get('project_id'),
                    'error': str(e)
                },
                project_id=task.get('project_id')
            )
            
            raise
    
    async def _load_analysis_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load analysis data from task or S3
        
        Args:
            task: Task data containing analysis info
            
        Returns:
            Analysis data dictionary
        """
        if 'analysis_data' in task:
            return task['analysis_data']
        
        if 'analysis_s3_uri' in task:
            return await self.load_data(task['analysis_s3_uri'])
        
        # Try to load from state
        project_id = task['project_id']
        state = await self.load_state(project_id)
        
        if state and 'last_analysis' in state:
            return await self.load_data(state['last_analysis'])
        
        raise ValueError("No analysis data available. Run AnalysisAgent first.")
    
    async def _create_plan(
        self,
        analysis_data: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create implementation plan using AI
        
        Args:
            analysis_data: Analysis results
            constraints: Time/budget/team constraints
            
        Returns:
            Structured planning data
        """
        import json
        
        # Build planning prompt
        constraints_text = ""
        if constraints:
            constraints_text = f"\nCONSTRAINTS:\n{json.dumps(constraints, indent=2)}"
        
        prompt = f"""Create a detailed implementation plan based on the following technical analysis:

ANALYSIS DATA:
{json.dumps(analysis_data, indent=2)}
{constraints_text}

Provide a comprehensive implementation roadmap in JSON format as specified.
Be realistic with timelines and consider all dependencies."""
        
        # Invoke AI for planning
        ai_response = await self.invoke_ai(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.5  # Balance between creativity and structure
        )
        
        # Parse AI response
        import re
        try:
            planning_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback: extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                planning_data = json.loads(json_match.group(1))
            else:
                # Last resort: structured fallback
                planning_data = {
                    'raw_plan': ai_response,
                    'phases': [],
                    'sprints': [],
                    'milestones': [],
                    'prioritization': {
                        'must_have': [],
                        'should_have': [],
                        'could_have': [],
                        'wont_have': []
                    },
                    'effort_estimation': {
                        'total_story_points': 0,
                        'total_hours': 0,
                        'confidence_level': 'low'
                    },
                    'dependencies': [],
                    'team_requirements': {},
                    'timeline': {},
                    'risks_timeline': []
                }
        
        return planning_data
    
    async def get_roadmap_summary(self, project_id: str) -> Optional[str]:
        """
        Get a summary of the implementation roadmap
        
        Args:
            project_id: Project identifier
            
        Returns:
            Human-readable roadmap summary
        """
        state = await self.load_state(project_id)
        if not state or 'last_planning' not in state:
            return None
        
        planning_data = await self.load_data(state['last_planning'])
        
        phases = planning_data.get('phases', [])
        effort = planning_data.get('effort_estimation', {})
        timeline = planning_data.get('timeline', {})
        
        summary_parts = [
            "Implementation Roadmap:",
            f"Duration: {timeline.get('total_weeks', 'N/A')} weeks",
            f"Effort: {effort.get('total_story_points', 'N/A')} story points",
            f"Team Size: {planning_data.get('team_requirements', {}).get('team_size', 'N/A')} members",
            "\nPhases:"
        ]
        
        for i, phase in enumerate(phases, 1):
            summary_parts.append(f"  {i}. {phase.get('name', 'Unknown')} ({phase.get('duration', 'N/A')})")
        
        milestones = planning_data.get('milestones', [])[:3]
        if milestones:
            summary_parts.append("\nKey Milestones:")
            for m in milestones:
                summary_parts.append(f"  - {m.get('name', 'Unknown')}: {m.get('date', 'TBD')}")
        
        return '\n'.join(summary_parts)
