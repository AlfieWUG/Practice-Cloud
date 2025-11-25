"""
DependencyMapperAgent - Maps application dependencies and relationships
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base import BaseAgent, bedrock_client, s3_client, dynamodb_client, eventbridge_client


class DependencyMapperAgent(BaseAgent):
    """
    Agent responsible for mapping application dependencies and relationships.
    
    Capabilities:
    - Library and package dependency analysis
    - Inter-service dependency mapping
    - API endpoint discovery and relationships
    - Database connection mapping
    - External service dependencies
    - Dependency version tracking
    - Compatibility assessment
    - Circular dependency detection
    - Critical path identification
    """
    
    SYSTEM_PROMPT = """You are a software architecture expert specializing in dependency analysis for cloud migrations.

Your responsibilities:
1. Map all application dependencies (libraries, packages, frameworks)
2. Identify inter-service dependencies and communication patterns
3. Discover API endpoints and their relationships
4. Map database connections and data flows
5. Identify external service dependencies (3rd party APIs, SaaS)
6. Track dependency versions and compatibility
7. Detect circular dependencies and potential issues
8. Identify critical paths and single points of failure

For dependency analysis:
- DIRECT DEPENDENCIES: Immediate dependencies declared in manifest files
- TRANSITIVE DEPENDENCIES: Dependencies of dependencies
- RUNTIME DEPENDENCIES: Services, databases, APIs required at runtime
- BUILD DEPENDENCIES: Tools and libraries needed for compilation/build
- OPTIONAL DEPENDENCIES: Non-critical dependencies for enhanced features

Dependency types to identify:
- Code libraries (npm, pip, maven, nuget, etc.)
- System libraries and OS dependencies
- Database connections (PostgreSQL, MySQL, MongoDB, Redis, etc.)
- Message queues (RabbitMQ, Kafka, SQS, etc.)
- External APIs and webhooks
- Cloud services (AWS, Azure, GCP)
- Authentication providers (OAuth, SAML, LDAP)
- Monitoring and logging services

Version compatibility analysis:
- Identify version conflicts
- Check for deprecated versions
- Flag security vulnerabilities
- Recommend upgrade paths
- Assess cloud compatibility

Dependency health metrics:
- Maintenance status (active, deprecated, abandoned)
- Security vulnerability count
- License compatibility
- Cloud-native alternatives available
- Migration complexity score (1-10)

For each dependency, provide:
- Name and version
- Type and purpose
- Criticality level (critical, high, medium, low)
- Cloud compatibility assessment
- Recommended migration approach
- Alternative options if needed

