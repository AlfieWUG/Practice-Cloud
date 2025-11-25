"""Quick Assess API endpoints."""
from __future__ import annotations

import asyncio
import base64
import json
import logging
from io import BytesIO
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse

# Import workflow with fallback for missing dependencies
try:
    from agentic_services.orchestrator.quick_assess_workflow import QuickAssessWorkflow
    WORKFLOW_AVAILABLE = True
except ImportError as e:
    logger.warning(f"QuickAssessWorkflow not available: {e}. Workflow execution will be disabled.")
    WORKFLOW_AVAILABLE = False
    QuickAssessWorkflow = None
from app.dependencies.security import AuthenticatedUser, get_current_user
from app.schemas.quick_assess import (
    AssessmentListItem,
    AssessmentListResponse,
    AssessmentResultResponse,
    AssessmentStatusResponse,
    QuickAssessUploadResponse,
    ShareLinkResponse,
    WorkflowLaunchResponse,
)
from app.services.quick_assess import (
    FileTooLargeError,
    InvalidFileTypeError,
    MetadataWriteError,
    QuickAssessService,
    StorageUploadError,
)

logger = logging.getLogger(__name__)

MAX_FILES_PER_REQUEST = 10
STAGE_PROGRESS = {
    "ingestion": 15,
    "parsing": 35,
    "analysis": 65,
    "report": 85,
    "completed": 100,
}
STAGE_ETA = {
    "ingestion": 240,
    "parsing": 180,
    "analysis": 120,
    "report": 60,
    "completed": 0,
}


router = APIRouter(prefix="/quick-assess", tags=["quick-assess"])


def get_quick_assess_service() -> QuickAssessService:
    if not hasattr(get_quick_assess_service, "_service"):
        get_quick_assess_service._service = QuickAssessService()  # type: ignore[attr-defined]
    return get_quick_assess_service._service  # type: ignore[attr-defined]


def _http_error(status_code: int, code: str, message: str) -> None:
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )


def _encode_token(key: Dict[str, Any]) -> str:
    return base64.urlsafe_b64encode(json.dumps(key).encode("utf-8")).decode("utf-8")


def _decode_token(token: str) -> Dict[str, Any]:
    return json.loads(base64.urlsafe_b64decode(token.encode("utf-8")))


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=QuickAssessUploadResponse,
)
async def upload_assessment_files(
    files: List[UploadFile] = File(..., description="Assessment documents"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: QuickAssessService = Depends(get_quick_assess_service),
) -> QuickAssessUploadResponse:
    if not files:
        _http_error(status.HTTP_400_BAD_REQUEST, "validation_error", "At least one file is required")
    if len(files) > MAX_FILES_PER_REQUEST:
        _http_error(
            status.HTTP_400_BAD_REQUEST,
            "validation_error",
            f"You can upload up to {MAX_FILES_PER_REQUEST} files per request",
        )

    try:
        result = await service.create_assessment(files, current_user.user_id)
    except InvalidFileTypeError as exc:
        logger.error(f"Invalid file type: {exc}")
        _http_error(status.HTTP_400_BAD_REQUEST, "invalid_file_type", str(exc))
    except FileTooLargeError as exc:
        logger.error(f"File too large: {exc}")
        _http_error(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "file_too_large", str(exc))
    except StorageUploadError as exc:
        logger.error(f"Storage upload error: {exc}", exc_info=True)
        _http_error(status.HTTP_502_BAD_GATEWAY, "storage_error", str(exc))
    except MetadataWriteError as exc:
        logger.error(f"Metadata write error: {exc}", exc_info=True)
        _http_error(status.HTTP_503_SERVICE_UNAVAILABLE, "metadata_error", str(exc))
    except Exception as exc:
        logger.exception(f"Unexpected error during upload: {exc}")
        _http_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "internal_error",
            f"An unexpected error occurred: {str(exc)}"
        )

    return QuickAssessUploadResponse(**result)


@router.post(
    "/{assessment_id}/execute",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=WorkflowLaunchResponse,
)
async def execute_assessment(
    assessment_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: QuickAssessService = Depends(get_quick_assess_service),
) -> WorkflowLaunchResponse:
    try:
        record = await service.get_assessment(assessment_id)
        if not record:
            _http_error(status.HTTP_404_NOT_FOUND, "not_found", "Assessment not found")
        if record.get("user_id") != current_user.user_id:
            _http_error(status.HTTP_403_FORBIDDEN, "forbidden", "You do not have access to this assessment")

        if not WORKFLOW_AVAILABLE:
            _http_error(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "workflow_unavailable",
                "QuickAssess workflow is not available. Required dependencies may be missing. "
                "Install: pip install pdfplumber python-docx langgraph"
            )
        
        try:
            workflow = QuickAssessWorkflow(
                assessment_id=assessment_id,
                project_id=record.get("project_id"),
            )
        except Exception as exc:
            logger.exception(f"Failed to initialize QuickAssessWorkflow: {exc}")
            _http_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "workflow_init_error",
                f"Failed to initialize workflow: {str(exc)}"
            )

        async def _run():
            try:
                await workflow.run()
            except Exception:
                logger.exception("QuickAssess workflow failed for %s", assessment_id)
                await service.update_status(
                    assessment_id,
                    status="failed",
                    extra={"stage": "workflow_error", "error": "Workflow execution failed"}
                )

        asyncio.create_task(_run())
        await service.update_status(assessment_id, status="processing", extra={"stage": "ingestion"})

        return WorkflowLaunchResponse(
            assessment_id=assessment_id,
            workflow_id=getattr(workflow, "workflow_id", f"wf-{assessment_id}"),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error in execute_assessment: {exc}")
        _http_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "internal_error",
            f"An unexpected error occurred: {str(exc)}"
        )


