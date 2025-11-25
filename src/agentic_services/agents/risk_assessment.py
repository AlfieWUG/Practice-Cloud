"""
RiskAssessmentAgent - Assesses risks for cloud migration
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseAgent, bedrock_client, s3_client, dynamodb_client, eventbridge_client


class RiskAssessmentAgent(BaseAgent):
    """
    Agent responsible for assessing migration risks and mitigation strategies.
    
    Capabilities:
    - Technical risk identification
    - Business risk assessment
    - Security risk analysis
    - Compliance risk evaluation
    - Impact analysis (high/medium/low)
    - Probability assessment
    - Risk scoring and prioritization
    - Mitigation strategy recommendations
    - Risk monitoring plan
    """
    
    SYSTEM_PROMPT = """You are a risk management expert specializing in cloud migration risk assessment.

Your responsibilities:
1. Identify technical risks (compatibility, performance, integration)
2. Assess business risks (downtime, cost overruns, resource constraints)
3. Analyze security risks (data breaches, access control, vulnerabilities)
4. Evaluate compliance risks (regulatory violations, data residency)
5. Assess impact levels (critical, high, medium, low)
6. Estimate probability (very likely, likely, possible, unlikely)
7. Calculate risk scores (impact × probability)
8. Recommend mitigation strategies
9. Develop risk monitoring and contingency plans

Risk Categories:

Technical Risks:
- Application compatibility issues
- Performance degradation
- Data migration failures or corruption
- Integration breakage with existing systems
- Vendor lock-in concerns
- Technical debt and legacy code
- Insufficient testing coverage
- Rollback complexity

Business Risks:
- Extended downtime during migration
- Cost overruns beyond budget
- Resource availability constraints
- Schedule delays and missed deadlines
- Loss of business continuity
- Customer impact and dissatisfaction
- Competitive disadvantage during transition
- Organizational resistance to change

Security Risks:
- Data breaches during migration
- Insufficient access controls
- Exposed credentials or secrets
- Unencrypted data transmission
- Misconfigured cloud resources
- Inadequate monitoring and alerting
- Insider threats
- Third-party vulnerabilities

Compliance Risks:
- Regulatory violations (GDPR, HIPAA, PCI-DSS)
- Data residency requirement breaches
- Audit trail gaps
- Inadequate data retention policies
- Missing compliance documentation
- Certification lapses
- Privacy policy violations

Operational Risks:
- Insufficient cloud expertise
- Inadequate documentation
- Knowledge transfer gaps
- Support model changes
- Monitoring blind spots
- Backup and recovery gaps
- Disaster recovery inadequacy

For each risk provide:
- Risk ID and name
- Category (technical/business/security/compliance/operational)
- Description of the risk
- Impact level (critical/high/medium/low)
- Probability (very_likely/likely/possible/unlikely)
- Risk score (calculated: impact × probability)
- Affected systems/components
- Potential consequences
- Current controls (if any)
- Mitigation strategies (preventive and detective)
- Mitigation priority
- Estimated cost to mitigate
- Residual risk after mitigation
- Owner/responsible party
- Timeline for mitigation

Risk Scoring Matrix:
- Critical Impact + Very Likely = Risk Score: 100 (Immediate action required)
- Critical Impact + Likely = Risk Score: 80
- High Impact + Very Likely = Risk Score: 75
- Critical Impact + Possible = Risk Score: 60
- High Impact + Likely = Risk Score: 60
- Medium Impact + Very Likely = Risk Score: 50
- And so on...

Mitigation Strategy Types:
- Avoid: Eliminate the risk entirely (change approach)
- Reduce: Implement controls to lower probability or impact
- Transfer: Shift risk to third party (insurance, cloud provider SLAs)
- Accept: Acknowledge and monitor (for low-priority risks)

