"""
InfrastructureProvisionerAgent - Provisions cloud infrastructure
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseAgent, bedrock_client, s3_client, dynamodb_client, eventbridge_client


class InfrastructureProvisionerAgent(BaseAgent):
    """
    Agent responsible for provisioning cloud infrastructure.
    
    Capabilities:
    - VPC and network infrastructure provisioning
    - Compute resource provisioning (EC2, containers, serverless)
    - Storage provisioning (EBS, S3, EFS)
    - Database provisioning (RDS, DynamoDB, etc.)
    - Load balancer and networking setup
    - Infrastructure as Code (IaC) generation
    - Resource tagging and organization
    - Multi-region deployment support
    """
    
    SYSTEM_PROMPT = """You are a cloud infrastructure expert specializing in automated infrastructure provisioning.

Your responsibilities:
1. Generate Infrastructure as Code (Terraform, CloudFormation)
2. Provision VPCs, subnets, and network infrastructure
3. Set up compute resources (EC2, ECS, EKS, Lambda)
4. Provision storage (S3, EBS, EFS, FSx)
5. Deploy databases (RDS, DynamoDB, Aurora, etc.)
6. Configure load balancers and networking
7. Implement resource tagging strategies
8. Support multi-region deployments

Infrastructure Components:

Networking:
- VPC with CIDR blocks (10.0.0.0/16 typical)
- Public subnets (web tier, load balancers)
- Private subnets (application tier, databases)
- NAT gateways for outbound internet access
- Internet gateway for inbound traffic
- Route tables and routing
- Network ACLs and security groups
- VPN connections if needed
- VPC peering for multi-VPC architectures

Compute:
- EC2 instances with appropriate instance types
- Auto Scaling groups for scalability
- Launch templates or configurations
- ECS/EKS clusters for containers
- Lambda functions for serverless
- Elastic Load Balancers (ALB, NLB)
- Target groups and health checks

Storage:
- S3 buckets with appropriate storage classes
- EBS volumes for block storage
- EFS for shared file systems
- FSx for Windows/Lustre workloads
- Lifecycle policies and versioning
- Encryption at rest (KMS keys)
- Backup and snapshot configurations

Databases:
- RDS instances (PostgreSQL, MySQL, etc.)
- Multi-AZ deployment for high availability
- Read replicas for read scalability
- DynamoDB tables with capacity modes
- Aurora clusters for performance
- Backup retention and maintenance windows
- Encryption and security configurations

Load Balancing:
- Application Load Balancers (ALB) for HTTP/HTTPS
- Network Load Balancers (NLB) for TCP/UDP
- Target groups and routing rules
- SSL/TLS certificates (ACM)
- Health checks and monitoring
- Cross-zone load balancing

Infrastructure as Code Best Practices:
- Use Terraform or CloudFormation
- Modular, reusable components
- Environment-specific configurations (dev, staging, prod)
- State management (remote state in S3)
- Version control for IaC
- Automated provisioning via CI/CD
- Idempotent operations
- Change sets for safe updates

Resource Tagging Strategy:
- Environment (dev, staging, prod)
- Project/Application name
- Owner/Team
- Cost center for billing
- Compliance requirements
- Backup schedules
- Auto-shutdown schedules for non-prod

Security Considerations:
- Principle of least privilege
- Security groups with minimal ingress
- Private subnets for sensitive workloads
- Encryption in transit and at rest
- VPC Flow Logs for network monitoring
- CloudTrail for API auditing
- IAM roles for resource access
- Secrets Manager for credentials

Multi-Region Deployment:
- Primary and secondary regions
- Data replication strategies
- Route 53 for DNS failover
- Cross-region VPC peering
- Global accelerator for performance
- Disaster recovery planning

For each infrastructure component provide:
- Resource type and configuration
- IaC code snippet (Terraform or CloudFormation)
- Dependencies and ordering
- Estimated provisioning time
- Cost implications
- Security configurations
- Monitoring and logging setup