@router.get(
    "/{assessment_id}/status",
    response_model=AssessmentStatusResponse,
)
async def get_assessment_status(
    assessment_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: QuickAssessService = Depends(get_quick_assess_service),
) -> AssessmentStatusResponse:
    record = await service.get_assessment(assessment_id)
    if not record:
        _http_error(status.HTTP_404_NOT_FOUND, "not_found", "Assessment not found")
    if record.get("user_id") != current_user.user_id:
        _http_error(status.HTTP_403_FORBIDDEN, "forbidden", "You do not have access to this assessment")

    stage = record.get("stage", "ingestion")
    progress = int(record.get("progress") or STAGE_PROGRESS.get(stage, 10))
    eta = STAGE_ETA.get(stage)
    files = record.get("files", [])

    return AssessmentStatusResponse(
        assessment_id=assessment_id,
        status=record.get("status", "processing"),
        stage=stage,
        progress=progress,
        estimated_seconds_remaining=eta,
        files=[{"filename": f["filename"], "status": f.get("status", "pending"), "message": f.get("message")} for f in files],
        error_messages=record.get("errors", []),
        report_url=record.get("report_url"),
        report_json_url=record.get("report_json_url"),
    )


@router.get(
    "/{assessment_id}/results",
    response_model=AssessmentResultResponse,
)
async def get_assessment_results(
    assessment_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: QuickAssessService = Depends(get_quick_assess_service),
) -> AssessmentResultResponse:
    record = await service.get_assessment(assessment_id)
    if not record:
        _http_error(status.HTTP_404_NOT_FOUND, "not_found", "Assessment not found")
    if record.get("user_id") != current_user.user_id:
        _http_error(status.HTTP_403_FORBIDDEN, "forbidden", "You do not have access to this assessment")
    if record.get("status") != "completed":
        _http_error(status.HTTP_409_CONFLICT, "not_ready", "Assessment has not finished yet")

    report_json_url = record.get("report_json_url")
    results = {}
    if report_json_url:
        try:
            results = await service.get_report_json(report_json_url)
        except Exception as exc:
            logger.warning("Failed to load report JSON: %s", exc)

    return AssessmentResultResponse(
        assessment_id=assessment_id,
        status=record.get("status", "completed"),
        report_url=record.get("report_url"),
        report_json_url=report_json_url,
        results=results,
    )


@router.get("/{assessment_id}/report")
async def download_report(
    assessment_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: QuickAssessService = Depends(get_quick_assess_service),
):
    record = await service.get_assessment(assessment_id)
    if not record:
        _http_error(status.HTTP_404_NOT_FOUND, "not_found", "Assessment not found")
    if record.get("user_id") != current_user.user_id:
        _http_error(status.HTTP_403_FORBIDDEN, "forbidden", "You do not have access to this assessment")

    report_url = record.get("report_url")
    if not report_url:
        _http_error(status.HTTP_404_NOT_FOUND, "not_found", "Report not available yet")

    content, content_type = await service.get_report_stream(report_url)
    return StreamingResponse(
        BytesIO(content),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{assessment_id}-quick-assess-report.pdf"'
        },
    )


@router.get(
    "/list",
    response_model=AssessmentListResponse,
)
async def list_assessments(
    limit: int = Query(20, ge=1, le=100),
    page_token: Optional[str] = Query(None, description="Pagination token"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: QuickAssessService = Depends(get_quick_assess_service),
) -> AssessmentListResponse:
    last_key = None
    if page_token:
        try:
            last_key = _decode_token(page_token)
        except Exception:
            _http_error(status.HTTP_400_BAD_REQUEST, "invalid_token", "Invalid pagination token")

    try:
        response = await service.list_assessments(current_user.user_id, limit=limit, last_key=last_key)
    except Exception as e:
        logger.error(f"Failed to list assessments: {e}", exc_info=True)
        # Return empty list if table doesn't exist or other error
        return AssessmentListResponse(items=[], next_token=None)
    
    items = [
        AssessmentListItem(
            assessment_id=item["assessment_id"],
            status=item.get("status", "processing"),
            stage=item.get("stage"),
            progress=item.get("progress"),
            upload_time=item.get("upload_time"),
        )
        for item in response.get("items", [])
    ]

    next_token = None
    if response.get("last_evaluated_key"):
        next_token = _encode_token(response["last_evaluated_key"])

    return AssessmentListResponse(items=items, next_token=next_token)


@router.post(
    "/{assessment_id}/share",
    response_model=ShareLinkResponse,
)
async def share_assessment_report(
    assessment_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: QuickAssessService = Depends(get_quick_assess_service),
) -> ShareLinkResponse:
    record = await service.get_assessment(assessment_id)
    if not record:
        _http_error(status.HTTP_404_NOT_FOUND, "not_found", "Assessment not found")
    if record.get("user_id") != current_user.user_id:
        _http_error(status.HTTP_403_FORBIDDEN, "forbidden", "You do not have access to this assessment")
    if not record.get("report_url"):
        _http_error(status.HTTP_404_NOT_FOUND, "not_found", "Report not available yet")

    share_url = record["report_url"]
    return ShareLinkResponse(assessment_id=assessment_id, share_url=share_url)
