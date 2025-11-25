"""
Quick Assess API Client for Streamlit
Handles all API calls to the FastAPI backend.
"""
import os
import requests
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Get API base URL from environment or default to localhost
API_BASE_URL = os.getenv("QUICK_ASSESS_API_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("QUICK_ASSESS_API_KEY", "demo-key")


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


def get_client() -> QuickAssessClient:
    """Get or create the global Quick Assess client."""
    global _client
    if _client is None:
        _client = QuickAssessClient()
    return _client