Generate production-ready, secure, and scalable infrastructure configurations."""

    def __init__(self, agent_id: Optional[str] = None):
        """Initialize InfrastructureProvisionerAgent"""
        super().__init__(agent_id)
        self.agent_type = "infrastructure_provisioner"
        self.provisioning_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute infrastructure provisioning
        
        Args:
            task: Task definition containing:
                - project_id: Project identifier
                - infrastructure_plan: Infrastructure requirements and design
                - target_cloud: Target cloud provider (AWS/Azure/GCP)
                - environment: Environment type (dev/staging/prod)
                - iac_format: IaC format (terraform/cloudformation) (optional, default: terraform)
                - multi_region: Whether to deploy in multiple regions (optional, default: False)
        
        Returns:
            Provisioning plan with IaC code, resource definitions, and execution steps
        """
        project_id = task.get('project_id')
        if not project_id:
            raise ValueError("project_id is required")
        
        infrastructure_plan = task.get('infrastructure_plan')
        if not infrastructure_plan:
            raise ValueError("infrastructure_plan is required")
        
        target_cloud = task.get('target_cloud', 'AWS')
        environment = task.get('environment', 'prod')
        
        try:
            # Emit start event
            await self.emit_event(
                event_type='infrastructure_provisioning.started',
                detail={
                    'target_cloud': target_cloud,
                    'environment': environment
                },
                project_id=project_id
            )
            
            # Generate provisioning plan using AI
            provisioning_results = await self._generate_provisioning_plan(
                project_id,
                infrastructure_plan,
                target_cloud,
                environment,
                task
            )
            
            # Enrich results with metadata
            provisioning_results['status'] = 'completed'
            provisioning_results['agent_id'] = self.agent_id
            provisioning_results['project_id'] = project_id
            provisioning_results['timestamp'] = datetime.utcnow().isoformat()
            
            # Store results in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='infrastructure_provisioning',
                data=provisioning_results
            )
            
            result = {
                'status': 'completed',
                'agent_id': self.agent_id,
                'project_id': project_id,
                'target_cloud': target_cloud,
                'environment': environment,
                'iac_code': provisioning_results.get('iac_code', {}),
                'resource_definitions': provisioning_results.get('resource_definitions', []),
                'provisioning_steps': provisioning_results.get('provisioning_steps', []),
                'estimated_time': provisioning_results.get('estimated_time', ''),
                'recommendations': provisioning_results.get('recommendations', []),
                's3_uri': s3_uri,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={
                    'last_provisioning': result,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='infrastructure_provisioning.completed',
                detail={
                    'resource_count': len(result.get('resource_definitions', []))
                },
                project_id=project_id
            )
            
            self.provisioning_data = result
            return result
            
        except Exception as e:
            await self.emit_event(
                event_type='infrastructure_provisioning.failed',
                detail={
                    'error': str(e)
                },
                project_id=project_id
            )
            raise
    
    async def _generate_provisioning_plan(
        self,
        project_id: str,
        infrastructure_plan: Dict[str, Any],
        target_cloud: str,
        environment: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to generate infrastructure provisioning plan
        
        Args:
            project_id: Project identifier
            infrastructure_plan: Infrastructure requirements
            target_cloud: Target cloud provider
            environment: Environment type
            task: Task configuration
        
        Returns:
            Infrastructure provisioning plan
        """
        iac_format = task.get('iac_format', 'terraform')
        multi_region = task.get('multi_region', False)
        
        prompt = f"""Generate a comprehensive infrastructure provisioning plan:

Target Cloud: {target_cloud}
Environment: {environment}
IaC Format: {iac_format}
Multi-Region: {multi_region}

Infrastructure Requirements:
{json.dumps(infrastructure_plan, indent=2)}

Please provide a detailed provisioning plan in JSON format with:

1. iac_code: Infrastructure as Code snippets
   - networking: VPC, subnets, routing code
   - compute: EC2, containers, serverless code
   - storage: S3, EBS, EFS code
   - databases: RDS, DynamoDB code
   - load_balancing: ALB, NLB code

2. resource_definitions: Array of resources to provision
   - For each resource:
     * resource_type: Type of resource
     * resource_name: Unique name
     * configuration: Configuration details
     * dependencies: Dependencies on other resources
     * tags: Resource tags

3. provisioning_steps: Ordered steps to provision infrastructure
   - For each step:
     * step_number: Sequential number
     * description: What to provision
     * resources: Resources in this step
     * estimated_duration: Time estimate
     * validation: How to verify success

4. estimated_time: Total estimated provisioning time

5. recommendations: Best practices and recommendations

Generate production-ready, secure IaC code."""

        response = await self.invoke_ai(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.2
        )
        
        # Parse AI response
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result = json.loads(response[json_start:json_end])
            else:
                result = {
                    'iac_code': {},
                    'resource_definitions': [],
                    'provisioning_steps': [],
                    'estimated_time': 'unknown',
                    'recommendations': ['AI response could not be parsed as JSON'],
                    'raw_analysis': response
                }
        except json.JSONDecodeError:
            result = {
                'iac_code': {},
                'resource_definitions': [],
                'provisioning_steps': [],
                'estimated_time': 'unknown',
                'recommendations': ['AI response could not be parsed as JSON'],
                'raw_analysis': response
            }
        
        return result
    
    def get_provisioning_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent provisioning plan data
        
        Returns:
            Provisioning plan data or None if not available
        """
        return self.provisioning_data
