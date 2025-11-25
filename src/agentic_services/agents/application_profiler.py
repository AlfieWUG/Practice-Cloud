"""
Application Profiler Agent for Nagarro Agentic Services Platform
Profiles application performance, resource usage, and scaling patterns
"""

import logging
from typing import Dict, Any, Optional, List

from agentic_services.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class ApplicationProfilerAgent(BaseAgent):
    """
    Application Profiler Agent - Analyzes application performance and resource usage
    
    Responsibilities:
    - Profile application performance (response times, throughput)
    - Analyze resource usage (CPU, memory, disk I/O)
    - Identify scaling patterns and peak load times
    - Detect performance bottlenecks
    - Analyze application dependencies
    - Assess cloud readiness
    - Provide optimization recommendations
    """
    
    SYSTEM_PROMPT = """You are an Application Profiler Agent specialized in analyzing application performance and resource usage.

Your tasks:
1. Profile application performance metrics (response times, throughput, latency)
2. Analyze resource consumption (CPU, memory, disk I/O, network)
3. Identify scaling patterns and traffic peaks
4. Detect performance bottlenecks and inefficiencies
5. Map application dependencies (databases, APIs, services)
6. Assess cloud migration readiness
7. Provide optimization and right-sizing recommendations

Return structured JSON with:
- applications: array of application objects with:
  - name: string
  - type: string (web_application, rest_api, microservice, etc.)
  - technology: string
  - version: string
  - performance: object with response_time_ms, throughput_rps
  - resource_usage: object with cpu_percent, memory_mb, disk_io_mbps
  - scaling_patterns: object with pattern_type, peak_hours, scaling_factor (optional)
  - dependencies: object with databases, external_apis, internal_services (optional)
  - bottlenecks: array of bottleneck objects (optional)
  - cloud_readiness: object with score, rating, factors (optional)
- total_applications: integer count
- profiling_duration_hours: number
- peak_load_time: string timestamp (optional)
- message: string with additional information (optional)

Be thorough and data-driven. Include quantitative metrics and actionable insights."""

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.agent_type = "application_profiler"
        self.profile_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute application profiling
        
        Args:
            task: Must contain:
                - project_id: Unique project identifier
                - target_servers: List of servers to profile
                - profiling_duration_hours: Duration to profile (optional, default: 24)
                - include_scaling_analysis: Whether to analyze scaling patterns (optional)
                - include_dependencies: Whether to map dependencies (optional)
                - identify_bottlenecks: Whether to identify bottlenecks (optional)
                - assess_cloud_readiness: Whether to assess cloud readiness (optional)
        
        Returns:
            Application profiling results with performance and resource data
        """
        try:
            # Validate inputs
            self.validate_task(task, ['project_id', 'target_servers'])
            
            project_id = task['project_id']
            target_servers = task['target_servers']
            profiling_duration = task.get('profiling_duration_hours', 24)
            include_scaling = task.get('include_scaling_analysis', False)
            include_dependencies = task.get('include_dependencies', False)
            identify_bottlenecks = task.get('identify_bottlenecks', False)
            assess_cloud_readiness = task.get('assess_cloud_readiness', False)
            
            logger.info(f"Starting application profiling for project: {project_id}, servers: {target_servers}")
            
            # Emit start event
            await self.emit_event(
                event_type='profiling.started',
                detail={
                    'project_id': project_id,
                    'target_servers': target_servers,
                    'profiling_duration_hours': profiling_duration
                },
                project_id=project_id
            )
            
            # Perform application profiling
            profile_results = await self._perform_profiling(
                target_servers=target_servers,
                profiling_duration=profiling_duration,
                include_scaling=include_scaling,
                include_dependencies=include_dependencies,
                identify_bottlenecks=identify_bottlenecks,
                assess_cloud_readiness=assess_cloud_readiness
            )
            
            # Enrich with metadata
            profile_results['project_id'] = project_id
            profile_results['agent_id'] = self.agent_id
            profile_results['status'] = 'completed'
            profile_results['target_servers'] = target_servers
            profile_results['profiling_duration_hours'] = profiling_duration
            
            # Store profile results in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='application_profile',
                data=profile_results
            )
            
            profile_results['s3_uri'] = s3_uri
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={'last_profile': s3_uri}
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='profiling.completed',
                detail={
                    'project_id': project_id,
                    's3_uri': s3_uri,
                    'total_applications': profile_results.get('total_applications', 0)
                },
                project_id=project_id
            )
            
            logger.info(
                f"Application profiling completed for project: {project_id}, "
                f"found {profile_results.get('total_applications', 0)} applications"
            )
            self.profile_data = profile_results
            
            return profile_results
            
        except Exception as e:
            logger.error(f"Application profiling failed: {e}", exc_info=True)
            
            # Emit failure event
            await self.emit_event(
                event_type='profiling.failed',
                detail={
                    'project_id': task.get('project_id'),
                    'target_servers': task.get('target_servers'),
                    'error': str(e)
                },
                project_id=task.get('project_id')
            )
            
            raise
    
    async def _perform_profiling(
        self,
        target_servers: List[str],
        profiling_duration: int = 24,
        include_scaling: bool = False,
        include_dependencies: bool = False,
        identify_bottlenecks: bool = False,
        assess_cloud_readiness: bool = False
    ) -> Dict[str, Any]:
        """
        Perform application profiling using AI
        
        Args:
            target_servers: List of servers to profile
            profiling_duration: Hours to profile
            include_scaling: Whether to analyze scaling patterns
            include_dependencies: Whether to map dependencies
            identify_bottlenecks: Whether to identify bottlenecks
            assess_cloud_readiness: Whether to assess cloud readiness
            
        Returns:
            Structured application profiling data
        """
        # Build comprehensive prompt
        servers_list = ', '.join(target_servers)
        
        analysis_sections = []
        if include_scaling:
            analysis_sections.append("""
