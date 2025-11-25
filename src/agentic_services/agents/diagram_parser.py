"""
DiagramParserAgent
------------------

LangGraph-powered agent that parses Visio (.vsdx) and draw.io (.drawio / .xml)
architecture diagrams, extracts infrastructure components/connectivity, and
invokes Claude Sonnet 4.5 via Bedrock for higher-level pattern detection.
"""

from __future__ import annotations

import asyncio
import html
import io
import json
import logging
import re
import zipfile
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Tuple, TypedDict

from defusedxml import ElementTree as ET
from langgraph.graph import END, StateGraph

from agentic_services.agents.base import BaseAgent
from agentic_services.config.settings import settings

logger = logging.getLogger(__name__)


class DiagramParserState(TypedDict, total=False):
    """LangGraph state shared between nodes."""

    diagram_name: str
    diagram_type: Literal["visio", "drawio"]
    source_path: Optional[str]
    s3_uri: Optional[str]
    file_bytes: Optional[bytes]
    raw_bytes: bytes
    components: List[Dict[str, Any]]
    summary: Dict[str, Any]
    architecture_pattern: str
    _labels_blob: str
    errors: List[str]


@dataclass
class ParsedDiagram:
    """Structured diagram information."""

    components: List[Dict[str, Any]]
    labels_blob: str


