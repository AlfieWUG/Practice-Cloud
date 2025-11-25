"""
Performance Monitor Agent for Nagarro Agentic Services Platform
Monitors performance metrics, establishes baselines, and detects anomalies
"""

import logging
from typing import Dict, Any, Optional, List

from agentic_services.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class PerformanceMonitorAgent(BaseAgent):
    """
    Performance Monitor Agent - Monitors and analyzes system performance
    
    Responsibilities:
    - Collect performance metrics (response time, throughput, errors)
    - Establish performance baselines
    - Detect anomalies and performance degradation
    - Monitor SLA compliance
    - Validate post-migration performance
    - Analyze performance trends
    """
    
    SYSTEM_PROMPT = """You are a Performance Monitor Agent specialized in monitoring and analyzing system performance metrics.

Your tasks:
1. Collect performance metrics (response times, throughput, error rates, resource usage)
2. Establish performance baselines for comparison
3. Detect anomalies and performance degradation
4. Monitor SLA compliance against defined thresholds
5. Validate post-migration performance improvements
6. Analyze performance trends and projections
7. Provide actionable recommendations

Return structured JSON with:
- metrics: object with performance metrics (response_time, throughput, error_rate, cpu_usage, memory_usage, availability)
- anomalies: array of anomaly objects with type, severity, description (optional)
- sla_compliance: object with SLA status for each metric (optional)
- trends: object with trend analysis and projections (optional)
- comparison: object comparing pre/post migration metrics (optional)
- baseline_established: boolean
- baseline_confidence: string (low/medium/high) (optional)
- validation_passed: boolean (optional)
- monitoring_duration_hours: number
- data_points_collected: integer
- recommendation: string (optional)

Include quantitative metrics and clear trend indicators (increasing, decreasing, stable)."""

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id)
        self.agent_type = "performance_monitor"
        self.monitoring_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute performance monitoring
        
        Args:
            task: Must contain:
                - project_id: Unique project identifier
                - target_systems: List of systems to monitor
                - monitoring_duration_hours: Duration to monitor (optional, default: 24)
                - establish_baseline: Whether to establish baseline (optional)
                - detect_anomalies: Whether to detect anomalies (optional)
                - monitor_sla_compliance: Whether to monitor SLA (optional)
                - validate_post_migration: Whether to validate migration (optional)
                - analyze_trends: Whether to analyze trends (optional)
                - baseline_s3_uri: Baseline data location for comparison (optional)
                - sla_thresholds: SLA thresholds dict (optional)
        
        Returns:
            Performance monitoring results with metrics and analysis
        """
        try:
            # Validate inputs
            self.validate_task(task, ['project_id', 'target_systems'])
            
            project_id = task['project_id']
            target_systems = task['target_systems']
            monitoring_duration = task.get('monitoring_duration_hours', 24)
            establish_baseline = task.get('establish_baseline', False)
            detect_anomalies = task.get('detect_anomalies', False)
            monitor_sla = task.get('monitor_sla_compliance', False)
            validate_migration = task.get('validate_post_migration', False)
            analyze_trends = task.get('analyze_trends', False)
            baseline_uri = task.get('baseline_s3_uri')
            sla_thresholds = task.get('sla_thresholds', {})
            
            logger.info(f"Starting performance monitoring for project: {project_id}, systems: {target_systems}")
            
            # Emit start event
            await self.emit_event(
                event_type='monitoring.started',
                detail={
                    'project_id': project_id,
                    'target_systems': target_systems,
                    'monitoring_duration_hours': monitoring_duration
                },
                project_id=project_id
            )
            
            # Perform monitoring
            monitoring_results = await self._perform_monitoring(
                target_systems=target_systems,
                monitoring_duration=monitoring_duration,
                establish_baseline=establish_baseline,
                detect_anomalies=detect_anomalies,
                monitor_sla=monitor_sla,
                validate_migration=validate_migration,
                analyze_trends=analyze_trends,
                baseline_uri=baseline_uri,
                sla_thresholds=sla_thresholds
            )
            
            # Enrich with metadata
            monitoring_results['project_id'] = project_id
            monitoring_results['agent_id'] = self.agent_id
            monitoring_results['status'] = 'completed'
            monitoring_results['target_systems'] = target_systems
            monitoring_results['monitoring_duration_hours'] = monitoring_duration
            
            # Store monitoring results in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='performance_metrics',
                data=monitoring_results
            )
            
            monitoring_results['s3_uri'] = s3_uri
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={'last_monitoring': s3_uri}
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='monitoring.completed',
                detail={
                    'project_id': project_id,
                    's3_uri': s3_uri,
                    'baseline_established': monitoring_results.get('baseline_established', False)
                },
                project_id=project_id
            )
            
            logger.info(f"Performance monitoring completed for project: {project_id}")
            self.monitoring_data = monitoring_results
            
            return monitoring_results
            
        except Exception as e:
            logger.error(f"Performance monitoring failed: {e}", exc_info=True)
            
            # Emit failure event
            await self.emit_event(
                event_type='monitoring.failed',
                detail={
                    'project_id': task.get('project_id'),
                    'target_systems': task.get('target_systems'),
                    'error': str(e)
                },
                project_id=task.get('project_id')
            )
            
            raise
    
    async def _perform_monitoring(
        self,
        target_systems: List[str],
        monitoring_duration: int = 24,
        establish_baseline: bool = False,
        detect_anomalies: bool = False,
        monitor_sla: bool = False,
        validate_migration: bool = False,
        analyze_trends: bool = False,
        baseline_uri: Optional[str] = None,
        sla_thresholds: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Perform performance monitoring using AI
        
        Args:
            target_systems: List of systems to monitor
            monitoring_duration: Hours to monitor
            establish_baseline: Whether to establish baseline
            detect_anomalies: Whether to detect anomalies
            monitor_sla: Whether to monitor SLA
            validate_migration: Whether to validate migration
            analyze_trends: Whether to analyze trends
            baseline_uri: Baseline data location
            sla_thresholds: SLA thresholds
            
        Returns:
            Structured monitoring data
        """
        # Build comprehensive prompt
        systems_list = ', '.join(target_systems)
        
        analysis_sections = []
        
        if establish_baseline:
            analysis_sections.append("""
BASELINE ESTABLISHMENT:
- Collect comprehensive performance data over monitoring period
- Calculate statistical baselines (mean, median, percentiles)
- Determine confidence level of baseline
- Identify normal operating ranges for all metrics
""")
        
        if detect_anomalies:
            analysis_sections.append("""
ANOMALY DETECTION:
- Identify significant deviations from baseline
- Classify anomaly severity (low, medium, high, critical)
- Determine anomaly duration and impact
- Suggest possible root causes
""")
        
        if monitor_sla:
            sla_details = f"SLA Thresholds: {sla_thresholds}" if sla_thresholds else "Use standard SLA thresholds"
            analysis_sections.append(f"""
SLA COMPLIANCE MONITORING:
{sla_details}
- Compare current metrics against SLA thresholds
- Calculate compliance margin
- Flag SLA violations
""")
        
        if validate_migration:
            analysis_sections.append("""
POST-MIGRATION VALIDATION:
- Compare pre-migration baseline vs post-migration metrics
- Calculate improvement/degradation percentages
- Verify SLA compliance after migration
- Provide overall migration verdict (improved, degraded, stable)
""")
        
        if analyze_trends:
            analysis_sections.append("""
TREND ANALYSIS:
- Analyze metric trends (increasing, decreasing, stable)
- Calculate trend rates
- Project future values (30-day projection)
- Identify concerning trends requiring attention
""")
        
        analysis_text = '\n'.join(analysis_sections) if analysis_sections else ""
        
        prompt = f"""Monitor performance of the following systems:

TARGET SYSTEMS: {systems_list}
MONITORING DURATION: {monitoring_duration} hours

Collect and analyze:
1. Response time metrics (avg, p50, p95, p99)
2. Throughput (requests per second)
3. Error rates (percentage)
4. Resource usage (CPU, memory)
5. Availability/uptime

{analysis_text}

Provide comprehensive performance monitoring data in JSON format as specified.
Include quantitative metrics and actionable insights."""
        
        # Invoke AI for monitoring analysis
        ai_response = await self.invoke_ai(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.2  # Lower temperature for accurate metrics
        )
        
        # Parse AI response
        import json
        try:
            monitoring_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback: extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                monitoring_data = json.loads(json_match.group(1))
            else:
                # Last resort: create structured response
                monitoring_data = {
                    'raw_monitoring': ai_response,
                    'metrics': {},
                    'baseline_established': establish_baseline,
                    'monitoring_duration_hours': monitoring_duration,
                    'message': 'Monitoring completed with limited structure'
                }
        
        return monitoring_data