SCALING PATTERN ANALYSIS:
- Identify traffic patterns (predictable peaks, unpredictable spikes, steady load)
- Determine peak hours and baseline throughput
- Calculate scaling factors needed
- Recommend autoscaling configuration
""")
        
        if include_dependencies:
            analysis_sections.append("""
DEPENDENCY MAPPING:
- Identify database connections and query patterns
- Map external API calls and latencies
- Trace internal service dependencies
- Measure dependency call frequencies
""")
        
        if identify_bottlenecks:
            analysis_sections.append("""
BOTTLENECK IDENTIFICATION:
- Detect slow database queries (N+1 problems, missing indexes)
- Identify inefficient algorithms or code
- Find resource contention issues
- Locate network latency problems
- Assess impact and provide recommendations
""")
        
        if assess_cloud_readiness:
            analysis_sections.append("""
CLOUD READINESS ASSESSMENT:
- Evaluate statelessness
- Check containerizability
- Assess horizontal scalability
- Identify local storage dependencies
- Flag hardcoded configurations
- Score overall cloud readiness (0-100)
- Recommend migration strategy (rehost, replatform, refactor)
""")
        
        analysis_text = '\n'.join(analysis_sections) if analysis_sections else ""
        
        prompt = f"""Profile the applications running on the following servers:

TARGET SERVERS: {servers_list}
PROFILING DURATION: {profiling_duration} hours

Collect and analyze:
1. Application identification (name, type, technology stack, version)
2. Performance metrics (response times, throughput, latency percentiles)
3. Resource consumption (CPU, memory, disk I/O, network)
4. Load patterns over profiling period
5. Peak usage times and baseline usage

{analysis_text}

Provide comprehensive application profiling data in JSON format as specified.
Include quantitative metrics and actionable recommendations."""
        
        # Invoke AI for profiling analysis
        ai_response = await self.invoke_ai(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.2  # Lower temperature for accurate data analysis
        )
        
        # Parse AI response
        import json
        try:
            profile_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback: extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                profile_data = json.loads(json_match.group(1))
            else:
                # Last resort: create structured response from text
                profile_data = {
                    'raw_profile': ai_response,
                    'applications': [],
                    'total_applications': 0,
                    'profiling_duration_hours': profiling_duration,
                    'message': 'Profiling completed with limited structure'
                }
        
        return profile_data
    
    async def get_profile_summary(self, project_id: str) -> Optional[str]:
        """
        Get a text summary of the application profiling results
        
        Args:
            project_id: Project identifier
            
        Returns:
            Human-readable summary or None if not available
        """
        if not self.profile_data:
            # Try to load from state
            state = await self.load_state(project_id)
            if not state or 'last_profile' not in state:
                return None
            
            # Load from S3
            profile_data = await self.load_data(state['last_profile'])
            self.profile_data = profile_data
        
        # Generate summary
        total_apps = self.profile_data.get('total_applications', 0)
        duration = self.profile_data.get('profiling_duration_hours', 0)
        
        applications = self.profile_data.get('applications', [])
        
        summary = f"""Application Profiling Summary:
Total Applications: {total_apps}
Profiling Duration: {duration} hours

Applications Profiled:
"""
        for i, app in enumerate(applications[:5], 1):
            name = app.get('name', 'unknown')
            tech = app.get('technology', 'unknown')
            perf = app.get('performance', {})
            resource = app.get('resource_usage', {})
            
            avg_response = perf.get('avg_response_time_ms', 'N/A')
            throughput = perf.get('throughput_rps', 'N/A')
            cpu = resource.get('cpu_avg_percent', 'N/A')
            memory = resource.get('memory_avg_mb', 'N/A')
            
            summary += f"{i}. {name} ({tech})\n"
            summary += f"   Performance: {avg_response}ms avg, {throughput} rps\n"
            summary += f"   Resources: {cpu}% CPU, {memory}MB RAM\n"
            
            # Add bottlenecks if present
            bottlenecks = app.get('bottlenecks', [])
            if bottlenecks:
                high_severity = [b for b in bottlenecks if b.get('severity') == 'high']
                if high_severity:
                    summary += f"   ⚠️  {len(high_severity)} high-severity bottleneck(s) detected\n"
        
        return summary
