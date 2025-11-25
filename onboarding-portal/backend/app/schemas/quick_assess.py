"""Schemas for Quick Assess feature."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class UploadedAssessmentFile(BaseModel):
    """Details about an uploaded assessment file."""

    filename: str = Field(..., description="Original file name")
    size_bytes: int = Field(..., description="Size of the uploaded file in bytes")


class QuickAssessUploadResponse(BaseModel):
    """Response returned after uploading assessment files."""

    assessment_id: str = Field(..., description="Generated assessment identifier")
    status: str = Field(default="uploaded", description="Current processing status")
    files: List[UploadedAssessmentFile]


class WorkflowLaunchResponse(BaseModel):
    """Response for workflow execution trigger."""

    assessment_id: str
    workflow_id: str
    status: str = Field(default="processing")


class AssessmentFileStatus(BaseModel):
    filename: str
    status: str
    message: Optional[str] = None


class AssessmentStatusResponse(BaseModel):
    assessment_id: str
    status: str
    stage: str
    progress: int = Field(ge=0, le=100)
    estimated_seconds_remaining: Optional[int] = None
    files: List[AssessmentFileStatus] = []
    error_messages: List[str] = []
    report_url: Optional[str] = None
    report_json_url: Optional[str] = None


class AssessmentResultResponse(BaseModel):
    assessment_id: str
    status: str
    report_url: Optional[str]
    report_json_url: Optional[str]
    results: Dict[str, Any]


class AssessmentListItem(BaseModel):
    assessment_id: str
    status: str
    stage: Optional[str] = None
    progress: Optional[int] = None
    upload_time: Optional[str] = None


class AssessmentListResponse(BaseModel):
    items: List[AssessmentListItem]
    next_token: Optional[str] = None


class ShareLinkResponse(BaseModel):
    assessment_id: str
    share_url: str

