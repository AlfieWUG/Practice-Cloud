#!/usr/bin/env python3
"""Create sample artifacts for testing the Reports & Artifacts Hub"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agentic_services.database import get_db

def create_sample_artifacts():
    """Create sample artifacts for existing projects"""
    db = get_db()
    
    # Get all projects
    projects = db.get_all_projects()
    
    if not projects:
        print("❌ No projects found. Create a project first.")
        return
    
    print(f"📊 Found {len(projects)} project(s)")
    print()
    
    # Sample artifacts to create
    artifacts_created = 0
    
    for project in projects:
        print(f"Creating artifacts for: {project['name']}")
        
        # 1. Migration Plan
        artifact_data = {
            'project_id': project['id'],
            'agent_name': 'planning',
            'artifact_type': 'migration_plan',
            'title': f"{project['name']} - Migration Plan",
            'description': 'Comprehensive migration plan with timelines and resource allocation',
            'content': f"""# Migration Plan: {project['name']}

## Executive Summary
This document outlines the comprehensive migration strategy for {project['name']}.

## Project Overview
- **Timeline**: {project.get('timeline', 'N/A')}
- **Priority**: {project.get('priority', 'N/A')}
- **Budget**: {project.get('budget', 'N/A')}
- **Complexity**: {project.get('complexity', 'N/A')}

## Migration Strategy
### Phase 1: Discovery & Assessment
- Infrastructure discovery and dependency mapping
- Application profiling and performance baseline
- Risk assessment and compliance review

### Phase 2: Planning & Design
- Target architecture design
- Wave planning and sequencing
- Resource allocation and timeline
- Cost estimation and optimization

### Phase 3: Execution
- Infrastructure provisioning (IaC)
- Data migration (staged approach)
- Application migration (blue-green deployment)
- Testing and validation

### Phase 4: Optimization
- Performance tuning
- Cost optimization
- Security hardening
- Documentation and knowledge transfer

## Risk Mitigation
- **Risk 1**: Data loss during migration → Implement checkpoint-based migration
- **Risk 2**: Downtime exceeds window → Blue-green deployment strategy
- **Risk 3**: Cost overruns → Weekly cost reviews and optimization

## Success Criteria
- ✅ Zero data loss
- ✅ < 4 hours downtime
- ✅ Budget variance < 10%
- ✅ All compliance requirements met

## Next Steps
1. Finalize target architecture design
2. Obtain stakeholder approvals
3. Begin infrastructure provisioning
4. Schedule pilot migration
""",
            'file_size': 2048,
            'metadata': {
                'version': '1.0',
                'status': 'approved',
                'approver': 'Migration Team Lead'
            }
        }
        
        db.create_artifact(artifact_data)
        artifacts_created += 1
        print("  ✅ Migration Plan created")
        
        # 2. Wave Plan
        artifact_data = {
            'project_id': project['id'],
            'agent_name': 'planning',
            'artifact_type': 'wave_plan',
            'title': f"{project['name']} - Wave Plan",
            'description': 'Detailed wave-based migration sequence with dependencies',
            'content': f"""# Wave Plan: {project['name']}

## Wave Strategy
Applications grouped into waves based on dependencies, complexity, and business impact.

## Wave 1: Foundation (Week 1-2)
**Objective**: Establish baseline infrastructure
- VPC and networking setup
- Security groups and IAM roles
- Database infrastructure (RDS, DynamoDB)
- S3 buckets and data pipeline

**Applications**: None (infrastructure only)
**Risk**: Low
**Rollback**: Full rollback available

## Wave 2: Non-Critical Services (Week 3-4)
**Objective**: Migrate low-risk, standalone services
- Logging service
- Monitoring dashboards
- Internal tools
- Batch processing jobs

**Applications**: 4 services
**Dependencies**: Wave 1 complete
**Risk**: Low
**Rollback**: Service-level rollback

## Wave 3: Core Services (Week 5-7)
**Objective**: Migrate business-critical services
- Authentication service
- API Gateway
- Core business logic services
- Customer-facing APIs

