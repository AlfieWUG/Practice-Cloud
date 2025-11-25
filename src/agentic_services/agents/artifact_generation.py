"""
Artifact Generation Agent for Nagarro Agentic Services Platform
Generates code, documentation, and configuration artifacts
"""

import logging
from typing import Dict, Any, Optional, List

from agentic_services.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class ArtifactGenerationAgent(BaseAgent):
    """
    Artifact Generation Agent - Fourth agent in the workflow
    
    Responsibilities:
    - Generate code skeletons and boilerplates
    - Create API specifications (OpenAPI/Swagger)
    - Generate database schemas and migrations
    - Create configuration files (Docker, CI/CD, etc.)
    - Generate documentation (README, API docs, architecture diagrams)
    - Create test templates
    """
    
    SYSTEM_PROMPT = """You are an Artifact Generation Agent specialized in creating project artifacts.

Your tasks:
1. Generate code structure and boilerplate
2. Create API specifications (OpenAPI/Swagger)
3. Generate database schemas (SQL, NoSQL)
4. Create Docker and docker-compose configurations
5. Generate CI/CD pipeline configs (GitHub Actions, GitLab CI, Jenkins)
6. Create comprehensive documentation (README, CONTRIBUTING, API docs)
7. Generate test templates and fixtures
8. Create Infrastructure as Code (Terraform, CloudFormation, CDK)

Return structured JSON with:
- artifacts: list of artifacts with type, filename, content, description
- structure: project directory structure as nested object
- documentation: object with readme, api_docs, architecture_docs
- configurations: object with docker, ci_cd, environment_configs
- code_templates: list of code files with language, path, content
- database_schemas: list of schema definitions
- api_specifications: OpenAPI/GraphQL specs
- testing_templates: list of test files and fixtures

Generate production-ready, well-commented code following best practices."""

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.generated_artifacts: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute artifact generation
        
        Args:
            task: Must contain:
                - project_id: Unique project identifier
                - planning_data: Planning results (or s3_uri to load)
                - artifact_types: Optional list of artifact types to generate
        
        Returns:
            Generated artifacts and files
        """
        try:
            # Validate inputs
            self.validate_task(task, ['project_id'])
            
            project_id = task['project_id']
            artifact_types = task.get('artifact_types', ['all'])
            
            logger.info(f"Starting artifact generation for project: {project_id}")
            
            # Load planning data
            planning_data = await self._load_planning_data(task)
            
            # Emit start event
            await self.emit_event(
                event_type='artifact_generation.started',
                detail={
                    'project_id': project_id,
                    'artifact_types': artifact_types
                },
                project_id=project_id
            )
            
            # Generate artifacts
            artifact_results = await self._generate_artifacts(
                planning_data,
                artifact_types
            )
            
            # Enrich with metadata
            artifact_results['project_id'] = project_id
            artifact_results['agent_id'] = self.agent_id
            artifact_results['status'] = 'completed'
            artifact_results['artifact_types_generated'] = artifact_types
            
            # Store artifacts in S3 (artifacts bucket)
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='artifacts',
                data=artifact_results,
                bucket=self.s3.artifacts_bucket
            )
            
            artifact_results['s3_uri'] = s3_uri
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={
                    'last_artifacts': s3_uri,
                    'total_artifacts': len(artifact_results.get('artifacts', [])),
                    'artifact_types': artifact_types
                }
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='artifact_generation.completed',
                detail={
                    'project_id': project_id,
                    's3_uri': s3_uri,
                    'total_artifacts': len(artifact_results.get('artifacts', []))
                },
                project_id=project_id
            )
            
            logger.info(f"Artifact generation completed for project: {project_id}")
            self.generated_artifacts = artifact_results
            
            return artifact_results
            
        except Exception as e:
            logger.error(f"Artifact generation failed: {e}", exc_info=True)
            
            # Emit failure event
            await self.emit_event(
                event_type='artifact_generation.failed',
                detail={
                    'project_id': task.get('project_id'),
                    'error': str(e)
                },
                project_id=task.get('project_id')
            )
            
            raise
    
    async def _load_planning_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load planning data from task or S3
        
        Args:
            task: Task data containing planning info
            
        Returns:
            Planning data dictionary
        """
        if 'planning_data' in task:
            return task['planning_data']
        
        if 'planning_s3_uri' in task:
            return await self.load_data(task['planning_s3_uri'])
        
        # Try to load from state
        project_id = task['project_id']
        state = await self.load_state(project_id)
        
        if state and 'last_planning' in state:
            return await self.load_data(state['last_planning'])
        
        raise ValueError("No planning data available. Run PlanningAgent first.")
    
    async def _generate_artifacts(
        self,
        planning_data: Dict[str, Any],
        artifact_types: List[str]
    ) -> Dict[str, Any]:
        """
        Generate project artifacts using AI
        
        Args:
            planning_data: Planning results
            artifact_types: Types of artifacts to generate
            
        Returns:
            Structured artifacts data
        """
        import json
        
        # Build artifact generation prompt
        artifact_spec = f"\nGenerate the following artifact types: {', '.join(artifact_types)}"
        
        prompt = f"""Generate comprehensive project artifacts based on the following implementation plan:

PLANNING DATA:
{json.dumps(planning_data, indent=2)}
{artifact_spec}

Provide complete, production-ready artifacts in JSON format as specified.
Include well-commented code and comprehensive documentation."""
        
        # Invoke AI for artifact generation (may need multiple calls for large projects)
        ai_response = await self.invoke_ai(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3  # Lower temperature for consistent code generation
        )
        
        # Parse AI response
        import re
        try:
            artifacts_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback: extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                artifacts_data = json.loads(json_match.group(1))
            else:
                # Last resort: structured fallback
                artifacts_data = {
                    'raw_output': ai_response,
                    'artifacts': [],
                    'structure': {},
                    'documentation': {},
                    'configurations': {},
                    'code_templates': [],
                    'database_schemas': [],
                    'api_specifications': {},
                    'testing_templates': []
                }
        
        return artifacts_data
    
    async def get_artifact_by_type(
        self,
        project_id: str,
        artifact_type: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve specific artifact types
        
        Args:
            project_id: Project identifier
            artifact_type: Type of artifact (e.g., 'code', 'documentation', 'config')
            
        Returns:
            List of matching artifacts
        """
        state = await self.load_state(project_id)
        if not state or 'last_artifacts' not in state:
            return None
        
        artifacts_data = await self.load_data(state['last_artifacts'])
        
        all_artifacts = artifacts_data.get('artifacts', [])
        return [a for a in all_artifacts if a.get('type') == artifact_type]
    
    async def export_artifacts_to_zip(
        self,
        project_id: str,
        output_path: str
    ) -> str:
        """
        Export all artifacts as a ZIP file
        
        Args:
            project_id: Project identifier
            output_path: Local path to save ZIP file
            
        Returns:
            Path to created ZIP file
        """
        import zipfile
        import os
        from datetime import datetime
        
        state = await self.load_state(project_id)
        if not state or 'last_artifacts' not in state:
            raise ValueError("No artifacts found for project")
        
        artifacts_data = await self.load_data(state['last_artifacts'])
        
        # Create ZIP file
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        zip_filename = f"{project_id}_artifacts_{timestamp}.zip"
        zip_path = os.path.join(output_path, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for artifact in artifacts_data.get('artifacts', []):
                filename = artifact.get('filename', 'unnamed.txt')
                content = artifact.get('content', '')
                zipf.writestr(filename, content)
        
        logger.info(f"Exported artifacts to: {zip_path}")
        return zip_path
