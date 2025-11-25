"""
Agents API endpoints for executing and monitoring agents.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.project import AgentExecution, MigrationPhase, AgentExecutionStatus
from app.schemas.project import (
    AgentExecutionCreate,
    AgentExecutionUpdate,
    AgentExecutionResponse
)
from app.services.agent_executor import AgentExecutorService

router = APIRouter(prefix="/agents", tags=["agents"])


# List of all 24 agents organized by phase
AGENTS_BY_PHASE = {
    "discovery": [
        "infrastructure_scanner",
        "application_profiler",
        "data_discovery",
        "network_topology_mapper",
        "license_auditor",
        "technical_debt_analyzer",
        "api_catalog_builder",
        "integration_discovery"
    ],
    "assessment": [
        "dependency_mapper",
        "compliance_checker",
        "security_hardening",
        "cost_estimator",
        "data_classifier"
    ],
    "execution": [
        "infrastructure_provisioner",
        "application_migration",
        "data_migration",
        "cutover_coordinator",
        "rollback_manager",
        "validation_tester"
    ],
    "optimization": [
        "performance_monitor",
        "cost_optimizer",
        "security_validator",
        "compliance_auditor",
        "documentation_generator"
    ]
}


@router.get("", response_model=Dict[str, List[str]])
def list_agents():
    """List all 24 available agents organized by phase."""
    return AGENTS_BY_PHASE


@router.get("/phases", response_model=List[str])
def list_phases():
    """List all migration phases."""
    return ["discovery", "assessment", "execution", "optimization"]


@router.post("/{agent_name}/execute", response_model=AgentExecutionResponse, status_code=202)
async def execute_agent(
    agent_name: str,
    execution: AgentExecutionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Execute a specific agent asynchronously.
    
    This creates an agent execution record and starts the agent in the background.
    """
    # Validate agent name
    all_agents = [agent for agents in AGENTS_BY_PHASE.values() for agent in agents]
    if agent_name not in all_agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    # Create execution record
    db_execution = AgentExecution(
        project_id=execution.project_id,
        agent_name=agent_name,
        phase=execution.phase,
        status=AgentExecutionStatus.QUEUED
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    
    # Start agent execution in background
    executor = AgentExecutorService()
    background_tasks.add_task(
        executor.execute_agent,
        db_execution.id,
        agent_name,
        execution.project_id
    )
    
    return db_execution


@router.post("/bulk-execute", response_model=List[AgentExecutionResponse], status_code=202)
async def bulk_execute_agents(
    project_id: UUID,
    phase: MigrationPhase,
    agent_names: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Execute multiple agents for a phase.
    
    This is useful for running all agents in a phase at once.
    """
    executions = []
    
    for agent_name in agent_names:
        # Validate agent
        if phase.value not in AGENTS_BY_PHASE or agent_name not in AGENTS_BY_PHASE[phase.value]:
            raise HTTPException(
                status_code=400,
                detail=f"Agent '{agent_name}' not valid for phase '{phase.value}'"
            )
        
        # Create execution record
        db_execution = AgentExecution(
            project_id=project_id,
            agent_name=agent_name,
            phase=phase,
            status=AgentExecutionStatus.QUEUED
        )
        db.add(db_execution)
        executions.append(db_execution)
    
    db.commit()
    
    # Start all agents in background
    executor = AgentExecutorService()
    for execution in executions:
        background_tasks.add_task(
            executor.execute_agent,
            execution.id,
            execution.agent_name,
            project_id
        )
    
    return executions


@router.get("/{agent_name}/status/{execution_id}", response_model=AgentExecutionResponse)
def get_agent_status(
    agent_name: str,
    execution_id: UUID,
    db: Session = Depends(get_db)
):
    """Get the status of a specific agent execution."""
    execution = db.query(AgentExecution).filter(
        AgentExecution.id == execution_id,
        AgentExecution.agent_name == agent_name
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Agent execution not found")
    
    return execution


@router.put("/executions/{execution_id}", response_model=AgentExecutionResponse)
def update_agent_execution(
    execution_id: UUID,
    update: AgentExecutionUpdate,
    db: Session = Depends(get_db)
):
    """Update an agent execution (for internal use / webhooks)."""
    execution = db.query(AgentExecution).filter(
        AgentExecution.id == execution_id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    update_data = update.model_dump(exclude_unset=True)
    
    # Update timestamps based on status changes
    if "status" in update_data:
        if update_data["status"] == AgentExecutionStatus.RUNNING and not execution.started_at:
            execution.started_at = datetime.utcnow()
        elif update_data["status"] in [AgentExecutionStatus.COMPLETED, AgentExecutionStatus.FAILED]:
            execution.completed_at = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(execution, field, value)
    
    db.commit()
    db.refresh(execution)
    return execution


@router.get("/executions/project/{project_id}", response_model=List[AgentExecutionResponse])
def get_project_executions(
    project_id: UUID,
    phase: Optional[MigrationPhase] = None,
    status: Optional[AgentExecutionStatus] = None,
    db: Session = Depends(get_db)
):
    """Get all agent executions for a project with optional filtering."""
    query = db.query(AgentExecution).filter(AgentExecution.project_id == project_id)
    
    if phase:
        query = query.filter(AgentExecution.phase == phase)
    
    if status:
        query = query.filter(AgentExecution.status == status)
    
    return query.all()
