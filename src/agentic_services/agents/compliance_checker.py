"""
ComplianceCheckerAgent - Validates compliance requirements for cloud migration
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base import BaseAgent, bedrock_client, s3_client, dynamodb_client, eventbridge_client


class ComplianceCheckerAgent(BaseAgent):
    """
    Agent responsible for checking compliance requirements and regulations.
    
    Capabilities:
    - GDPR compliance validation (EU data protection)
    - HIPAA compliance checking (US healthcare data)
    - PCI-DSS assessment (payment card industry)
    - SOC 2 requirements validation
    - ISO 27001 security controls
    - Industry-specific regulations (CCPA, GLBA, etc.)
    - Cloud provider compliance mapping
    - Compliance gap analysis
    - Remediation recommendations
    """
    
    SYSTEM_PROMPT = """You are a compliance and regulatory expert specializing in cloud migration compliance.

Your responsibilities:
1. Assess GDPR compliance requirements and data protection needs
2. Validate HIPAA compliance for healthcare data
3. Check PCI-DSS requirements for payment card data
4. Evaluate SOC 2 controls and requirements
5. Assess ISO 27001 security standards
6. Identify industry-specific regulatory requirements
7. Map cloud provider compliance certifications
8. Perform compliance gap analysis
9. Provide detailed remediation recommendations

Compliance frameworks to assess:

GDPR (General Data Protection Regulation):
- Data processing lawful basis
- Data subject rights (access, erasure, portability)
- Consent management
- Data breach notification (72 hours)
- Data Protection Impact Assessment (DPIA)
- Data residency requirements (EU data stays in EU)
- Privacy by design and default
- Data Protection Officer (DPO) requirements

HIPAA (Health Insurance Portability and Accountability Act):
- Protected Health Information (PHI) safeguards
- Administrative, physical, and technical safeguards
- Access controls and audit logs
- Encryption at rest and in transit
- Business Associate Agreements (BAA)
- Breach notification requirements
- Minimum necessary standard
- HITECH Act requirements

PCI-DSS (Payment Card Industry Data Security Standard):
- Cardholder Data Environment (CDE) protection
- Network segmentation
- Strong access controls
- Regular security testing
- Vulnerability management
- Encryption of cardholder data
- Secure development practices
- Incident response procedures

SOC 2 (Service Organization Control 2):
- Security (must-have)
- Availability
- Processing integrity
- Confidentiality
- Privacy
- Control objectives and activities
- Risk assessment
- Monitoring activities

ISO 27001:
- Information security management system (ISMS)
- Risk assessment methodology
- Security control selection
- Asset management
- Access control
- Cryptography
- Operations security
- Incident management

Industry-specific regulations:
- CCPA (California Consumer Privacy Act)
- GLBA (Gramm-Leach-Bliley Act) - Financial services
- FERPA (Family Educational Rights and Privacy Act) - Education
- FedRAMP (Federal Risk and Authorization Management Program) - US Government
- CMMC (Cybersecurity Maturity Model Certification) - Defense contractors

Cloud compliance considerations:
- AWS compliance programs (HIPAA eligible, PCI-DSS certified, etc.)
- Shared responsibility model
- Regional data residency
- Compliance inheritance from cloud provider
- Additional controls needed beyond cloud provider
- Compliance documentation and evidence collection

For each compliance requirement provide:
- Applicability assessment (required/recommended/not applicable)
- Current compliance status
- Gap analysis with specific findings
- Risk level if non-compliant (critical, high, medium, low)
- Remediation steps with priority
- Estimated effort for remediation
- Cloud provider support available
- Required documentation and evidence

