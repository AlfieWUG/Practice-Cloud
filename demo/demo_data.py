#!/usr/bin/env python3
"""Demo data for webinar"""

DEMO_SCENARIO = {
    "company": "Meridian Financial Group",
    "current_environment": {
        "servers": 247,
        "applications": 156,
        "databases": 42,
        "storage_tb": 850,
        "age": "8-12 years old",
        "datacenter": "Legacy on-premises DC"
    },
    "target": "AWS Cloud",
    "timeline": "12 months",
    "budget": "$4.2M"
}

DISCOVERY_RESULTS = {
    "summary": {
        "total_servers": 247,
        "virtual_machines": 189,
        "physical_servers": 58,
        "applications": 156,
        "databases": 42,
        "critical_apps": 23,
        "dependencies_mapped": 1847
    },
    "application_portfolio": [
        {"name": "Customer Portal", "tier": "Mission Critical", "complexity": "High", "dependencies": 12},
        {"name": "Payment Processing", "tier": "Mission Critical", "complexity": "Very High", "dependencies": 18},
        {"name": "Core Banking System", "tier": "Mission Critical", "complexity": "Very High", "dependencies": 25},
        {"name": "CRM System", "tier": "Business Critical", "complexity": "Medium", "dependencies": 8},
        {"name": "HR Portal", "tier": "Standard", "complexity": "Low", "dependencies": 3},
        {"name": "Internal Wiki", "tier": "Standard", "complexity": "Low", "dependencies": 2},
        {"name": "Email Archive", "tier": "Standard", "complexity": "Low", "dependencies": 1},
        {"name": "Dev/Test Environment", "tier": "Standard", "complexity": "Medium", "dependencies": 5}
    ]
}

ASSESSMENT_RESULTS = {
    "cloud_readiness_score": 68,
    "migration_strategies": {
        "rehost": 45,
        "replatform": 30,
        "refactor": 15,
        "retire": 10
    },
    "cost_projection": {
        "migration_cost": "$3.8M",
        "year_1_cloud_cost": "$1.2M",
        "year_3_savings": "$2.1M annually"
    }
}

WAVE_PLAN = {
    "total_waves": 7,
    "timeline": "36 weeks",
    "waves": [
        {
            "wave": 0,
            "name": "Pilot Wave",
            "duration": "3 weeks",
            "apps": ["Internal Wiki", "Dev/Test Environment"],
            "servers": 12,
            "risk": "Low"
        },
        {
            "wave": 1,
            "name": "Non-Critical Systems",
            "duration": "4 weeks",
            "apps": ["Email Archive", "HR Portal"],
            "servers": 18,
            "risk": "Low"
        },
        {
            "wave": 2,
            "name": "Supporting Systems",
            "duration": "5 weeks",
            "apps": ["CRM System", "Reporting Tools"],
            "servers": 35,
            "risk": "Medium"
        },
        {
            "wave": 3,
            "name": "Business Applications",
            "duration": "6 weeks",
            "apps": ["Customer Portal"],
            "servers": 42,
            "risk": "High"
        },
        {
            "wave": 4,
            "name": "Payment Systems",
            "duration": "8 weeks",
            "apps": ["Payment Processing"],
            "servers": 38,
            "risk": "Very High"
        },
        {
            "wave": 5,
            "name": "Core Banking - Phase 1",
            "duration": "6 weeks",
            "apps": ["Core Banking - Read"],
            "servers": 45,
            "risk": "Very High"
        },
        {
            "wave": 6,
            "name": "Core Banking - Phase 2",
            "duration": "4 weeks",
            "apps": ["Core Banking - Write"],
            "servers": 35,
            "risk": "Critical"
        }
    ]
}

QUICK_ASSESS_FILES = [
    {"filename": "infrastructure-design.docx", "type": "Architecture Doc", "size_mb": 2.4, "status": "Parsed"},
    {"filename": "application-inventory.pdf", "type": "Inventory", "size_mb": 3.1, "status": "Parsed"},
    {"filename": "core-network.vsdx", "type": "Visio Diagram", "size_mb": 1.8, "status": "Analyzed"},
    {"filename": "data-flow.drawio", "type": "Draw.io Diagram", "size_mb": 0.9, "status": "Analyzed"},
    {"filename": "operations-playbook.docx", "type": "Runbook", "size_mb": 1.1, "status": "Pending Review"}
]

QUICK_ASSESS_RESULTS = {
    "assessment_id": "QA-1427",
    "cloud_readiness_score": 74,
    "summary": {
        "documents_processed": 5,
        "diagrams_parsed": 2,
        "entities_detected": 312,
        "processing_time": "7m 32s"
    },
    "risks": {
        "outdated_os": 4,
        "single_points_of_failure": 3,
        "missing_monitoring": 5,
        "manual_deployments": 2
    },
    "technology_stack": {
        "languages": ["Java", "C#", "Python"],
        "frameworks": ["Spring Boot", ".NET Core", "Django"],
        "databases": ["Oracle", "PostgreSQL", "MongoDB"],
        "platforms": ["VMware", "AWS", "Bare Metal"]
    },
    "recommendations": [
        "Prioritize modernization of payment services currently on unsupported OS.",
        "Introduce blue/green deployment capabilities to reduce outage risk.",
        "Implement centralized logging/monitoring before migration waves.",
        "Decompose reporting monolith into domain services during refactor waves."
    ]
}
