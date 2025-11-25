"""
Projects API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.project import Project, AgentExecution, Artifact
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithExecutions,
    PaginatedResponse
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """Create a new migration project."""
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    customer_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all projects with optional filtering."""
    query = db.query(Project)
    
    if customer_id:
        query = query.filter(Project.customer_id == customer_id)
    
    if status:
        query = query.filter(Project.status == status)
    
    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectWithExecutions)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific project with agent executions and artifacts."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update a project."""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update fields
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a project."""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return None


@router.get("/{project_id}/executions", response_model=List)
def get_project_executions(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all agent executions for a project."""
    executions = db.query(AgentExecution).filter(
        AgentExecution.project_id == project_id
    ).all()
    
    return executions


@router.get("/{project_id}/artifacts", response_model=List)
def get_project_artifacts(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all artifacts for a project."""
    artifacts = db.query(Artifact).filter(
        Artifact.project_id == project_id
    ).all()
    
    return artifacts
