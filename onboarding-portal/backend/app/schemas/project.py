"""
Pydantic schemas for Project, AgentExecution, and Artifact.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.project import (
    ProjectStatus,
    MigrationPhase,
    AgentExecutionStatus,
    ArtifactType
)


# Project Schemas
class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    requirements: Optional[str] = None
    target_cloud: str = Field(default="aws", max_length=50)


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    customer_id: UUID


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    requirements: Optional[str] = None
    status: Optional[ProjectStatus] = None
    current_phase: Optional[MigrationPhase] = None
    progress: Optional[int] = Field(None, ge=0, le=100)


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: UUID
    customer_id: UUID
    status: ProjectStatus
    current_phase: Optional[MigrationPhase]
    progress: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# AgentExecution Schemas
class AgentExecutionCreate(BaseModel):
    """Schema for creating an agent execution."""
    project_id: UUID
    agent_name: str = Field(..., min_length=1, max_length=100)
    phase: MigrationPhase


class AgentExecutionUpdate(BaseModel):
    """Schema for updating agent execution."""
    status: Optional[AgentExecutionStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    result: Optional[dict] = None
    error: Optional[str] = None


class AgentExecutionResponse(BaseModel):
    """Schema for agent execution response."""
    id: UUID
    project_id: UUID
    agent_name: str
    phase: MigrationPhase
    status: AgentExecutionStatus
    progress: int
    result: Optional[dict]
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Artifact Schemas
class ArtifactCreate(BaseModel):
    """Schema for creating an artifact."""
    project_id: UUID
    agent_execution_id: Optional[UUID] = None
    artifact_type: ArtifactType
    file_name: str = Field(..., min_length=1, max_length=255)
    s3_url: str = Field(..., max_length=512)
    size_bytes: Optional[int] = None


class ArtifactResponse(BaseModel):
    """Schema for artifact response."""
    id: UUID
    project_id: UUID
    agent_execution_id: Optional[UUID]
    artifact_type: ArtifactType
    file_name: str
    s3_url: str
    size_bytes: Optional[int]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Composite Schemas
class ProjectWithExecutions(ProjectResponse):
    """Project with agent executions."""
    agent_executions: List[AgentExecutionResponse] = []
    artifacts: List[ArtifactResponse] = []


# Pagination
class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
