"""
EnvironmentAnalysisAgent
------------------------

Consumes parsed documents and diagrams to build an end-to-end infrastructure
assessment, leveraging Claude Sonnet 4.5 for deep reasoning and scoring.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from agentic_services.agents.base import BaseAgent
from agentic_services.config.settings import settings

logger = logging.getLogger(__name__)


class EnvironmentAnalysisState(TypedDict, total=False):
    """Shared LangGraph state."""

    documents: List[Dict[str, Any]]
    diagrams: List[Dict[str, Any]]
    aggregate_context: Dict[str, Any]
    llm_response: Dict[str, Any]


class EnvironmentAnalysisAgent(BaseAgent):
    """Runs multi-source environment assessment."""

    SYSTEM_PROMPT = """You are EnvironmentAnalysisAgent for Nagarro's AIMS platform.
Given parsed documents and diagrams, produce a JSON report with sections:

- infrastructure_inventory: {
    "servers": [...],
    "databases": [...],
    "applications": [...],
    "operating_systems": [{"name": "", "version": ""}],
    "counts": {"servers": int, "databases": int, "applications": int, "other": int}
  }
- technology_stack: {
    "languages": [...],
    "frameworks": [...],
    "cloud_services": [...],
    "databases": [...],
    "storage": [...]
  }
- architecture_assessment: {
    "pattern": "",
    "dependencies": [{"from": "", "to": "", "type": ""}],
    "single_points_of_failure": [...],
    "scalability": {"score": 0-100, "notes": [...]},
    "redundancy": {"score": 0-100, "notes": [...]}
  }
- cloud_readiness: {
    "score": 0-100,
    "legacy_technology_count": int,
    "design_style": "monolithic|modular|hybrid",
    "hard_coded_dependencies": [...],
    "statefulness": {"stateful": int, "stateless": int}
  }
- risk_assessment: {
    "outdated_technologies": [...],
    "missing_redundancy": [...],
    "security_concerns": [...],
    "complexity_indicators": [...],
    "overall_risk": "low|medium|high"
  }

Respond with STRICT JSON only. Make reasonable inferences; if data not found,
return empty arrays but keep structure.
"""

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id=agent_id)
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(EnvironmentAnalysisState)
        graph.add_node("aggregate_inputs", self._aggregate_inputs)
        graph.add_node("run_analysis", self._run_analysis)
        graph.add_node("finalize", self._finalize)

        graph.set_entry_point("aggregate_inputs")
        graph.add_edge("aggregate_inputs", "run_analysis")
        graph.add_edge("run_analysis", "finalize")
        graph.add_edge("finalize", END)
        return graph.compile()

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        documents = task.get("documents", [])
        diagrams = task.get("diagrams", [])
        if not documents and not diagrams:
            raise ValueError("Provide at least one parsed document or diagram")

        state: EnvironmentAnalysisState = {
            "documents": documents,
            "diagrams": diagrams,
        }

        logger.info(
            "EnvironmentAnalysisAgent running: %d documents, %d diagrams",
            len(documents),
            len(diagrams),
        )

        result = await self.graph.ainvoke(state)
        return result.get("llm_response", {})

    # LangGraph node implementations -------------------------------------
    async def _aggregate_inputs(
        self, state: EnvironmentAnalysisState
    ) -> EnvironmentAnalysisState:
        aggregate = {
            "documents": self._summarize_documents(state.get("documents", [])),
            "diagrams": self._summarize_diagrams(state.get("diagrams", [])),
        }

        state["aggregate_context"] = aggregate
        return state

    async def _run_analysis(
        self, state: EnvironmentAnalysisState
    ) -> EnvironmentAnalysisState:
        payload = state.get("aggregate_context", {})
        prompt = (
            "Analyze the following environment data and produce the JSON report "
            "described in the system prompt.\n\n"
            f"DATA:\n{json.dumps(payload, indent=2)}"
        )

        response = await self.bedrock.invoke_claude(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=2500,
            model_id=settings.BEDROCK_DOCUMENT_PARSER_MODEL_ID,
        )
        parsed = self._safe_json(response.get("text", "{}"))
        state["llm_response"] = parsed
        return state

    async def _finalize(
        self, state: EnvironmentAnalysisState
    ) -> EnvironmentAnalysisState:
        return state

    # Helper methods -----------------------------------------------------
    def _summarize_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        inventory = {
            "servers": set(),
            "databases": set(),
            "applications": set(),
            "operating_systems": set(),
            "technologies": set(),
        }
        excerpts: List[str] = []
        raw_entities: List[Dict[str, Any]] = []

        for doc in documents:
            entities = doc.get("technical_entities", {})
            for server in entities.get("servers", []):
                inventory["servers"].add(server)
            for tech in entities.get("technologies", []):
                inventory["technologies"].add(tech)
            if entities:
                raw_entities.append(
                    {
                        "document_name": doc.get("document_name"),
                        "technical_entities": entities,
                    }
                )

            metadata = doc.get("metadata", {})
            if title := metadata.get("title"):
                excerpts.append(f"Document: {title}")

            text = doc.get("extracted_text", "")
            if text:
                inventory["operating_systems"].update(self._detect_operating_systems(text))
                excerpts.append(text[:1500])

        return {
            "inventory": {
                key: sorted(values) for key, values in inventory.items()
            },
            "excerpts": excerpts[:10],
            "count": len(documents),
            "raw_entities": raw_entities,
        }

    def _summarize_diagrams(self, diagrams: List[Dict[str, Any]]) -> Dict[str, Any]:
        components: List[Dict[str, Any]] = []
        patterns: List[str] = []
        for diagram in diagrams:
            components.extend(diagram.get("components", []))
            pattern = diagram.get("architecture_pattern")
            if pattern:
                patterns.append(pattern)

        summarized = []
        connections = []
        type_counts: Dict[str, int] = {}
        for component in components[:200]:
            comp_type = component.get("type") or "component"
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
            summarized.append(
                {
                    "type": comp_type,
                    "name": component.get("name"),
                    "labels": component.get("labels", []),
                    "connections_to": component.get("connections_to", []),
                    "connections_from": component.get("connections_from", []),
                }
            )
            for target in component.get("connections_to", []):
                connections.append(
                    {
                        "from": component.get("name"),
                        "to": target,
                        "type": comp_type,
                    }
                )

        return {
            "components": summarized,
            "component_count": len(components),
            "component_types": type_counts,
            "connections": connections[:300],
            "patterns": patterns,
        }

    def _detect_operating_systems(self, text: str) -> List[str]:
        os_keywords = {
            "windows server 2012",
            "windows server 2016",
            "windows server 2019",
            "windows server 2022",
            "rhel",
            "red hat",
            "ubuntu",
            "debian",
            "centos",
            "suse",
            "aix",
            "hp-ux",
            "solaris",
        }
        text_lower = text.lower()
        found = {kw for kw in os_keywords if kw in text_lower}
        return sorted(found)

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

