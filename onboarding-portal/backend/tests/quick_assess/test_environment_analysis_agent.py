import json
import pytest

from agentic_services.agents.environment_analysis import EnvironmentAnalysisAgent


@pytest.fixture
def analysis_agent(monkeypatch):
    agent = EnvironmentAnalysisAgent()

    async def fake_bedrock(prompt: str, system_prompt: str, temperature: float, max_tokens: int, model_id: str):
        return {
            "text": json.dumps(
                {
                    "executive_summary": {
                        "overview": "Environment is ready for modernization.",
                        "key_findings": ["Well-defined tiers"],
                        "next_steps": ["Implement blue/green deployments"],
                        "overall_score": 78,
                    },
                    "infrastructure_inventory": {
                        "counts": {"servers": 4, "databases": 2, "applications": 3, "other": 1},
                        "insights": ["Redundant web tier"],
                    },
                    "technology_stack": {
                        "summary": "Modern stack",
                        "languages": ["Python"],
                        "frameworks": ["FastAPI"],
                        "cloud_services": ["AWS EC2"],
                        "databases": ["PostgreSQL"],
                        "storage": ["S3"],
                    },
                    "architecture_assessment": {
                        "pattern": "3-tier",
                        "dependencies": [{"from": "Web", "to": "App", "type": "http"}],
                        "single_points_of_failure": [],
                        "scalability": {"score": 70, "notes": ["Horizontally scalable"]},
                        "redundancy": {"score": 65, "notes": ["Needs multi-AZ DB"]},
                    },
                    "cloud_readiness": {
                        "score": 80,
                        "metrics": {
                            "legacy": 20,
                            "modularity": 70,
                            "dependencies": 60,
                            "statefulness": 40,
                            "security": 75,
                        },
                        "explanation": "Ready with minor refactor.",
                    },
                    "risk_assessment": {
                        "overall_risk": "medium",
                        "outdated_technologies": [],
                        "missing_redundancy": ["Single DB instance"],
                        "security_concerns": [],
                        "complexity_indicators": [],
                    },
                    "recommendations": {
                        "actions": [
                            {"priority": "High", "description": "Add DB replicas"},
                        ],
                        "timeline": "3-6 months",
                        "cost_estimate": "Medium",
                        "next_steps": ["Architect failover"],
                    },
                }
            )
        }

    monkeypatch.setattr(agent.bedrock, "invoke_claude", fake_bedrock)
    return agent


@pytest.mark.asyncio
async def test_analysis_agent_generates_inventory(analysis_agent):
    documents = [
        {
            "document_name": "doc1",
            "technical_entities": {"servers": ["web-01"], "technologies": ["NGINX"]},
            "metadata": {"title": "Design"},
            "extracted_text": "Ubuntu server running nginx.",
        }
    ]
    diagrams = [
        {
            "diagram_name": "diagram.vsdx",
            "components": [{"name": "Web", "type": "server", "labels": ["DMZ"], "connections_to": ["App"]}],
        }
    ]

    result = await analysis_agent.execute({"documents": documents, "diagrams": diagrams})
    assert result["infrastructure_inventory"]["counts"]["servers"] == 4
    assert result["cloud_readiness"]["score"] == 80
    assert result["risk_assessment"]["overall_risk"] == "medium"


@pytest.mark.asyncio
async def test_analysis_agent_handles_empty_inputs(analysis_agent):
    result = await analysis_agent.execute({"documents": [], "diagrams": []})
    assert result["executive_summary"]["overview"]
    assert "technology_stack" in result

