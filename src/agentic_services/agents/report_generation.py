"""
ReportGenerationAgent
---------------------

Consumes EnvironmentAnalysisAgent output to create a branded PDF and JSON report.
"""

from __future__ import annotations

import base64
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, TypedDict

from langgraph.graph import END, StateGraph

from agentic_services.agents.base import BaseAgent
from agentic_services.config.settings import settings
from agentic_services.utils.report_renderer import ReportRenderer

logger = logging.getLogger(__name__)


class ReportGenerationState(TypedDict, total=False):
    analysis: Dict[str, Any]
    llm_sections: Dict[str, Any]
    report_payload: Dict[str, Any]
    pdf_bytes: bytes
    pdf_s3_uri: str
    json_s3_uri: str


class ReportGenerationAgent(BaseAgent):
    """Generates professional Quick Assess reports."""

    SYSTEM_PROMPT = """You are ReportGenerationAgent inside Nagarro's AIMS platform.
Given cloud environment analysis data, craft rich narrative content for the report
sections listed below. Respond with STRICT JSON:
{
  "executive_summary": {
    "overview": "...",
    "key_findings": ["..."],
    "next_steps": ["..."],
    "overall_score": 0-100
  },
  "infrastructure_inventory": {
     "counts": {"servers": int, "databases": int, "applications": int, "other": int},
     "insights": ["..."]
  },
  "technology_stack": {
     "summary": "...",
     "languages": [...],
     "frameworks": [...],
     "cloud_services": [...],
     "databases": [...],
     "storage": [...]
  },
  "architecture_assessment": {
     "pattern": "...",
     "dependencies": [{"from": "", "to": "", "type": ""}],
     "single_points_of_failure": [...],
     "scalability": {"score": 0-100, "notes": ["..."]},
     "redundancy": {"score": 0-100, "notes": ["..."]}
  },
  "cloud_readiness": {
     "score": 0-100,
     "metrics": {"legacy": 0-100, "modularity": 0-100, "dependencies": 0-100, "statefulness": 0-100, "security": 0-100},
     "explanation": "..."
  },
  "risk_assessment": {
     "overall_risk": "low|medium|high",
     "outdated_technologies": [...],
     "missing_redundancy": [...],
     "security_concerns": [...],
     "complexity_indicators": [...]
  },
  "recommendations": {
     "actions": [{"priority": "High|Medium|Low", "description": "..."}],
     "timeline": "e.g., 6-9 months",
     "cost_estimate": "Rough range",
     "next_steps": ["..."]
  }
}
Keep prose concise but professional. Base claims on provided analysis."""

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id=agent_id)
        self.graph = self._build_graph()
        self.renderer = ReportRenderer()

    def _build_graph(self):
        graph = StateGraph(ReportGenerationState)
        graph.add_node("prepare", self._prepare_context)
        graph.add_node("compose", self._compose_sections)
        graph.add_node("render", self._render_report)
        graph.add_node("finalize", self._finalize)

        graph.set_entry_point("prepare")
        graph.add_edge("prepare", "compose")
        graph.add_edge("compose", "render")
        graph.add_edge("render", "finalize")
        graph.add_edge("finalize", END)
        return graph.compile()

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        self.validate_task(task, ["analysis_results"])
        state: ReportGenerationState = {
            "analysis": task["analysis_results"],
        }
        state["project_id"] = task.get("project_id")  # type: ignore[assignment]
        result = await self.graph.ainvoke(state)
        return {
            "report": result["report_payload"],
            "pdf_s3_uri": result.get("pdf_s3_uri"),
            "json_s3_uri": result.get("json_s3_uri"),
            "pdf_base64": base64.b64encode(result["pdf_bytes"]).decode("utf-8"),
        }

    # LangGraph nodes --------------------------------------------------
    async def _prepare_context(self, state: ReportGenerationState) -> ReportGenerationState:
        analysis = state["analysis"]
        metadata = analysis.get("metadata", {})
        condensed = {
            "metadata": metadata,
            "inventory": analysis.get("infrastructure_inventory", {}),
            "technology_stack": analysis.get("technology_stack", {}),
            "architecture_assessment": analysis.get("architecture_assessment", {}),
            "cloud_readiness": analysis.get("cloud_readiness", {}),
            "risk_assessment": analysis.get("risk_assessment", {}),
            "recommendations": analysis.get("recommendations", {}),
        }
        state["condensed_analysis"] = condensed  # type: ignore[assignment]
        return state

    async def _compose_sections(self, state: ReportGenerationState) -> ReportGenerationState:
        prompt = (
            "Create the professional report structure described in the system prompt "
            "based on the following environment analysis JSON.\n\n"
            f"DATA:\n{json.dumps(state['condensed_analysis'], indent=2)}"
        )
        response = await self.bedrock.invoke_claude(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.25,
            max_tokens=3000,
            model_id=settings.BEDROCK_DOCUMENT_PARSER_MODEL_ID,
        )
        sections = self._safe_json(response.get("text", "{}"))
        state["llm_sections"] = sections
        return state

    async def _render_report(self, state: ReportGenerationState) -> ReportGenerationState:
        report_payload = self._merge_payload(state)
        pdf_bytes = self.renderer.build_pdf(report_payload)
        state["report_payload"] = report_payload
        state["pdf_bytes"] = pdf_bytes

        project_id = state.get("project_id") or "quick-assess"
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        base_key = f"{project_id}/reports/quick-assess-report-{timestamp}"

        try:
            pdf_uri = await self.s3.upload_bytes(
                bucket=self.s3.artifacts_bucket,
                key=f"{base_key}.pdf",
                data=pdf_bytes,
                content_type="application/pdf",
                metadata={"agent": self.agent_type},
            )
            json_uri = await self.s3.upload_json(
                bucket=self.s3.artifacts_bucket,
                key=f"{base_key}.json",
                data=report_payload,
                metadata={"agent": self.agent_type},
            )
            state["pdf_s3_uri"] = pdf_uri
            state["json_s3_uri"] = json_uri
        except Exception as exc:
            logger.warning("Failed to upload report artifacts: %s", exc)

        return state

    async def _finalize(self, state: ReportGenerationState) -> ReportGenerationState:
        return state

    # Helpers ----------------------------------------------------------
    def _merge_payload(self, state: ReportGenerationState) -> Dict[str, Any]:
        payload = state.get("llm_sections", {})
        payload.setdefault("metadata", state["analysis"].get("metadata", {}))
        payload.setdefault("infrastructure_inventory", {}).setdefault(
            "counts", state["analysis"].get("infrastructure_inventory", {}).get("counts", {})
        )
        payload["infrastructure_inventory"]["connections"] = (
            state["analysis"].get("architecture_assessment", {}).get("dependencies", [])
        )
        payload.setdefault("cloud_readiness", {}).setdefault(
            "metrics", state["analysis"].get("cloud_readiness", {}).get("metrics", {})
        )
        return payload

    def _safe_json(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    pass
        return {}

