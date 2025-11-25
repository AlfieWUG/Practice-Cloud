"""
Workflow Orchestrator for Nagarro Agentic Services Platform
Coordinates the execution of AI agents in the proper sequence
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from agentic_services.agents import (
    DiscoveryAgent,
    AnalysisAgent,
    PlanningAgent,
    ArtifactGenerationAgent
)

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowOrchestrator:
    """
    Orchestrates the multi-agent workflow
    
    Standard workflow:
    1. Discovery → Analyze requirements
    2. Analysis → Deep technical analysis
    3. Planning → Create implementation roadmap
    4. Artifact Generation → Generate code and documentation
    
    Can also run agents individually or in custom sequences
    """
    
    def __init__(self, workflow_id: Optional[str] = None):
        """
        Initialize orchestrator
        
        Args:
            workflow_id: Unique workflow identifier (generated if not provided)
        """
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.status = WorkflowStatus.PENDING
        self.execution_log: List[Dict[str, Any]] = []
        
        # Initialize agents
        self.discovery_agent = DiscoveryAgent()
        self.analysis_agent = AnalysisAgent()
        self.planning_agent = PlanningAgent()
        self.artifact_agent = ArtifactGenerationAgent()
        
        logger.info(f"Initialized workflow orchestrator: {self.workflow_id}")
    
    async def execute_full_workflow(
        self,
        project_id: str,
        requirements: str,
        context: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete workflow from discovery to artifact generation
        
        Args:
            project_id: Unique project identifier
            requirements: Project requirements text
            context: Optional additional context
            constraints: Optional time/budget/team constraints
            
        Returns:
            Complete workflow results with all agent outputs
        """
        try:
            self.status = WorkflowStatus.RUNNING
            start_time = datetime.utcnow()
            
            logger.info(f"Starting full workflow for project: {project_id}")
            
            results = {
                'workflow_id': self.workflow_id,
                'project_id': project_id,
                'start_time': start_time.isoformat(),
                'agents_executed': []
            }
            
            # Step 1: Discovery
            logger.info("Step 1/4: Running DiscoveryAgent...")
            discovery_result = await self.discovery_agent.execute({
                'project_id': project_id,
                'requirements': requirements,
                'context': context or ''
            })
            results['discovery'] = discovery_result
            results['agents_executed'].append('DiscoveryAgent')
            self._log_step('discovery', 'completed', discovery_result)
            
            # Step 2: Analysis
            logger.info("Step 2/4: Running AnalysisAgent...")
            analysis_result = await self.analysis_agent.execute({
                'project_id': project_id,
                'discovery_data': discovery_result
            })
            results['analysis'] = analysis_result
            results['agents_executed'].append('AnalysisAgent')
            self._log_step('analysis', 'completed', analysis_result)
            
            # Step 3: Planning
            logger.info("Step 3/4: Running PlanningAgent...")
            planning_result = await self.planning_agent.execute({
                'project_id': project_id,
                'analysis_data': analysis_result,
                'constraints': constraints or {}
            })
            results['planning'] = planning_result
            results['agents_executed'].append('PlanningAgent')
            self._log_step('planning', 'completed', planning_result)
            
            # Step 4: Artifact Generation
            logger.info("Step 4/4: Running ArtifactGenerationAgent...")
            artifact_result = await self.artifact_agent.execute({
                'project_id': project_id,
                'planning_data': planning_result,
                'artifact_types': ['all']
            })
            results['artifacts'] = artifact_result
            results['agents_executed'].append('ArtifactGenerationAgent')
            self._log_step('artifact_generation', 'completed', artifact_result)
            
            # Complete workflow
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            self.status = WorkflowStatus.COMPLETED
            results['status'] = self.status.value
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = duration
            results['execution_log'] = self.execution_log
            
            logger.info(f"Workflow completed successfully in {duration:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}", exc_info=True)
            self.status = WorkflowStatus.FAILED
            self._log_step('workflow', 'failed', {'error': str(e)})
            raise
    
    async def execute_discovery_only(
        self,
        project_id: str,
        requirements: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute only the discovery phase"""
        logger.info(f"Running discovery-only workflow for project: {project_id}")
        return await self.discovery_agent.execute({
            'project_id': project_id,
            'requirements': requirements,
            'context': context or ''
        })
    
    async def execute_from_discovery(
        self,
        project_id: str,
        discovery_s3_uri: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow starting from existing discovery data
        
        Args:
            project_id: Project identifier
            discovery_s3_uri: S3 URI of discovery results
            constraints: Optional constraints
            
        Returns:
            Workflow results from analysis onwards
        """
        try:
            self.status = WorkflowStatus.RUNNING
            start_time = datetime.utcnow()
            
            logger.info(f"Starting workflow from discovery for project: {project_id}")
            
            results = {
                'workflow_id': self.workflow_id,
                'project_id': project_id,
                'start_time': start_time.isoformat(),
                'agents_executed': []
            }
            
            # Analysis
            logger.info("Running AnalysisAgent...")
            analysis_result = await self.analysis_agent.execute({
                'project_id': project_id,
                'discovery_s3_uri': discovery_s3_uri
            })
            results['analysis'] = analysis_result
            results['agents_executed'].append('AnalysisAgent')
            
            # Planning
            logger.info("Running PlanningAgent...")
            planning_result = await self.planning_agent.execute({
                'project_id': project_id,
                'analysis_data': analysis_result,
                'constraints': constraints or {}
            })
            results['planning'] = planning_result
            results['agents_executed'].append('PlanningAgent')
            
            # Artifact Generation
            logger.info("Running ArtifactGenerationAgent...")
            artifact_result = await self.artifact_agent.execute({
                'project_id': project_id,
                'planning_data': planning_result
            })
            results['artifacts'] = artifact_result
            results['agents_executed'].append('ArtifactGenerationAgent')
            
            # Complete
            end_time = datetime.utcnow()
            results['status'] = WorkflowStatus.COMPLETED.value
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = (end_time - start_time).total_seconds()
            
            self.status = WorkflowStatus.COMPLETED
            logger.info("Workflow completed successfully")
            
            return results
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}", exc_info=True)
            self.status = WorkflowStatus.FAILED
            raise
    
    async def resume_workflow(
        self,
        project_id: str,
        from_agent: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Resume workflow from a specific agent
        
        Args:
            project_id: Project identifier
            from_agent: Agent to resume from ('analysis', 'planning', 'artifacts')
            constraints: Optional constraints
            
        Returns:
            Workflow results
        """
        logger.info(f"Resuming workflow from {from_agent} for project: {project_id}")
        
        if from_agent == 'analysis':
            return await self.execute_from_discovery(project_id, None, constraints)
        elif from_agent == 'planning':
            # Run planning and artifacts only
            planning_result = await self.planning_agent.execute({
                'project_id': project_id,
                'constraints': constraints or {}
            })
            artifact_result = await self.artifact_agent.execute({
                'project_id': project_id,
                'planning_data': planning_result
            })
            return {
                'planning': planning_result,
                'artifacts': artifact_result
            }
        elif from_agent == 'artifacts':
            # Run artifacts only
            return await self.artifact_agent.execute({
                'project_id': project_id
            })
        else:
            raise ValueError(f"Unknown agent: {from_agent}")
    
    def _log_step(
        self,
        step_name: str,
        status: str,
        result: Dict[str, Any]
    ):
        """Log a workflow step"""
        self.execution_log.append({
            'step': step_name,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            's3_uri': result.get('s3_uri'),
            'agent_id': result.get('agent_id')
        })
    
    def get_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            'workflow_id': self.workflow_id,
            'status': self.status.value,
            'steps_completed': len(self.execution_log),
            'execution_log': self.execution_log
        }
