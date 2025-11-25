"""
Agent Executor Service - communicates with the main agentic-services platform.
"""
import asyncio
import httpx
from uuid import UUID
from typing import Dict, Any
from datetime import datetime

from app.config import settings
from app.database import SessionLocal
from app.models.project import AgentExecution, AgentExecutionStatus


class AgentExecutorService:
    """Service for executing agents via the main agentic-services platform."""
    
    def __init__(self):
        self.api_endpoint = settings.agentic_services_api_endpoint
        self.demo_mode = settings.demo_mode
    
    async def execute_agent(
        self,
        execution_id: UUID,
        agent_name: str,
        project_id: UUID
    ):
        """
        Execute an agent by calling the main platform API.
        
        In demo mode, this simulates agent execution.
        In production, this calls the actual Lambda/API Gateway endpoint.
        """
        db = SessionLocal()
        
        try:
            # Update status to running
            execution = db.query(AgentExecution).filter(
                AgentExecution.id == execution_id
            ).first()
            
            if not execution:
                return
            
            execution.status = AgentExecutionStatus.RUNNING
            execution.started_at = datetime.utcnow()
            execution.progress = 0
            db.commit()
            
            if self.demo_mode:
                # Demo mode: simulate execution
                result = await self._simulate_agent_execution(agent_name, project_id)
            else:
                # Production: call actual API
                result = await self._call_agent_api(agent_name, project_id, execution_id)
            
            # Update with results
            execution.status = AgentExecutionStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.progress = 100
            execution.result = result
            db.commit()
            
        except Exception as e:
            # Handle errors
            execution.status = AgentExecutionStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error = str(e)
            db.commit()
        
        finally:
            db.close()
    
    async def _simulate_agent_execution(
        self,
        agent_name: str,
        project_id: UUID
    ) -> Dict[str, Any]:
        """Simulate agent execution for demo mode."""
        # Simulate processing time
        await asyncio.sleep(5)
        
        return {
            "agent": agent_name,
            "project_id": str(project_id),
            "status": "completed",
            "demo_mode": True,
            "message": f"Demo execution of {agent_name} completed successfully",
            "artifacts": [
                {
                    "type": "report",
                    "name": f"{agent_name}_report.pdf",
                    "url": f"s3://demo-bucket/{agent_name}_report.pdf"
                }
            ]
        }
    
    async def _call_agent_api(
        self,
        agent_name: str,
        project_id: UUID,
        execution_id: UUID
    ) -> Dict[str, Any]:
        """Call the main platform API to execute an agent."""
        if not self.api_endpoint:
            raise ValueError("AGENTIC_SERVICES_API_ENDPOINT not configured")
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.api_endpoint}/agents/{agent_name}/execute",
                json={
                    "project_id": str(project_id),
                    "execution_id": str(execution_id)
                }
            )
            response.raise_for_status()
            return response.json()
