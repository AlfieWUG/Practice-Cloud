"""
CapacityPlannerAgent - Plans capacity and resource sizing for cloud migration
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseAgent, bedrock_client, s3_client, dynamodb_client, eventbridge_client


class CapacityPlannerAgent(BaseAgent):
    """
    Agent responsible for capacity planning and resource sizing.
    
    Capabilities:
    - Current capacity analysis
    - Future capacity projection
    - Resource sizing recommendations
    - Scaling strategy design
    - Performance requirements mapping
    - Growth accommodation planning
    - Peak load handling
    - Cost-optimized capacity planning
    """
    
    SYSTEM_PROMPT = """You are a capacity planning expert specializing in cloud infrastructure sizing and scaling.

Your responsibilities:
1. Analyze current capacity utilization
2. Project future capacity needs based on growth
3. Recommend optimal resource sizing
4. Design auto-scaling strategies
5. Map performance requirements to resources
6. Plan for peak load scenarios
7. Balance cost vs. performance
8. Ensure adequate headroom for growth

Capacity Planning Methodology:

Current State Analysis:
- CPU utilization patterns (average, peak, p95, p99)
- Memory usage trends
- Storage capacity and growth rate
- Network bandwidth utilization
- I/O patterns (IOPS, throughput)
- Request rates and response times
- Concurrent user/connection counts
- Database query performance

Future Projection Factors:
- Historical growth rates (monthly, quarterly, annual)
- Business growth projections
- Seasonal variations and trends
- Marketing campaigns and events
- New feature rollouts
- Geographic expansion plans
- Expected user base growth

Resource Sizing Considerations:

Compute (EC2/VMs):
- CPU cores and architecture (x86, ARM/Graviton)
- Memory requirements
- Instance families (general purpose, compute optimized, memory optimized)
- Burstable vs. consistent performance
- Right-sizing opportunities (oversized/undersized instances)

Storage:
- IOPS requirements (SSD vs. HDD)
- Throughput needs (MB/s)
- Capacity planning with growth buffer
- Storage tiers (hot, warm, cold, archive)
- Backup and snapshot storage

Databases:
- Connection pool sizing
- Query performance requirements
- Read/write ratio
- Replication needs
- Backup windows and retention

Networking:
- Bandwidth requirements
- Latency targets
- Data transfer volumes
- Load balancer capacity
- CDN coverage

Scaling Strategies:

Vertical Scaling:
- When to scale up (increase instance size)
- Instance type upgrades
- Limitations and ceilings

Horizontal Scaling:
- When to scale out (add more instances)
- Load balancing strategies
- State management (stateless vs. stateful)
- Auto-scaling triggers and thresholds

Auto-Scaling Configuration:
- Target tracking (CPU, memory, request count)
- Step scaling policies
- Scheduled scaling (predictable patterns)
- Cool-down periods
- Min/max instance counts
- Scale-in protection

Performance Targets:
- Response time requirements (p50, p95, p99)
- Throughput goals (requests/second, transactions/minute)
- Availability targets (99.9%, 99.95%, 99.99%)
- Concurrent user capacity
- Data processing throughput

Peak Load Planning:
- Expected peak capacity (Black Friday, year-end, etc.)
- Burst capacity requirements
- Pre-warming strategies
- Load testing recommendations

Cost Optimization:
- Right-sizing to avoid over-provisioning
- Reserved capacity for baseline load
- Spot/preemptible instances for variable workload
- Auto-scaling to match demand
- Storage tiering for cost efficiency

For each capacity recommendation provide:
- Resource type and configuration
- Sizing rationale
- Performance characteristics
- Cost implications
- Scaling strategy
- Growth accommodation (months/years)
- Confidence level
- Alternatives and trade-offs

