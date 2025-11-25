import pytest

from agentic_services.agents.diagram_parser import DiagramParserAgent
from .sample_data import sample_drawio_bytes, sample_vsdx_bytes


@pytest.fixture
def diagram_agent(monkeypatch):
    agent = DiagramParserAgent()

    async def fake_invoke(prompt: str):
        return '{"architecture_pattern": "3-tier", "summary": {"total_components": 3, "component_types": ["server","database"], "network_zones": ["DMZ","App Tier"], "notes": ["sample"]}}'

    monkeypatch.setattr(agent.bedrock, "invoke_claude", fake_invoke)
    return agent


@pytest.mark.asyncio
async def test_vsdx_parsing_extracts_components(diagram_agent):
    result = await diagram_agent.execute(
        {
            "diagram_name": "architecture-diagram.vsdx",
            "file_bytes": sample_vsdx_bytes(),
        }
    )
    assert any(comp["name"] == "Web Tier" for comp in result["components"])
    assert result["architecture_pattern"]


@pytest.mark.asyncio
async def test_drawio_parsing_extracts_links(diagram_agent):
    result = await diagram_agent.execute(
        {
            "diagram_name": "data-flow.drawio",
            "file_bytes": sample_drawio_bytes(),
        }
    )
    assert len(result["components"]) >= 3
    assert result["components"][0]["connections_to"] is not None


@pytest.mark.asyncio
async def test_invalid_diagram_raises(diagram_agent):
    with pytest.raises(ValueError):
        await diagram_agent.execute(
            {
                "diagram_name": "diagram.txt",
                "file_bytes": b"not a diagram",
            }
        )