Focus on providing actionable, specific compliance guidance that enables successful cloud migration."""

    def __init__(self, agent_id: Optional[str] = None):
        """Initialize ComplianceCheckerAgent"""
        super().__init__(agent_id)
        self.agent_type = "compliance_checker"
        self.compliance_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute compliance checking
        
        Args:
            task: Task definition containing:
                - project_id: Project identifier
                - data_classification: Data classification results
                - target_cloud: Target cloud provider (AWS/Azure/GCP)
                - industry: Industry sector (healthcare, finance, retail, etc.) (optional)
                - check_gdpr: Whether to check GDPR compliance (optional, default: True)
                - check_hipaa: Whether to check HIPAA compliance (optional, default: False)
                - check_pci_dss: Whether to check PCI-DSS compliance (optional, default: False)
                - check_soc2: Whether to check SOC 2 compliance (optional, default: True)
                - check_iso27001: Whether to check ISO 27001 (optional, default: False)
        
        Returns:
            Compliance assessment with requirements, gaps, and recommendations
        """
        project_id = task.get('project_id')
        if not project_id:
            raise ValueError("project_id is required")
        
        data_classification = task.get('data_classification')
        if not data_classification:
            raise ValueError("data_classification is required")
        
        target_cloud = task.get('target_cloud', 'AWS')
        
        try:
            # Emit start event
            await self.emit_event(
                event_type='compliance_check.started',
                detail={
                    'target_cloud': target_cloud
                },
                project_id=project_id
            )
            
            # Perform compliance checking using AI
            compliance_results = await self._check_compliance(
                project_id, 
                data_classification,
                target_cloud,
                task
            )
            
            # Enrich results with metadata
            compliance_results['status'] = 'completed'
            compliance_results['agent_id'] = self.agent_id
            compliance_results['project_id'] = project_id
            compliance_results['timestamp'] = datetime.utcnow().isoformat()
            
            # Store results in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='compliance_assessment',
                data=compliance_results
            )
            
            result = {
                'status': 'completed',
                'agent_id': self.agent_id,
                'project_id': project_id,
                'target_cloud': target_cloud,
                'compliance_frameworks': compliance_results.get('compliance_frameworks', {}),
                'gaps': compliance_results.get('gaps', []),
                'overall_compliance_score': compliance_results.get('overall_compliance_score', 0),
                'critical_issues': compliance_results.get('critical_issues', []),
                'recommendations': compliance_results.get('recommendations', []),
                'remediation_plan': compliance_results.get('remediation_plan', {}),
                's3_uri': s3_uri,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={
                    'last_check': result,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='compliance_check.completed',
                detail={
                    'overall_score': result.get('overall_compliance_score', 0),
                    'critical_issues_count': len(result.get('critical_issues', []))
                },
                project_id=project_id
            )
            
            self.compliance_data = result
            return result
            
        except Exception as e:
            await self.emit_event(
                event_type='compliance_check.failed',
                detail={
                    'error': str(e)
                },
                project_id=project_id
            )
            raise
    
    async def _check_compliance(
        self, 
        project_id: str, 
        data_classification: Dict[str, Any],
        target_cloud: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to check compliance requirements
        
        Args:
            project_id: Project identifier
            data_classification: Data classification results
            target_cloud: Target cloud provider
            task: Task configuration with optional flags
        
        Returns:
            Compliance assessment results
        """
        # Build compliance check request based on task flags
        frameworks_to_check = []
        if task.get('check_gdpr', True):
            frameworks_to_check.append("GDPR")
        if task.get('check_hipaa', False):
            frameworks_to_check.append("HIPAA")
        if task.get('check_pci_dss', False):
            frameworks_to_check.append("PCI-DSS")
        if task.get('check_soc2', True):
            frameworks_to_check.append("SOC 2")
        if task.get('check_iso27001', False):
            frameworks_to_check.append("ISO 27001")
        
        industry = task.get('industry', 'general')
        
        prompt = f"""Perform a comprehensive compliance assessment for cloud migration:

Target Cloud Provider: {target_cloud}
Industry Sector: {industry}
Frameworks to Check: {', '.join(frameworks_to_check)}

Data Classification Results:
{json.dumps(data_classification, indent=2)}

Please provide a detailed compliance assessment in JSON format with:
1. compliance_frameworks: Object with each framework's assessment
   - For each framework include:
     * applicable: boolean
     * current_status: compliant/partial/non_compliant
     * compliance_score: 0-100
     * required_controls: list of required controls
     * implemented_controls: list of already implemented controls
     * missing_controls: list of missing controls
     * cloud_provider_support: what the cloud provider offers

2. gaps: Array of compliance gaps found
   - For each gap:
     * framework: which compliance framework
     * requirement: specific requirement not met
     * severity: critical/high/medium/low
     * description: detailed gap description
     * impact: business impact if not addressed
     * affected_systems: which systems are affected

3. overall_compliance_score: Overall compliance score (0-100)

4. critical_issues: Array of critical compliance issues requiring immediate attention

5. recommendations: Array of actionable recommendations
   - For each recommendation:
     * priority: critical/high/medium/low
     * framework: related compliance framework
     * action: specific action to take
     * effort: estimated effort (hours/days/weeks)
     * dependencies: any dependencies on other actions

6. remediation_plan: Structured plan to achieve compliance
   - phases: array of remediation phases
   - timeline: estimated timeline for full compliance
   - total_effort: total effort estimate
   - quick_wins: easy fixes that can be done quickly

Be specific and actionable in all recommendations. Consider the target cloud provider's compliance certifications and shared responsibility model."""

        response = await self.invoke_ai(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.2  # Low temperature for compliance accuracy
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
                    'compliance_frameworks': {},
                    'gaps': [],
                    'overall_compliance_score': 0,
                    'critical_issues': [],
                    'recommendations': ['AI response could not be parsed as JSON'],
                    'remediation_plan': {},
                    'raw_analysis': response
                }
        except json.JSONDecodeError:
            result = {
                'compliance_frameworks': {},
                'gaps': [],
                'overall_compliance_score': 0,
                'critical_issues': [],
                'recommendations': ['AI response could not be parsed as JSON'],
                'remediation_plan': {},
                'raw_analysis': response
            }
        
        return result
    
    def get_compliance_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent compliance check data
        
        Returns:
            Compliance assessment data or None if not available
        """
        return self.compliance_data