Identify dependency clusters and service boundaries for microservices decomposition opportunities."""

    def __init__(self, agent_id: Optional[str] = None):
        """Initialize DependencyMapperAgent"""
        super().__init__(agent_id)
        self.agent_type = "dependency_mapper"
        self.dependency_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute dependency mapping
        
        Args:
            task: Task definition containing:
                - project_id: Project identifier
                - applications: List of applications to analyze
                - include_transitive: Whether to include transitive dependencies (optional, default: True)
                - detect_circular: Whether to detect circular dependencies (optional, default: True)
                - assess_compatibility: Whether to assess cloud compatibility (optional, default: True)
                - identify_vulnerabilities: Whether to check for security vulnerabilities (optional, default: True)
        
        Returns:
            Dependency map with applications, dependencies, relationships, and recommendations
        """
        project_id = task.get('project_id')
        if not project_id:
            raise ValueError("project_id is required")
        
        applications = task.get('applications')
        if not applications:
            raise ValueError("applications is required")
        
        try:
            # Emit start event
            await self.emit_event(
                event_type='dependency_mapping.started',
                detail={
                    'application_count': len(applications)
                },
                project_id=project_id
            )
            
            # Perform dependency mapping using AI
            dependency_results = await self._map_dependencies(
                project_id, 
                applications,
                task
            )
            
            # Enrich results with metadata
            dependency_results['status'] = 'completed'
            dependency_results['agent_id'] = self.agent_id
            dependency_results['project_id'] = project_id
            dependency_results['timestamp'] = datetime.utcnow().isoformat()
            
            # Store results in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='dependency_map',
                data=dependency_results
            )
            
            result = {
                'status': 'completed',
                'agent_id': self.agent_id,
                'project_id': project_id,
                'applications': dependency_results.get('applications', []),
                'dependency_graph': dependency_results.get('dependency_graph', {}),
                'circular_dependencies': dependency_results.get('circular_dependencies', []),
                'critical_paths': dependency_results.get('critical_paths', []),
                'vulnerability_summary': dependency_results.get('vulnerability_summary', {}),
                'compatibility_assessment': dependency_results.get('compatibility_assessment', {}),
                'total_dependencies': dependency_results.get('total_dependencies', 0),
                'recommendations': dependency_results.get('recommendations', []),
                's3_uri': s3_uri,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={
                    'last_mapping': result,
                    'application_count': len(applications),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='dependency_mapping.completed',
                detail={
                    'application_count': len(applications),
                    'total_dependencies': result.get('total_dependencies', 0),
                    'circular_dependencies_found': len(result.get('circular_dependencies', []))
                },
                project_id=project_id
            )
            
            self.dependency_data = result
            return result
            
        except Exception as e:
            await self.emit_event(
                event_type='dependency_mapping.failed',
                detail={
                    'error': str(e)
                },
                project_id=project_id
            )
            raise
    
    async def _map_dependencies(
        self, 
        project_id: str, 
        applications: List[Dict[str, Any]],
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to map application dependencies
        
        Args:
            project_id: Project identifier
            applications: List of applications to analyze
            task: Task configuration with optional flags
        
        Returns:
            Dependency mapping results
        """
        # Build analysis request based on task flags
        analysis_options = {
            'include_transitive': task.get('include_transitive', True),
            'detect_circular': task.get('detect_circular', True),
            'assess_compatibility': task.get('assess_compatibility', True),
            'identify_vulnerabilities': task.get('identify_vulnerabilities', True)
        }
        
        prompt = f"""Analyze the following applications and map their dependencies:

Applications:
{json.dumps(applications, indent=2)}

Analysis Options:
{json.dumps(analysis_options, indent=2)}

Please provide a comprehensive dependency analysis in JSON format with:
1. applications: Array of analyzed applications with their dependencies
2. dependency_graph: Complete dependency graph showing relationships
3. circular_dependencies: List of circular dependency chains (if any)
4. critical_paths: Key dependency paths that could impact migration
5. vulnerability_summary: Security vulnerabilities by severity
6. compatibility_assessment: Cloud compatibility for each dependency
7. total_dependencies: Total count of unique dependencies
8. recommendations: Actionable recommendations for dependency management

For each application include:
- name: Application name
- dependencies: List of direct dependencies with versions
- transitive_dependencies: Dependencies of dependencies (if requested)
- external_services: External APIs and services
- database_connections: Database dependencies
- runtime_requirements: Runtime environment needs

For each dependency include:
- name: Dependency name
- version: Current version
- type: Type of dependency (library, service, database, etc.)
- criticality: Importance level (critical, high, medium, low)
- cloud_compatible: Whether it's cloud-ready
- vulnerabilities: Known security issues
- recommended_version: Suggested version for cloud migration
- migration_complexity: Complexity score (1-10)

Focus on identifying migration blockers and providing actionable recommendations."""

        response = await self.invoke_ai(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3  # Lower temperature for more deterministic analysis
        )
        
        # Parse AI response
        try:
            # Try to parse JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result = json.loads(response[json_start:json_end])
            else:
                # Fallback: structure the response
                result = {
                    'applications': applications,
                    'dependency_graph': {},
                    'circular_dependencies': [],
                    'critical_paths': [],
                    'vulnerability_summary': {},
                    'compatibility_assessment': {},
                    'total_dependencies': 0,
                    'recommendations': ['AI response could not be parsed as JSON'],
                    'raw_analysis': response
                }
        except json.JSONDecodeError:
            result = {
                'applications': applications,
                'dependency_graph': {},
                'circular_dependencies': [],
                'critical_paths': [],
                'vulnerability_summary': {},
                'compatibility_assessment': {},
                'total_dependencies': 0,
                'recommendations': ['AI response could not be parsed as JSON'],
                'raw_analysis': response
            }
        
        return result
    
    def get_dependency_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent dependency mapping data
        
        Returns:
            Dependency mapping data or None if not available
        """
        return self.dependency_data
