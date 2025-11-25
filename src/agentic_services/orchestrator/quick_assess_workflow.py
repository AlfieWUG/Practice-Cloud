"""
QuickAssessWorkflow orchestrates the Quick Assess pipeline using LangGraph.

Nodes:
1. FileIngestionNode         → Pull uploaded files + metadata from S3/DynamoDB
2. DocumentParsingNode       → Parse DOCX/PDF via DocumentParserAgent
3. DiagramParsingNode        → Parse VSDX/draw.io via DiagramParserAgent
4. AnalysisNode              → Aggregate results with EnvironmentAnalysisAgent
5. ReportGenerationNode      → Generate PDF + JSON report artifacts
6. NotificationNode          → Update DynamoDB + emit completion events
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict
from uuid import uuid4

from langgraph.graph import END, StateGraph

from agentic_services.agents import (
    DocumentParserAgent,
    DiagramParserAgent,
    EnvironmentAnalysisAgent,
    ReportGenerationAgent,
)
from agentic_services.config.settings import settings
from agentic_services.tools.aws_helper import dynamodb_client, s3_client, eventbridge_client

logger = logging.getLogger(__name__)


class QuickAssessState(TypedDict, total=False):
    assessment_id: str
    project_id: Optional[str]
    uploaded_files: List[Dict[str, Any]]
    documents_buffer: List[Dict[str, Any]]
    diagrams_buffer: List[Dict[str, Any]]
    parsed_documents: List[Dict[str, Any]]
    parsed_diagrams: List[Dict[str, Any]]
    analysis_results: Dict[str, Any]
    report: Dict[str, Any]
    report_url: Optional[str]
    report_json_url: Optional[str]
    report_base64: Optional[str]
    status: str
    error_messages: List[str]
    execution_log: List[Dict[str, Any]]
    documents_ready: bool
    diagrams_ready: bool
    token_usage: Dict[str, int]


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class WorkflowMetrics:
    node: str
    started_at: float
    duration_ms: Optional[float] = None
    retries: int = 0
    success: bool = True
    error: Optional[str] = None


class QuickAssessWorkflow:
    """LangGraph workflow that orchestrates Quick Assess pipeline."""

    def __init__(self, assessment_id: str, project_id: Optional[str] = None, max_retries: int = 3):
        self.assessment_id = assessment_id
        self.project_id = project_id
        self.max_retries = max_retries
        self.workflow_id = f"qa-wf-{uuid4().hex}"

        self.document_agent = DocumentParserAgent()
        self.diagram_agent = DiagramParserAgent()
        self.analysis_agent = EnvironmentAnalysisAgent()
        self.report_agent = ReportGenerationAgent()

        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(QuickAssessState)

        graph.add_node("file_ingestion", self._wrap_node("FileIngestionNode", self._file_ingestion))
        graph.add_node("document_parsing", self._wrap_node("DocumentParsingNode", self._document_parsing))
        graph.add_node("diagram_parsing", self._wrap_node("DiagramParsingNode", self._diagram_parsing))
        graph.add_node("analysis_gate", self._analysis_gate)
        graph.add_node("analysis", self._wrap_node("AnalysisNode", self._analysis))
        graph.add_node("report_generation", self._wrap_node("ReportGenerationNode", self._report_generation))
        graph.add_node("notification", self._wrap_node("NotificationNode", self._notification))

        # Set entry point and build sequential flow
        # Run parsing sequentially (document then diagram) to avoid LangGraph edge conflicts
        graph.add_edge("file_ingestion", "document_parsing")
        graph.add_edge("document_parsing", "diagram_parsing")
        graph.add_edge("diagram_parsing", "analysis_gate")
        
        # Set entry point AFTER adding edges to avoid conflicts
        graph.set_entry_point("file_ingestion")

        # Analysis gate - always proceed to analysis (both parsing nodes complete sequentially)
        graph.add_edge("analysis_gate", "analysis")
        
        # Continue flow
        graph.add_edge("analysis", "report_generation")
        graph.add_edge("report_generation", "notification")
        graph.add_edge("notification", END)

        # Compile the graph
        try:
            compiled = graph.compile()
            logger.info("QuickAssess workflow graph compiled successfully")
            return compiled
        except Exception as e:
            logger.error(f"Failed to compile workflow graph: {e}", exc_info=True)
            raise

    async def run(self) -> Dict[str, Any]:
        """Execute the Quick Assess workflow."""
        initial_state: QuickAssessState = {
            "assessment_id": self.assessment_id,
            "project_id": self.project_id,
            "status": "processing",
            "uploaded_files": [],
            "documents_buffer": [],
            "diagrams_buffer": [],
            "parsed_documents": [],
            "parsed_diagrams": [],
            "analysis_results": {},
            "report": {},
            "error_messages": [],
            "execution_log": [],
            "documents_ready": False,
            "diagrams_ready": False,
            "token_usage": {},
        }

        await self._update_status("processing", {"message": "Workflow started", "stage": "ingestion", "progress": 10})

        try:
            result = await self.graph.ainvoke(initial_state)
            await self._set_stage("completed", 100)
            await self._update_status(
                "completed",
                {
                    "report_url": result.get("report_url"),
                    "report_json_url": result.get("report_json_url"),
                },
            )
            return result
        except Exception as exc:
            logger.exception("QuickAssessWorkflow failed: %s", exc)
            await self._update_status("failed", {"error": str(exc)})
            raise

    # ------------------------------------------------------------------
    # Node implementations
    # ------------------------------------------------------------------
    async def _file_ingestion(self, state: QuickAssessState) -> QuickAssessState:
        metadata = await dynamodb_client.get_item(
            settings.DYNAMODB_QUICK_ASSESS_TABLE,
            {"assessment_id": self.assessment_id},
        )
        if not metadata:
            raise ValueError(f"No metadata found for assessment {self.assessment_id}")

        files = metadata.get("files", [])
        state["uploaded_files"] = files

        documents: List[Dict[str, Any]] = []
        diagrams: List[Dict[str, Any]] = []

        async def _download(file_item: Dict[str, Any]) -> Dict[str, Any]:
            obj = await asyncio.to_thread(
                s3_client.client.get_object,
                Bucket=s3_client.quick_assess_bucket,
                Key=file_item["s3_key"],
            )
            data = obj["Body"].read()
            return {
                "filename": file_item["filename"],
                "content": data,
                "content_type": file_item.get("content_type"),
                "s3_key": file_item["s3_key"],
            }

        download_tasks = [_download(file_item) for file_item in files]
        downloaded = await asyncio.gather(*download_tasks, return_exceptions=True)

        for item in downloaded:
            if isinstance(item, Exception):
                self._record_error(state, "FileIngestionNode", item)
                continue
            filename = item["filename"].lower()
            if filename.endswith((".docx", ".pdf")):
                documents.append(item)
            elif filename.endswith((".vsdx", ".drawio", ".xml")):
                diagrams.append(item)
            else:
                self._record_error(state, "FileIngestionNode", ValueError(f"Unsupported file: {filename}"))

        state["documents_buffer"] = documents
        state["diagrams_buffer"] = diagrams
        state["documents_ready"] = not documents
        state["diagrams_ready"] = not diagrams
        await self._set_stage("parsing", 25)
        return state

    async def _document_parsing(self, state: QuickAssessState) -> QuickAssessState:
        documents = state.get("documents_buffer", [])
        if not documents:
            state["documents_ready"] = True
            return state

        async def _parse(doc):
            return await self.document_agent.execute(
                {"document_name": doc["filename"], "file_bytes": doc["content"]}
            )

        tasks = [_parse(doc) for doc in documents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        parsed = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                self._record_error(state, f"DocumentParsingNode::{documents[idx]['filename']}", result)
                continue
            parsed.append(result)
            self._track_usage(state, "DocumentParserAgent", result)

        state["parsed_documents"] = parsed
        state["documents_ready"] = True
        await self._set_stage("parsing", 35)
        return state

    async def _diagram_parsing(self, state: QuickAssessState) -> QuickAssessState:
        diagrams = state.get("diagrams_buffer", [])
        if not diagrams:
            state["diagrams_ready"] = True
            return state

        async def _parse(diagram):
            return await self.diagram_agent.execute(
                {"diagram_name": diagram["filename"], "file_bytes": diagram["content"]}
            )

        tasks = [_parse(diagram) for diagram in diagrams]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        parsed = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                self._record_error(state, f"DiagramParsingNode::{diagrams[idx]['filename']}", result)
                continue
            parsed.append(result)
            self._track_usage(state, "DiagramParserAgent", result)

        state["parsed_diagrams"] = parsed
        state["diagrams_ready"] = True
        await self._set_stage("parsing", 40)
        return state

    async def _analysis(self, state: QuickAssessState) -> QuickAssessState:
        await self._set_stage("analysis", 60)
        analysis = await self.analysis_agent.execute(
            {
                "documents": state.get("parsed_documents", []),
                "diagrams": state.get("parsed_diagrams", []),
            }
        )
        state["analysis_results"] = analysis
        self._track_usage(state, "EnvironmentAnalysisAgent", analysis)
        return state

    async def _report_generation(self, state: QuickAssessState) -> QuickAssessState:
        await self._set_stage("report", 85)
        report_result = await self.report_agent.execute(
            {
                "analysis_results": state.get("analysis_results", {}),
                "project_id": state.get("project_id"),
            }
        )
        state["report"] = report_result.get("report", {})
        state["report_url"] = report_result.get("pdf_s3_uri")
        state["report_json_url"] = report_result.get("json_s3_uri")
        state["report_base64"] = report_result.get("pdf_base64")  # type: ignore[assignment]
        self._track_usage(state, "ReportGenerationAgent", report_result.get("report", {}))
        return state

    async def _notification(self, state: QuickAssessState) -> QuickAssessState:
        await self._set_stage("completed", 100)
        await self._update_status(
            "completed",
            {
                "report_url": state.get("report_url"),
                "report_json_url": state.get("report_json_url"),
            },
        )
        await eventbridge_client.publish_event(
            source="workflow.quickassess",
            detail_type="quick_assess.completed",
            detail={
                "assessment_id": self.assessment_id,
                "report_url": state.get("report_url"),
                "status": state.get("status", "completed"),
            },
        )
        return state

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _wrap_node(self, node_name: str, func):
        async def wrapper(state: QuickAssessState) -> QuickAssessState:
            metrics = WorkflowMetrics(node=node_name, started_at=time.perf_counter())
            try:
                result = await self._with_retry(func, state, node_name, metrics)
                metrics.duration_ms = (time.perf_counter() - metrics.started_at) * 1000
                self._log_metrics(metrics)
                return result
            except Exception as exc:
                metrics.duration_ms = (time.perf_counter() - metrics.started_at) * 1000
                metrics.success = False
                metrics.error = str(exc)
                self._log_metrics(metrics)
                self._record_error(state, node_name, exc)
                state["status"] = "failed"
                raise

        return wrapper

    async def _with_retry(self, func, state: QuickAssessState, node_name: str, metrics: WorkflowMetrics):
        last_exc = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return await func(state)
            except Exception as exc:
                last_exc = exc
                metrics.retries = attempt
                logger.warning("%s failed (attempt %s/%s): %s", node_name, attempt, self.max_retries, exc)
                await asyncio.sleep(min(2 ** attempt, 5))
        raise last_exc  # type: ignore[misc]

    def _analysis_gate(self, state: QuickAssessState) -> QuickAssessState:
        # Increment retry counter to prevent infinite loops
        retries = state.get("gate_retries", 0)
        state["gate_retries"] = retries + 1
        return state

    def _gate_condition(self, state: QuickAssessState) -> str:
        if state.get("documents_ready") and state.get("diagrams_ready"):
            return "ready"
        return "wait"

    def _record_error(self, state: QuickAssessState, context: str, error: Exception) -> None:
        message = f"{context}: {error}"
        logger.error(message)
        errors = state.setdefault("error_messages", [])
        errors.append(message)
        asyncio.create_task(self._write_error_log(message))

    async def _write_error_log(self, message: str) -> None:
        table = getattr(settings, "DYNAMODB_QUICK_ASSESS_ERRORS_TABLE", None)
        if not table:
            return
        try:
            await dynamodb_client.put_item(
                table,
                {
                    "assessment_id": self.assessment_id,
                    "timestamp": _now_ms(),
                    "message": message,
                },
            )
        except Exception as exc:
            logger.warning("Failed to write error log: %s", exc)

    def _log_metrics(self, metrics: WorkflowMetrics) -> None:
        logger.info(
            "Node %s finished in %.2f ms (success=%s, retries=%s)",
            metrics.node,
            metrics.duration_ms or 0.0,
            metrics.success,
            metrics.retries,
        )

    async def _update_status(self, status: Optional[str], extra: Optional[Dict[str, Any]] = None) -> None:
        try:
            update_parts = ["updated_at = :ts"]
            expression_values = {
                ":ts": time.time(),
            }
            expression_names: Dict[str, str] = {}
            if status is not None:
                expression_names["#s"] = "status"
                expression_values[":status"] = status
                update_parts.append("#s = :status")
            if extra:
                for idx, (key, value) in enumerate(extra.items()):
                    placeholder = f"#f{idx}"
                    value_placeholder = f":v{idx}"
                    expression_names[placeholder] = key
                    expression_values[value_placeholder] = value
                    update_parts.append(f"{placeholder} = {value_placeholder}")

            await dynamodb_client.update_item(
                settings.DYNAMODB_QUICK_ASSESS_TABLE,
                {"assessment_id": self.assessment_id},
                "SET " + ", ".join(update_parts),
                expression_values,
                expression_names or None,
            )
        except Exception as exc:
            logger.warning("Failed to update status: %s", exc)

    async def _set_stage(self, stage: str, progress: int) -> None:
        await self._update_status(
            None,
            {
                "stage": stage,
                "progress": progress,
            },
        )

    def _track_usage(self, state: QuickAssessState, agent_name: str, result: Dict[str, Any]) -> None:
        usage = result.get("usage") if isinstance(result, dict) else None
        if not isinstance(usage, dict):
            return
        tokens = usage.get("total_tokens") or usage.get("output_tokens")
        if not tokens:
            return
        token_map = state.setdefault("token_usage", {})
        token_map[agent_name] = token_map.get(agent_name, 0) + tokens