Provide specific numbers, not generic recommendations. Be conservative with headroom (20-30% buffer for growth)."""

    def __init__(self, agent_id: Optional[str] = None):
        """Initialize CapacityPlannerAgent"""
        super().__init__(agent_id)
        self.agent_type = "capacity_planner"
        self.capacity_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute capacity planning
        
        Args:
            task: Task definition containing:
                - project_id: Project identifier
                - current_capacity: Current infrastructure capacity metrics
                - performance_requirements: Target performance requirements
                - growth_projections: Expected growth (optional)
                - target_cloud: Target cloud provider (AWS/Azure/GCP)
                - planning_horizon: Months to plan for (optional, default: 12)
        
        Returns:
            Capacity plan with resource sizing, scaling strategies, and recommendations
        """
        project_id = task.get('project_id')
        if not project_id:
            raise ValueError("project_id is required")
        
        current_capacity = task.get('current_capacity')
        if not current_capacity:
            raise ValueError("current_capacity is required")
        
        performance_requirements = task.get('performance_requirements')
        if not performance_requirements:
            raise ValueError("performance_requirements is required")
        
        target_cloud = task.get('target_cloud', 'AWS')
        
        try:
            # Emit start event
            await self.emit_event(
                event_type='capacity_planning.started',
                detail={
                    'target_cloud': target_cloud
                },
                project_id=project_id
            )
            
            # Perform capacity planning using AI
            capacity_results = await self._plan_capacity(
                project_id, 
                current_capacity,
                performance_requirements,
                target_cloud,
                task
            )
            
            # Enrich results with metadata
            capacity_results['status'] = 'completed'
            capacity_results['agent_id'] = self.agent_id
            capacity_results['project_id'] = project_id
            capacity_results['timestamp'] = datetime.utcnow().isoformat()
            
            # Store results in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='capacity_plan',
                data=capacity_results
            )
            
            result = {
                'status': 'completed',
                'agent_id': self.agent_id,
                'project_id': project_id,
                'target_cloud': target_cloud,
                'resource_sizing': capacity_results.get('resource_sizing', {}),
                'scaling_strategy': capacity_results.get('scaling_strategy', {}),
                'capacity_projections': capacity_results.get('capacity_projections', {}),
                'peak_load_plan': capacity_results.get('peak_load_plan', {}),
                'recommendations': capacity_results.get('recommendations', []),
                's3_uri': s3_uri,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={
                    'last_plan': result,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='capacity_planning.completed',
                detail={},
                project_id=project_id
            )
            
            self.capacity_data = result
            return result
            
        except Exception as e:
            await self.emit_event(
                event_type='capacity_planning.failed',
                detail={
                    'error': str(e)
                },
                project_id=project_id
            )
            raise
    
    async def _plan_capacity(
        self, 
        project_id: str, 
        current_capacity: Dict[str, Any],
        performance_requirements: Dict[str, Any],
        target_cloud: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to plan capacity
        
        Args:
            project_id: Project identifier
            current_capacity: Current capacity metrics
            performance_requirements: Performance targets
            target_cloud: Target cloud provider
            task: Task configuration with optional parameters
        
        Returns:
            Capacity planning results
        """
        planning_horizon = task.get('planning_horizon', 12)
        growth_projections = task.get('growth_projections', {})
        
        prompt = f"""Perform comprehensive capacity planning for cloud migration:

Target Cloud Provider: {target_cloud}
Planning Horizon: {planning_horizon} months

Current Capacity Metrics:
{json.dumps(current_capacity, indent=2)}

Performance Requirements:
{json.dumps(performance_requirements, indent=2)}

Growth Projections:
{json.dumps(growth_projections, indent=2)}

Please provide a detailed capacity plan in JSON format with:

1. resource_sizing: Recommended resource configurations
   - compute: Compute resources (EC2, containers, etc.)
     * instance_types: List of recommended instance types
     * cpu_cores: Total CPU cores needed
     * memory_gb: Total memory in GB
     * instance_count: Number of instances
     * rationale: Why these resources
   - storage: Storage resources
     * type: Storage type (SSD, HDD, object storage)
     * capacity_gb: Total capacity in GB
     * iops: IOPS requirements
     * throughput_mbps: Throughput in MB/s
   - databases: Database resources
     * instance_type: Database instance type
     * storage_gb: Database storage
     * iops: Database IOPS
     * read_replicas: Number of read replicas
   - networking: Network resources
     * bandwidth_gbps: Required bandwidth
     * load_balancers: Load balancer configuration

2. scaling_strategy: Auto-scaling and scaling policies
   - auto_scaling_config: Auto-scaling configuration
     * min_instances: Minimum instance count
     * max_instances: Maximum instance count
     * target_cpu_utilization: Target CPU %
     * scale_up_threshold: When to add instances
     * scale_down_threshold: When to remove instances
     * cooldown_period_seconds: Cooldown period
   - vertical_scaling: When to scale up instance sizes
   - horizontal_scaling: When to scale out with more instances

3. capacity_projections: Capacity needs over time
   - month_3: Capacity at 3 months
   - month_6: Capacity at 6 months
   - month_12: Capacity at 12 months
   - growth_buffer_percent: Safety buffer percentage

4. peak_load_plan: Handling peak loads
   - expected_peak_multiplier: Peak vs. average load
   - burst_capacity: Additional capacity for peaks
   - pre_warming_strategy: Pre-warming recommendations
   - load_testing_recommendations: Load testing guidelines

5. recommendations: Array of capacity planning recommendations
   - For each recommendation:
     * category: Resource category
     * recommendation: Specific recommendation
     * impact: Expected impact
     * priority: Priority level

Be specific with numbers and instance types. Provide realistic estimates with adequate headroom for growth."""

        response = await self.invoke_ai(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3
        )
        
        # Parse AI response
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result = json.loads(response[json_start:json_end])
            else:
                result = {
                    'resource_sizing': {},
                    'scaling_strategy': {},
                    'capacity_projections': {},
                    'peak_load_plan': {},
                    'recommendations': ['AI response could not be parsed as JSON'],
                    'raw_analysis': response
                }
        except json.JSONDecodeError:
            result = {
                'resource_sizing': {},
                'scaling_strategy': {},
                'capacity_projections': {},
                'peak_load_plan': {},
                'recommendations': ['AI response could not be parsed as JSON'],
                'raw_analysis': response
            }
        
        return result
    
    def get_capacity_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent capacity plan data
        
        Returns:
            Capacity plan data or None if not available
        """
        return self.capacity_data
