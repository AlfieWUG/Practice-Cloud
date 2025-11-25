import pytest

from agentic_services.agents.document_parser import (
    DocumentParseError,
    DocumentParserAgent,
)
from .sample_data import sample_docx_bytes, sample_pdf_bytes


@pytest.fixture
def doc_agent(monkeypatch):
    agent = DocumentParserAgent()

    async def fake_invoke(*args, **kwargs):
        return '{"servers": ["web-01"], "ip_addresses": ["10.0.0.1"], "technologies": ["NGINX"]}'

    monkeypatch.setattr(agent, "_invoke_bedrock", fake_invoke)
    return agent


@pytest.mark.asyncio
async def test_docx_parsing_returns_text(doc_agent):
    result = await doc_agent.execute(
        {
            "document_name": "infrastructure-design.docx",
            "file_bytes": sample_docx_bytes(),
        }
    )
    assert result["document_type"] == "word"
    assert "infrastructure" in result["extracted_text"].lower()
    assert result["structure"]["sections"]


@pytest.mark.asyncio
async def test_pdf_parsing_returns_text(doc_agent):
    result = await doc_agent.execute(
        {
            "document_name": "network-layout.pdf",
            "file_bytes": sample_pdf_bytes(),
        }
    )
    assert result["document_type"] == "pdf"
    assert "load balancer" in result["extracted_text"].lower()
    assert result["structure"]["sections"]


@pytest.mark.asyncio
async def test_corrupted_file_raises(doc_agent):
    with pytest.raises(DocumentParseError):
        await doc_agent.execute(
            {
                "document_name": "broken.docx",
                "file_bytes": b"\x00\x01bad-data",
            }
        )


@pytest.mark.asyncio
async def test_output_contains_required_fields(doc_agent):
    result = await doc_agent.execute(
        {
            "document_name": "tech-overview.pdf",
            "file_bytes": sample_pdf_bytes(),
        }
    )
    assert {"document_name", "document_type", "metadata", "technical_entities"} <= result.keys()
    assert isinstance(result["technical_entities"]["servers"], list)

