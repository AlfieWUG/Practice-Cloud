"""
CostEstimatorAgent - Estimates migration and operational costs for cloud migration
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseAgent, bedrock_client, s3_client, dynamodb_client, eventbridge_client


class CostEstimatorAgent(BaseAgent):
    """
    Agent responsible for estimating cloud migration and operational costs.
    
    Capabilities:
    - Migration cost estimation (one-time costs)
    - Operational cost projection (ongoing costs)
    - TCO (Total Cost of Ownership) analysis
    - Cost optimization recommendations
    - ROI calculation
    - Cost comparison (current vs. cloud)
    - Reserved instance vs. on-demand analysis
    - Cost allocation and tagging strategy
    """
    
    SYSTEM_PROMPT = """You are a cloud cost optimization expert specializing in TCO analysis and cost estimation.

Your responsibilities:
1. Estimate one-time migration costs
2. Project ongoing operational costs
3. Calculate Total Cost of Ownership (TCO)
4. Provide cost optimization recommendations
5. Calculate ROI and break-even point
6. Compare current infrastructure costs vs. cloud costs
7. Analyze pricing models (on-demand, reserved, spot/preemptible)
8. Recommend cost allocation and tagging strategies

Migration Costs (One-Time):
- Planning and assessment: Staff time, consultants
- Application refactoring: Development effort
- Data migration: Transfer costs, tools, downtime costs
- Testing and validation: QA resources
- Training: Staff training on cloud technologies
- Migration tools and services: Third-party tools, cloud migration services
- Contingency buffer: 15-20% for unexpected costs

Operational Costs (Ongoing):
- Compute: VMs, containers, serverless
- Storage: Block, object, archive storage
- Networking: Data transfer, load balancers, VPNs
- Databases: Managed databases, backup storage
- Monitoring and logging: Observability tools
- Security: WAF, DDoS protection, secrets management
- Support: Cloud provider support plans
- Staff: Cloud operations and management

AWS Cost Components:
- EC2: Instance types, pricing models (on-demand, reserved, spot)
- RDS: Database instance costs, storage, backups
- S3: Storage classes, data transfer
- Lambda: Invocations, duration
- ECS/EKS: Container orchestration costs
- CloudFront: CDN data transfer
- Route 53: DNS queries
- VPC: NAT gateways, VPN connections
- CloudWatch: Metrics, logs, alarms
- Support: Developer, Business, Enterprise plans

Cost Optimization Strategies:
- Right-sizing: Match instance sizes to actual usage
- Reserved Instances: 1-year or 3-year commitments (40-60% savings)
- Spot Instances: Up to 90% savings for fault-tolerant workloads
- Savings Plans: Flexible pricing model
- Auto-scaling: Scale resources based on demand
- Storage tiering: Move infrequent data to cheaper storage classes
- Data transfer optimization: Minimize cross-region/inter-AZ transfers
- Unused resource cleanup: Eliminate idle resources
- Schedule-based scaling: Turn off non-prod resources during off-hours

TCO Analysis Components:
- Current infrastructure costs (baseline)
- Cloud migration costs
- Year 1-3 operational costs
- Cost savings from eliminated on-prem costs (hardware refresh, datacenter, staff)
- Productivity gains and business value
- Break-even analysis

Pricing Model Recommendations:
- Production workloads: Reserved Instances or Savings Plans
- Development/test: On-demand with scheduled shutdown
- Batch processing: Spot Instances
- Variable workloads: Auto-scaling with on-demand
- Predictable workloads: Reserved capacity

For each cost estimate provide:
- Component breakdown with individual costs
- Confidence level (high/medium/low)
- Assumptions made
- Cost range (best case, expected, worst case)
- Comparison to current costs
- Optimization opportunities
- Potential savings
- ROI timeline

