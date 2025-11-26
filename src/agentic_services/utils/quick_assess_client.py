"""
Quick Assess API Client for Streamlit
Handles all API calls to the FastAPI backend.
"""
import os
import logging
import uuid
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests
import streamlit as st

from agentic_services.config.settings import settings

logger = logging.getLogger(__name__)

# Get API base URL from environment or default to localhost
API_BASE_URL = os.getenv("QUICK_ASSESS_API_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("QUICK_ASSESS_API_KEY", "demo-key")


_demo_state: Dict[str, Any] = {
    "assessments": {
        "demo-abc12345": {
            "assessment_id": "demo-abc12345",
            "files": [
                {"filename": "architecture-diagram.drawio", "size_mb": 2.5, "content_type": "application/xml"},
                {"filename": "infrastructure-doc.docx", "size_mb": 1.8, "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
            ],
            "status": "completed",
            "stage": "analysis",
            "progress": 100,
            "created_at": "2025-01-26T10:30:00Z",
            "workflow_id": "demo-wf-xyz789",
            "results": None,
        },
        "demo-def67890": {
            "assessment_id": "demo-def67890",
            "files": [
                {"filename": "cloud-readiness.pdf", "size_mb": 3.2, "content_type": "application/pdf"},
            ],
            "status": "processing",
            "stage": "parsing",
            "progress": 65,
            "created_at": "2025-01-26T11:15:00Z",
            "workflow_id": "demo-wf-abc456",
            "results": None,
        },
    }
}


class QuickAssessClient:
    """Client for Quick Assess API endpoints."""
    
    def __init__(self, base_url: str = API_BASE_URL, api_key: str = API_KEY, user_id: str = "quick-assess-user"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "X-User-Id": user_id,
        }
    
    def upload_files(self, files: List[Any]) -> Dict[str, Any]:
        """
        Upload files for assessment.
        
        Args:
            files: List of Streamlit UploadedFile objects or file-like objects
            
        Returns:
            Dict with assessment_id and file details
        """
        url = f"{self.base_url}/quick-assess/upload"
        
        # Prepare multipart form data
        file_data = []
        for f in files:
            file_data.append(("files", (f.name, f.read(), f.type)))
        
        try:
            response = requests.post(
                url,
                files=file_data,
                headers=self.headers,
                timeout=300  # 5 minutes for large uploads
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Upload failed: {e}")
            raise
    
    def execute_assessment(self, assessment_id: str) -> Dict[str, Any]:
        """
        Execute assessment workflow.
        
        Args:
            assessment_id: The assessment ID from upload
            
        Returns:
            Dict with workflow_id
        """
        url = f"{self.base_url}/quick-assess/{assessment_id}/execute"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Execute failed: {e}")
            raise
    
    def get_status(self, assessment_id: str) -> Dict[str, Any]:
        """
        Get assessment status.
        
        Args:
            assessment_id: The assessment ID
            
        Returns:
            Dict with status, progress, stage, etc.
        """
        url = f"{self.base_url}/quick-assess/{assessment_id}/status"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Status check failed: {e}")
            raise
    
    def get_results(self, assessment_id: str) -> Dict[str, Any]:
        """
        Get assessment results.
        
        Args:
            assessment_id: The assessment ID
            
        Returns:
            Dict with analysis results, report_url, etc.
        """
        url = f"{self.base_url}/quick-assess/{assessment_id}/results"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Results fetch failed: {e}")
            raise
    
    def download_report(self, assessment_id: str) -> bytes:
        """
        Download PDF report.
        
        Args:
            assessment_id: The assessment ID
            
        Returns:
            PDF file bytes
        """
        url = f"{self.base_url}/quick-assess/{assessment_id}/report"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=60,
                stream=True
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Report download failed: {e}")
            raise
    
    def list_assessments(self, limit: int = 20, last_key: Optional[str] = None) -> Dict[str, Any]:
        """
        List assessments.
        
        Args:
            limit: Maximum number of assessments to return
            last_key: Pagination token
            
        Returns:
            Dict with assessments list and pagination info
        """
        url = f"{self.base_url}/quick-assess/list"
        params = {"limit": limit}
        if last_key:
            params["last_key"] = last_key
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"List assessments failed: {e}")
            raise


# Global client instance
_client: Optional[QuickAssessClient] = None


class QuickAssessDemoClient:
    """Offline-friendly mock client used when DEMO_MODE=true."""

    def __init__(self):
        self.state = _demo_state

    def _ensure_assessment(self, assessment_id: str) -> Dict[str, Any]:
        assessment = self.state["assessments"].get(assessment_id)
        if not assessment:
            raise ValueError(f"Unknown assessment_id {assessment_id}")
        return assessment

    def _generate_results(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        from demo.demo_data import QUICK_ASSESS_RESULTS

        results = deepcopy(QUICK_ASSESS_RESULTS)
        results["assessment_id"] = assessment["assessment_id"]
        results["summary"]["documents_processed"] = len(assessment["files"])
        results["files"] = assessment["files"]
        results["generated_at"] = datetime.utcnow().isoformat() + "Z"
        return results

    def upload_files(self, files: List[Any]) -> Dict[str, Any]:
        assessment_id = f"demo-{uuid.uuid4().hex[:8]}"
        stored_files = []
        for f in files:
            content = f.read()
            size_mb = round(len(content) / (1024 * 1024), 2)
            stored_files.append(
                {
                    "filename": f.name,
                    "size_mb": size_mb,
                    "content_type": getattr(f, "type", "application/octet-stream"),
                }
            )
            f.seek(0)

        created_at = datetime.utcnow().isoformat() + "Z"
        self.state["assessments"][assessment_id] = {
            "assessment_id": assessment_id,
            "files": stored_files,
            "status": "uploaded",
            "stage": "ingestion",
            "progress": 5,
            "created_at": created_at,
            "workflow_id": None,
            "results": None,
        }
        return {"assessment_id": assessment_id, "files": stored_files, "created_at": created_at}

    def execute_assessment(self, assessment_id: str) -> Dict[str, Any]:
        assessment = self._ensure_assessment(assessment_id)
        workflow_id = f"demo-wf-{uuid.uuid4().hex[:6]}"
        assessment.update(
            {
                "status": "completed",
                "stage": "analysis",
                "progress": 100,
                "workflow_id": workflow_id,
                "completed_at": datetime.utcnow().isoformat() + "Z",
                "results": self._generate_results(assessment),
            }
        )
        return {"workflow_id": workflow_id}

    def get_status(self, assessment_id: str) -> Dict[str, Any]:
        assessment = self._ensure_assessment(assessment_id)
        return {
            "assessment_id": assessment_id,
            "status": assessment["status"],
            "stage": assessment["stage"],
            "progress": assessment["progress"],
            "completed_at": assessment.get("completed_at"),
            "error": None,
        }

    def get_results(self, assessment_id: str) -> Dict[str, Any]:
        assessment = self._ensure_assessment(assessment_id)
        if not assessment["results"]:
            assessment["results"] = self._generate_results(assessment)
        return assessment["results"]

    def download_report(self, assessment_id: str) -> bytes:
        assessment = self._ensure_assessment(assessment_id)
        report_text = f"Demo report for {assessment_id}\n\nFiles:\n"
        for f in assessment["files"]:
            report_text += f"- {f['filename']} ({f['size_mb']} MB)\n"
        report_text += "\nGenerated via demo mode – no sensitive data."
        return report_text.encode("utf-8")

    def list_assessments(self, limit: int = 20, last_key: Optional[str] = None) -> Dict[str, Any]:
        assessments = list(self.state["assessments"].values())
        assessments.sort(key=lambda a: a["created_at"], reverse=True)
        return {
            "assessments": assessments[:limit],
            "last_key": last_key,
        }


def get_client() -> Union[QuickAssessClient, QuickAssessDemoClient]:
    """Get or create the global Quick Assess client."""
    global _client
    if _client is None:
        # Check DEMO_MODE from Streamlit secrets first (for Streamlit Cloud), then environment, then settings
        demo_mode = False
        try:
            if hasattr(st, "secrets"):
                demo_mode = st.secrets.get("DEMO_MODE", "false").lower() == "true"
        except (RuntimeError, AttributeError, KeyError):
            pass
        
        if not demo_mode:
            demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        
        if not demo_mode:
            demo_mode = settings.DEMO_MODE
        
        if demo_mode:
            logger.info("Quick Assess client running in DEMO_MODE - using mock data")
            _client = QuickAssessDemoClient()
        else:
            _client = QuickAssessClient()
    return _client