class DiagramParserAgent(BaseAgent):
    """Parses diagrams and enriches results using Claude Sonnet."""

    SYSTEM_PROMPT = """You are DiagramParserAgent embedded in Nagarro's AIMS platform.
Given a JSON summary of architecture components, infer:
- The overarching architecture pattern (e.g., 3-tier web application, microservices mesh, data lake)
- Key zones or tiers involved
- Any notable infrastructure characteristics

Return STRICT JSON:
{
  "architecture_pattern": "<pattern>",
  "summary": {
     "total_components": <int>,
     "component_types": ["type1", "type2"],
     "network_zones": ["zone1", "zone2"],
     "notes": ["bullet1", "bullet2"]
  }
}
"""

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(agent_id=agent_id)
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(DiagramParserState)
        graph.add_node("load_diagram", self._load_diagram)
        graph.add_node("extract_elements", self._extract_elements)
        graph.add_node("identify_pattern", self._identify_pattern)
        graph.add_node("aggregate", self._aggregate)

        graph.set_entry_point("load_diagram")
        graph.add_edge("load_diagram", "extract_elements")
        graph.add_edge("extract_elements", "identify_pattern")
        graph.add_edge("identify_pattern", "aggregate")
        graph.add_edge("aggregate", END)
        return graph.compile()

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Entry point required by BaseAgent."""
        self.validate_task(task, ["diagram_name"])
        if not any([task.get("file_path"), task.get("s3_uri"), task.get("file_bytes")]):
            raise ValueError("Provide file_path, s3_uri, or file_bytes")

        state: DiagramParserState = {
            "diagram_name": task["diagram_name"],
            "source_path": task.get("file_path"),
            "s3_uri": task.get("s3_uri"),
            "file_bytes": task.get("file_bytes"),
            "errors": [],
        }

        logger.info("DiagramParserAgent starting for %s", task["diagram_name"])

        result = await self.graph.ainvoke(state)

        return {
            "diagram_name": task["diagram_name"],
            "diagram_type": result.get("diagram_type"),
            "components": result.get("components", []),
            "architecture_pattern": result.get("architecture_pattern", "unknown"),
            "summary": result.get("summary", {}),
        }

    # LangGraph nodes -----------------------------------------------------
    async def _load_diagram(self, state: DiagramParserState) -> DiagramParserState:
        diagram_type = self._infer_type(state["diagram_name"])

        if state.get("file_bytes"):
            raw_bytes = state["file_bytes"]  # type: ignore[assignment]
        elif state.get("source_path"):
            raw_bytes = await asyncio.to_thread(self._read_local, state["source_path"])
        elif state.get("s3_uri"):
            raw_bytes = await self._read_s3(state["s3_uri"])
        else:
            raise FileNotFoundError("Diagram source not found")

        return {
            "raw_bytes": raw_bytes,
            "diagram_type": diagram_type,
        }

    async def _extract_elements(self, state: DiagramParserState) -> DiagramParserState:
        raw_bytes = state["raw_bytes"]
        diagram_type = state["diagram_type"]

        try:
            if diagram_type == "visio":
                parsed = await asyncio.to_thread(self._parse_vsdx, raw_bytes)
            else:
                parsed = await asyncio.to_thread(self._parse_drawio, raw_bytes)
        except Exception as exc:
            raise RuntimeError(f"Failed to parse diagram: {exc}") from exc

        summary = self._summarize_components(parsed.components)
        summary["labels_scan"] = parsed.labels_blob[:2000]

        return {
            "components": parsed.components,
            "summary": summary,
            "_labels_blob": parsed.labels_blob,
        }

    async def _identify_pattern(self, state: DiagramParserState) -> DiagramParserState:
        payload = {
            "components": state.get("components", []),
            "summary": {
                k: v for k, v in state.get("summary", {}).items() if k != "labels_scan"
            },
            "labels": state.get("_labels_blob", "")[:4000],
        }

        prompt = (
            "Analyze the JSON describing an architecture diagram and infer the high-level pattern.\n"
            "Respond with JSON exactly matching the schema described in the system prompt.\n"
            f"DATA:\n{json.dumps(payload, indent=2)}"
        )

        try:
            response = await self.bedrock.invoke_claude(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.2,
                max_tokens=1500,
                model_id=settings.BEDROCK_DOCUMENT_PARSER_MODEL_ID,
            )
            parsed = self._safe_json(response["text"])
        except Exception as exc:
            logger.warning("Pattern recognition failed: %s", exc)
            parsed = {
                "architecture_pattern": "unknown",
                "summary": {
                    "total_components": state["summary"].get("total_components", 0),
                    "component_types": state["summary"].get("component_types", []),
                    "network_zones": state["summary"].get("network_zones", []),
                    "notes": ["Pattern identification failed"],
                },
            }

        return {
            "architecture_pattern": parsed.get("architecture_pattern", "unknown"),
            "summary": parsed.get("summary", state.get("summary", {})),
        }

    async def _aggregate(self, state: DiagramParserState) -> DiagramParserState:
        return state

    # Utility methods -----------------------------------------------------
    def _infer_type(self, filename: str) -> Literal["visio", "drawio"]:
        suffix = filename.lower().split(".")[-1]
        if suffix == "vsdx":
            return "visio"
        if suffix in {"drawio", "xml"}:
            return "drawio"
        raise ValueError("Unsupported diagram type; expected .vsdx or .drawio/.xml")

    def _read_local(self, path: str) -> bytes:
        with open(path, "rb") as file:
            return file.read()

    async def _read_s3(self, uri: str) -> bytes:
        bucket, key = self._parse_s3_uri(uri)
        response = await asyncio.to_thread(
            self.s3.client.get_object,
            Bucket=bucket,
            Key=key,
        )
        return response["Body"].read()

    def _parse_s3_uri(self, uri: str) -> Tuple[str, str]:
        stripped = uri.replace("s3://", "", 1)
        bucket, _, key = stripped.partition("/")
        if not bucket or not key:
            raise ValueError("Invalid S3 URI")
        return bucket, key

    def _parse_vsdx(self, raw_bytes: bytes) -> ParsedDiagram:
        components: List[Dict[str, Any]] = []
        labels_blob: List[str] = []
        with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
            page_files = [
                name
                for name in zf.namelist()
                if name.startswith("visio/pages/page") and name.endswith(".xml")
            ]
            if not page_files:
                raise ValueError("No Visio page definitions found")

            ns = {"v": "http://schemas.microsoft.com/office/visio/2012/main"}

            for page_file in page_files:
                xml_root = ET.fromstring(zf.read(page_file))
                shape_map: Dict[str, Dict[str, Any]] = {}

                for shape in xml_root.findall(".//v:Shape", ns):
                    shape_id = shape.attrib.get("ID")
                    text_elem = shape.find(".//v:Text/v:cp", ns)
                    text_value = (
                        "".join(text_elem.itertext()).strip()
                        if text_elem is not None
                        else ""
                    )
                    if shape_id:
                        shape_map[shape_id] = {
                            "type": self._infer_component_type(text_value),
                            "name": text_value or f"Shape {shape_id}",
                            "labels": [
                                text_value,
                            ]
                            if text_value
                            else [],
                            "connections_to": [],
                            "connections_from": [],
                        }
                        if text_value:
                            labels_blob.append(text_value)

                for connect in xml_root.findall(".//v:Connect", ns):
                    from_id = connect.attrib.get("FromSheet")
                    to_id = connect.attrib.get("ToSheet")
                    if not from_id or not to_id:
                        continue
                    from_shape = shape_map.get(from_id)
                    to_shape = shape_map.get(to_id)
                    if from_shape and to_shape:
                        from_shape["connections_to"].append(to_shape["name"])
                        to_shape["connections_from"].append(from_shape["name"])

                components.extend(shape_map.values())

        return ParsedDiagram(components=components, labels_blob="\n".join(labels_blob))

    def _parse_drawio(self, raw_bytes: bytes) -> ParsedDiagram:
        tree = ET.fromstring(raw_bytes)
        components: List[Dict[str, Any]] = []
        labels_blob: List[str] = []
        node_map: Dict[str, Dict[str, Any]] = {}

        for cell in tree.findall(".//mxCell"):
            cell_id = cell.attrib.get("id")
            if cell.attrib.get("vertex") == "1":
                raw_label = html.unescape(cell.attrib.get("value", ""))
                label_clean = self._strip_tags(raw_label).strip()
                labels_blob.append(label_clean)
                comp = {
                    "type": self._infer_component_type(label_clean),
                    "name": label_clean or f"Component {cell_id}",
                    "labels": [label_clean] if label_clean else [],
                    "connections_to": [],
                    "connections_from": [],
                }
                node_map[cell_id] = comp
                components.append(comp)

        for cell in tree.findall(".//mxCell"):
            if cell.attrib.get("edge") != "1":
                continue
            source = cell.attrib.get("source")
            target = cell.attrib.get("target")
            if source and target and source in node_map and target in node_map:
                src = node_map[source]
                tgt = node_map[target]
                src["connections_to"].append(tgt["name"])
                tgt["connections_from"].append(src["name"])

        return ParsedDiagram(components=components, labels_blob="\n".join(labels_blob))

    def _infer_component_type(self, label: str) -> str:
        text = (label or "").lower()
        if any(keyword in text for keyword in ["db", "database", "sql", "postgres", "mysql"]):
            return "database"
        if any(keyword in text for keyword in ["server", "app", "api", "service"]):
            return "application"
        if any(keyword in text for keyword in ["load balancer", "elb", "alb", "gateway"]):
            return "load_balancer"
        if any(keyword in text for keyword in ["cache", "redis", "memcache"]):
            return "cache"
        if any(keyword in text for keyword in ["queue", "sns", "sqs", "kafka"]):
            return "messaging"
        if any(keyword in text for keyword in ["s3", "bucket", "storage"]):
            return "storage"
        return "server" if text else "component"

    def _summarize_components(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        types = sorted({comp["type"] for comp in components})
        total = len(components)
        zones = self._infer_zones_from_components(components)
        return {
            "total_components": total,
            "component_types": types,
            "network_zones": zones,
        }

    def _infer_zones_from_components(self, components: List[Dict[str, Any]]) -> List[str]:
        zones: set[str] = set()
        zone_keywords = {
            "dmz": ["dmz", "perimeter"],
            "app tier": ["app tier", "application tier"],
            "data tier": ["data tier", "database tier"],
            "core": ["core network", "core services"],
        }
        for comp in components:
            text = " ".join(comp.get("labels", []))
            lower = text.lower()
            for zone, keywords in zone_keywords.items():
                if any(keyword in lower for keyword in keywords):
                    zones.add(zone.title())
        return sorted(zones)

    def _strip_tags(self, html_text: str) -> str:
        return re.sub(r"<[^>]+>", " ", html_text)

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

