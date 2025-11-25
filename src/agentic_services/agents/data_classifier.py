"""
DataClassifierAgent - Classifies data and identifies compliance requirements
"""

import json
import re
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseAgent, bedrock_client, s3_client, dynamodb_client, eventbridge_client


class DataClassifierAgent(BaseAgent):
    """
    Agent responsible for classifying data and identifying compliance requirements.
    
    Capabilities:
    - Data classification (public, internal, confidential, highly confidential)
    - PII detection (email, phone, SSN, credit cards, etc.)
    - Compliance mapping (GDPR, HIPAA, PCI-DSS, SOC 2)
    - Data sensitivity scoring
    - Data residency requirement identification
    - Encryption requirement analysis
    """
    
    SYSTEM_PROMPT = """You are a data classification expert specializing in cloud migration compliance.

Your responsibilities:
1. Classify data sources by sensitivity level (public, internal, confidential, highly confidential)
2. Detect PII (Personally Identifiable Information) types and volumes
3. Map applicable compliance requirements (GDPR, HIPAA, PCI-DSS, SOC 2, etc.)
4. Identify data residency requirements
5. Recommend encryption standards
6. Score data sensitivity for risk assessment

For data classification:
- PUBLIC: Non-sensitive information that can be freely shared
- INTERNAL: Information for internal use only
- CONFIDENTIAL: Sensitive business information requiring protection
- HIGHLY CONFIDENTIAL: Critical data including PII, financial data, health records

PII Types to detect:
- Email addresses
- Phone numbers
- Social Security Numbers (SSN)
- Credit card numbers
- Passport numbers
- Driver's license numbers
- Date of birth
- Medical record numbers
- Biometric data
- IP addresses

Compliance frameworks to consider:
- GDPR: EU data protection regulation
- HIPAA: US healthcare data protection
- PCI-DSS: Payment card industry standards
- SOC 2: Service organization controls
- CCPA: California Consumer Privacy Act
- State-specific privacy laws

Data residency considerations:
- EU data must stay in EU (GDPR)
- Healthcare data location requirements (HIPAA)
- Financial data requirements
- Government data restrictions

Provide detailed, actionable classification with specific recommendations for each data source."""

    def __init__(self, agent_id: Optional[str] = None):
        """Initialize DataClassifierAgent"""
        super().__init__(agent_id)
        self.agent_type = "data_classifier"
        self.classification_data: Optional[Dict[str, Any]] = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data classification
        
        Args:
            task: Task definition containing:
                - project_id: Project identifier
                - data_sources: List of data sources to classify
                - detect_pii: Whether to perform PII detection (optional)
                - map_compliance: Whether to map compliance requirements (optional)
                - score_sensitivity: Whether to score data sensitivity (optional)
                - identify_residency_requirements: Whether to identify residency needs (optional)
                - recommend_encryption: Whether to recommend encryption (optional)
        
        Returns:
            Classification results with data sources, PII summary, compliance requirements
        """
        project_id = task.get('project_id')
        if not project_id:
            raise ValueError("project_id is required")
        
        data_sources = task.get('data_sources')
        if not data_sources:
            raise ValueError("data_sources is required")
        
        try:
            # Emit start event
            await self.emit_event(
                event_type='classification.started',
                detail={
                    'data_source_count': len(data_sources)
                },
                project_id=project_id
            )
            
            # Perform classification using AI
            classification_results = await self._classify_data(
                project_id, 
                data_sources,
                task
            )
            
            # Enrich results with metadata
            classification_results['status'] = 'completed'
            classification_results['agent_id'] = self.agent_id
            classification_results['project_id'] = project_id
            classification_results['timestamp'] = datetime.utcnow().isoformat()
            
            # Store results in S3
            s3_uri = await self.store_data(
                project_id=project_id,
                data_type='data_classification',
                data=classification_results
            )
            
            result = {
                'status': 'completed',
                'agent_id': self.agent_id,
                'project_id': project_id,
                'data_sources': classification_results.get('data_sources', []),
                'pii_summary': classification_results.get('pii_summary', {}),
                'compliance_requirements': classification_results.get('compliance_requirements', {}),
                'data_residency': classification_results.get('data_residency', {}),
                'overall_sensitivity': classification_results.get('overall_sensitivity', {}),
                'total_data_sources': classification_results.get('total_data_sources', len(data_sources)),
                's3_uri': s3_uri,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save state
            await self.save_state(
                project_id=project_id,
                state={
                    'last_classification': result,
                    'data_source_count': len(data_sources),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Emit completion event
            await self.emit_event(
                event_type='classification.completed',
                detail={
                    'data_source_count': len(data_sources),
                    'pii_detected': len(result.get('pii_summary', {})) > 0
                },
                project_id=project_id
            )
            
            self.classification_data = result
            return result
            
        except Exception as e:
            await self.emit_event(
                event_type='classification.failed',
                detail={
                    'error': str(e)
                },
                project_id=project_id
            )
            raise
    
    async def _classify_data(
        self, 
        project_id: str, 
        data_sources: list,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to classify data sources
        
        Args:
            project_id: Project identifier
            data_sources: List of data sources to classify
            task: Task configuration with optional flags
        
        Returns:
            Classification results
        """
        # Build analysis request based on task flags
        analysis_types = []
        if task.get('detect_pii', True):
            analysis_types.append("PII detection")
        if task.get('map_compliance', True):
            analysis_types.append("compliance mapping")
        if task.get('score_sensitivity', True):
            analysis_types.append("sensitivity scoring")
        if task.get('identify_residency_requirements', True):
            analysis_types.append("data residency requirements")
        if task.get('recommend_encryption', True):
            analysis_types.append("encryption recommendations")
        
        prompt = f"""Classify the following data sources for project {project_id}.

Data Sources: {json.dumps(data_sources, indent=2)}

Analysis Types: {', '.join(analysis_types)}

Provide comprehensive classification including:
1. Data classification level for each source
2. PII types detected with counts and sensitivity levels
3. Applicable compliance requirements (GDPR, HIPAA, PCI-DSS, etc.)
4. Data residency requirements
5. Sensitivity scores (0-100) and risk levels
6. Encryption recommendations

Return a JSON object with the following structure:
{{
    "data_sources": [
        {{
            "name": "source_name",
            "type": "database|file_storage|api|etc",
            "classification": "public|internal|confidential|highly_confidential",
            "contains_pii": true|false,
            "pii_types_found": [
                {{"type": "email_address", "count": 1000, "sensitivity": "high"}},
                {{"type": "ssn", "count": 500, "sensitivity": "critical"}}
            ],
            "sensitivity_score": 85,
            "sensitivity_level": "critical|high|medium|low",
            "encryption_required": true|false,
            "encryption_recommendations": {{
                "at_rest": "AES-256",
                "in_transit": "TLS 1.3",
                "key_management": "AWS KMS"
            }}
        }}
    ],
    "pii_summary": {{
        "total_pii_types": 5,
        "total_pii_records": 10000,
        "critical_pii_types": 2,
        "total_pii_fields": 10
    }},
    "compliance_requirements": {{
        "gdpr": {{
            "applicable": true|false,
            "reason": "explanation",
            "controls_required": ["encryption", "access_controls"]
        }},
        "hipaa": {{
            "applicable": true|false,
            "reason": "explanation",
            "controls_required": ["audit_logging"]
        }},
        "pci_dss": {{
            "applicable": true|false
        }}
    }},
    "data_residency": {{
        "regions_detected": ["EU", "US"],
        "requirements": {{
            "EU": {{
                "regulation": "GDPR",
                "requirement": "Data must stay in EU",
                "compliant": true|false,
                "action_needed": "description"
            }}
        }}
    }},
    "overall_sensitivity": {{
        "average_score": 75.5,
        "max_score": 95,
        "risk_level": "critical|high|medium|low"
    }},
    "total_data_sources": 5
}}"""

        # Invoke AI for data classification
        ai_response = await self.invoke_ai(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3  # Lower temperature for accurate classification
        )
        
        # Parse JSON response (handle markdown code blocks)
        try:
            classification_results = json.loads(ai_response)
        except json.JSONDecodeError:
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                classification_results = json.loads(json_match.group(1))
            else:
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    classification_results = json.loads(json_match.group(0))
                else:
                    raise ValueError("Could not parse classification results as JSON")
        
        return classification_results