Be comprehensive, specific, and prioritize risks by severity."""

    def __init__(self, agent_id: Optional[str] = None):
        """Initialize RiskAssessmentAgent"""
        super().__init__(agent_id)
        self.agent_type = "risk_assessment"
        self.risk_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute risk assessment
        
        Args:
            task: Task definition containing:
                - project_id: Project identifier
                - migration_plan: Migration plan details
                - infrastructure: Infrastructure details
                - assess_technical_risk: Whether to assess technical risks (optional, default: True)
                - assess_business_risk: Whether to assess business risks (optional, default: True)
                - assess_security_risk: Whether to assess security risks (optional, default: True)
                - assess_compliance_risk: Whether to assess compliance risks (optional, default: True)
        
        Returns:
            Risk assessment with identified risks, scores, and mitigation strategies
        """
        project_id = task.get('project_id')
        if not project_id:
            raise ValueError("project_id is required")
        
        migration_plan = task.get('migration_plan')
        if not migration_plan:
            raise ValueError("migration_plan is required")
        
        try:
            # Emit start event
            await self.emit_event(
                event_type='risk_assessment.started',
                detail={},
                project_id=project_id
            )
            
            # Perform risk assessment using AI
            risk_results = await self._assess_risks(
                project_id, 
                migration_plan,
                task
            )
            
            # Enrich results with metadata
            risk_results['status'] = 'completed'
            risk_results['agent_id'] = self.agent_id
            risk_results['project_id'] = project_id
            risk_results['timestamp'] = datetime.utcnow().isoformat()
            
            # Store results in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='risk_assessment',
                data=risk_results
            )
            
            result = {
                'status': 'completed',
                'agent_id': self.agent_id,
                'project_id': project_id,
                'risks': risk_results.get('risks', []),
                'risk_summary': risk_results.get('risk_summary', {}),
                'critical_risks': risk_results.get('critical_risks', []),
                'mitigation_plan': risk_results.get('mitigation_plan', {}),
                'monitoring_plan': risk_results.get('monitoring_plan', {}),
                'recommendations': risk_results.get('recommendations', []),
                's3_uri': s3_uri,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={
                    'last_assessment': result,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='risk_assessment.completed',
                detail={
                    'total_risks': len(result.get('risks', [])),
                    'critical_risks': len(result.get('critical_risks', []))
                },
                project_id=project_id
            )
            
            self.risk_data = result
            return result
            
        except Exception as e:
            await self.emit_event(
                event_type='risk_assessment.failed',
                detail={
                    'error': str(e)
                },
                project_id=project_id
            )
            raise
    
    async def _assess_risks(
        self, 
        project_id: str, 
        migration_plan: Dict[str, Any],
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to assess risks
        
        Args:
            project_id: Project identifier
            migration_plan: Migration plan details
            task: Task configuration with optional flags
        
        Returns:
            Risk assessment results
        """
        infrastructure = task.get('infrastructure', {})
        
        prompt = f"""Perform a comprehensive risk assessment for cloud migration:

Migration Plan:
{json.dumps(migration_plan, indent=2)}

Infrastructure Context:
{json.dumps(infrastructure, indent=2)}

Please provide a detailed risk assessment in JSON format with:

1. risks: Array of identified risks
   - For each risk:
     * risk_id: Unique identifier
     * name: Risk name
     * category: technical/business/security/compliance/operational
     * description: Detailed description
     * impact: critical/high/medium/low
     * probability: very_likely/likely/possible/unlikely
     * risk_score: Calculated score (1-100)
     * affected_systems: List of affected components
     * consequences: Potential consequences
     * current_controls: Existing mitigation controls
     * mitigation_strategies: Recommended mitigation actions
     * mitigation_priority: Priority level
     * estimated_mitigation_cost: Cost to implement mitigation
     * residual_risk: Risk level after mitigation

2. risk_summary: Summary statistics
   - total_risks: Total number of risks identified
   - by_category: Count by category
     * technical: count
     * business: count
     * security: count
     * compliance: count
     * operational: count
   - by_impact: Count by impact level
     * critical: count
     * high: count
     * medium: count
     * low: count
   - overall_risk_level: Overall project risk level

3. critical_risks: Array of critical/high priority risks requiring immediate attention

4. mitigation_plan: Structured mitigation plan
   - phases: Array of mitigation phases
   - timeline: Timeline for implementing mitigations
   - total_cost: Total cost to mitigate all risks
   - quick_wins: Easy mitigations to implement immediately

5. monitoring_plan: Risk monitoring strategy
   - key_risk_indicators: Metrics to monitor
   - monitoring_frequency: How often to review
   - escalation_procedures: When and how to escalate

6. recommendations: Array of risk management recommendations

Be thorough and prioritize risks by severity. Provide specific, actionable mitigation strategies."""

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
                    'risks': [],
                    'risk_summary': {},
                    'critical_risks': [],
                    'mitigation_plan': {},
                    'monitoring_plan': {},
                    'recommendations': ['AI response could not be parsed as JSON'],
                    'raw_analysis': response
                }
        except json.JSONDecodeError:
            result = {
                'risks': [],
                'risk_summary': {},
                'critical_risks': [],
                'mitigation_plan': {},
                'monitoring_plan': {},
                'recommendations': ['AI response could not be parsed as JSON'],
                'raw_analysis': response
            }
        
        return result
    
    def get_risk_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent risk assessment data
        
        Returns:
            Risk assessment data or None if not available
        """
        return self.risk_data