**Applications**: 8 services
**Dependencies**: Wave 1 & 2 complete
**Risk**: Medium
**Rollback**: Blue-green deployment

## Wave 4: Frontend & Integration (Week 8-10)
**Objective**: Complete migration with user-facing components
- Web applications
- Mobile backends
- Third-party integrations
- CDN and edge services

**Applications**: 6 services
**Dependencies**: Wave 3 complete
**Risk**: Medium-High
**Rollback**: DNS-based rollback

## Wave 5: Optimization (Week 11-12)
**Objective**: Fine-tune and optimize
- Performance optimization
- Cost optimization
- Security hardening
- Load testing

**Applications**: All (tuning)
**Dependencies**: All waves complete
**Risk**: Low
**Rollback**: Configuration rollback

## Critical Path
Wave 1 → Wave 2 → Wave 3 → Wave 4 → Wave 5

## Go/No-Go Criteria
Each wave requires:
- ✅ Previous wave 100% complete
- ✅ All tests passing
- ✅ Stakeholder approval
- ✅ Rollback plan validated
""",
            'file_size': 2560,
            'metadata': {
                'version': '1.0',
                'total_waves': 5,
                'duration_weeks': 12
            }
        }
        
        db.create_artifact(artifact_data)
        artifacts_created += 1
        print("  ✅ Wave Plan created")
        
        # 3. Cost Analysis
        artifact_data = {
            'project_id': project['id'],
            'agent_name': 'cost_estimator',
            'artifact_type': 'cost_analysis',
            'title': f"{project['name']} - Cost Analysis",
            'description': 'Detailed cost breakdown and TCO comparison',
            'content': f"""# Cost Analysis: {project['name']}

## Current State (On-Premises)
**Annual Cost**: $450,000
- Hardware: $120,000 (depreciation)
- Data Center: $180,000 (colocation, power, cooling)
- Maintenance: $80,000 (support contracts)
- Staff: $70,000 (allocated ops time)

## Target State (AWS Cloud)
**Year 1 Cost**: $380,000
- Compute (EC2, Fargate): $140,000
- Storage (S3, EBS, EFS): $45,000
- Database (RDS, DynamoDB): $85,000
- Networking (VPC, NLB, CloudFront): $35,000
- Data Transfer: $25,000
- Migration Services: $30,000
- Monitoring & Security: $20,000

## 3-Year TCO Comparison
| Year | On-Premises | AWS Cloud | Savings |
|------|-------------|-----------|---------|
| 1    | $450,000    | $380,000  | $70,000 |
| 2    | $450,000    | $320,000  | $130,000|
| 3    | $500,000*   | $300,000  | $200,000|

*Includes hardware refresh cycle

**Total 3-Year Savings**: $400,000 (29% reduction)

## Cost Optimization Opportunities
1. **Reserved Instances**: $45,000/year savings (compute)
2. **Savings Plans**: $20,000/year savings (committed usage)
3. **S3 Intelligent Tiering**: $8,000/year savings (storage)
4. **Right-sizing**: $25,000/year savings (over-provisioned resources)

**Total Optimization Potential**: $98,000/year

## Break-Even Analysis
- Migration cost: $30,000
- Monthly savings: $5,833
- **Break-even**: Month 6

## Recommendations
1. Purchase 1-year Reserved Instances for predictable workloads
2. Enable Cost Anomaly Detection
3. Implement FinOps practices (weekly reviews)
4. Use Spot Instances for non-critical batch jobs
""",
            'file_size': 2048,
            'metadata': {
                'currency': 'USD',
                'period': '3-year',
                'savings_percent': 29
            }
        }
        
        db.create_artifact(artifact_data)
        artifacts_created += 1
        print("  ✅ Cost Analysis created")
        
        print()
    
    print("="*60)
    print(f"✅ Created {artifacts_created} sample artifacts")
    print(f"📊 View them in: streamlit run app_streamlit.py → Reports")
    print("="*60)

if __name__ == "__main__":
    try:
        create_sample_artifacts()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