Be specific with numbers and provide realistic estimates based on industry standards."""

    def __init__(self, agent_id: Optional[str] = None):
        """Initialize CostEstimatorAgent"""
        super().__init__(agent_id)
        self.agent_type = "cost_estimator"
        self.cost_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute cost estimation
        
        Args:
            task: Task definition containing:
                - project_id: Project identifier
                - infrastructure: Current infrastructure details
                - target_cloud: Target cloud provider (AWS/Azure/GCP)
                - workload_profile: Workload characteristics (optional)
                - estimate_migration_cost: Whether to estimate migration cost (optional, default: True)
                - estimate_operational_cost: Whether to estimate operational cost (optional, default: True)
                - calculate_tco: Whether to calculate TCO (optional, default: True)
                - calculate_roi: Whether to calculate ROI (optional, default: True)
                - projection_years: Years to project costs (optional, default: 3)
        
        Returns:
            Cost estimates including migration cost, operational cost, TCO, and recommendations
        """
        project_id = task.get('project_id')
        if not project_id:
            raise ValueError("project_id is required")
        
        infrastructure = task.get('infrastructure')
        if not infrastructure:
            raise ValueError("infrastructure is required")
        
        target_cloud = task.get('target_cloud', 'AWS')
        
        try:
            # Emit start event
            await self.emit_event(
                event_type='cost_estimation.started',
                detail={
                    'target_cloud': target_cloud
                },
                project_id=project_id
            )
            
            # Perform cost estimation using AI
            cost_results = await self._estimate_costs(
                project_id, 
                infrastructure,
                target_cloud,
                task
            )
            
            # Enrich results with metadata
            cost_results['status'] = 'completed'
            cost_results['agent_id'] = self.agent_id
            cost_results['project_id'] = project_id
            cost_results['timestamp'] = datetime.utcnow().isoformat()
            
            # Store results in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='cost_estimate',
                data=cost_results
            )
            
            result = {
                'status': 'completed',
                'agent_id': self.agent_id,
                'project_id': project_id,
                'target_cloud': target_cloud,
                'migration_cost': cost_results.get('migration_cost', {}),
                'operational_cost': cost_results.get('operational_cost', {}),
                'tco': cost_results.get('tco', {}),
                'roi': cost_results.get('roi', {}),
                'cost_comparison': cost_results.get('cost_comparison', {}),
                'optimization_opportunities': cost_results.get('optimization_opportunities', []),
                'recommendations': cost_results.get('recommendations', []),
                's3_uri': s3_uri,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={
                    'last_estimate': result,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='cost_estimation.completed',
                detail={
                    'estimated_migration_cost': result['migration_cost'].get('total', 0),
                    'estimated_monthly_operational_cost': result['operational_cost'].get('monthly_total', 0)
                },
                project_id=project_id
            )
            
            self.cost_data = result
            return result
            
        except Exception as e:
            await self.emit_event(
                event_type='cost_estimation.failed',
                detail={
                    'error': str(e)
                },
                project_id=project_id
            )
            raise
    
    async def _estimate_costs(
        self, 
        project_id: str, 
        infrastructure: Dict[str, Any],
        target_cloud: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to estimate costs
        
        Args:
            project_id: Project identifier
            infrastructure: Current infrastructure details
            target_cloud: Target cloud provider
            task: Task configuration with optional flags
        
        Returns:
            Cost estimation results
        """
        projection_years = task.get('projection_years', 3)
        
        prompt = f"""Perform a comprehensive cost estimation for cloud migration:

Target Cloud Provider: {target_cloud}
Projection Period: {projection_years} years

Current Infrastructure:
{json.dumps(infrastructure, indent=2)}

Please provide a detailed cost estimate in JSON format with:

1. migration_cost: One-time migration costs
   - planning: Assessment and planning costs
   - refactoring: Application refactoring costs
   - data_migration: Data transfer and migration tools
   - testing: QA and validation costs
   - training: Staff training costs
   - tools: Migration tools and services
   - contingency: Buffer for unexpected costs (15-20%)
   - total: Total migration cost

2. operational_cost: Ongoing monthly/annual costs
   - compute: EC2/compute instances
   - storage: S3, EBS, and other storage
   - networking: Data transfer, load balancers
   - databases: RDS and managed databases
   - monitoring: CloudWatch, logging
   - security: WAF, security services
   - support: Cloud support plans
   - other: Additional services
   - monthly_total: Total monthly cost
   - annual_total: Total annual cost
   - year_projections: Array of costs for each year

3. tco: Total Cost of Ownership analysis
   - year1_total: First year total (migration + operational)
   - year2_total: Second year total
   - year3_total: Third year total
   - three_year_total: Sum of all three years

4. roi: Return on Investment analysis
   - current_annual_cost: Current infrastructure annual cost
   - cloud_annual_cost: Projected cloud annual cost
   - annual_savings: Cost savings per year
   - break_even_months: Months to recover migration cost
   - three_year_savings: Total savings over 3 years

5. cost_comparison: Current vs. Cloud costs
   - current_monthly: Current monthly infrastructure cost
   - cloud_monthly: Projected cloud monthly cost
   - difference: Monthly cost difference
   - percentage_change: Percentage increase/decrease

6. optimization_opportunities: Array of cost optimization recommendations
   - For each opportunity:
     * category: Cost category (compute, storage, etc.)
     * opportunity: Description of optimization
     * potential_savings: Estimated savings (monthly)
     * effort: Implementation effort (low/medium/high)
     * priority: Priority level

7. recommendations: Array of cost management recommendations

Provide realistic estimates with clear assumptions. Include ranges where appropriate (best case, expected, worst case)."""

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
                    'migration_cost': {'total': 0},
                    'operational_cost': {'monthly_total': 0},
                    'tco': {},
                    'roi': {},
                    'cost_comparison': {},
                    'optimization_opportunities': [],
                    'recommendations': ['AI response could not be parsed as JSON'],
                    'raw_analysis': response
                }
        except json.JSONDecodeError:
            result = {
                'migration_cost': {'total': 0},
                'operational_cost': {'monthly_total': 0},
                'tco': {},
                'roi': {},
                'cost_comparison': {},
                'optimization_opportunities': [],
                'recommendations': ['AI response could not be parsed as JSON'],
                'raw_analysis': response
            }
        
        return result
    
    def get_cost_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent cost estimate data
        
        Returns:
            Cost estimate data or None if not available
        """
        return self.cost_data
