import asyncio
from io import BytesIO

import pytest
from fastapi import status
from httpx import AsyncClient

from main import app
from app.api import quick_assess as api_module
from app.api.quick_assess import get_quick_assess_service
from app.config import settings
from app.dependencies.security import AuthenticatedUser, get_current_user
from app.services.quick_assess import FileTooLargeError, InvalidFileTypeError
from .sample_data import sample_docx_bytes, sample_vsdx_bytes

fake_service: "FakeQuickAssessService | None" = None

API_KEY = "test-api-key"


class FakeQuickAssessService:
    def __init__(self):
        self.assessments: dict[str, dict] = {}
        self.counter = 0

    async def create_assessment(self, files, user_id: str):
        self.counter += 1
        assessment_id = f"qa-fake-{self.counter}"
        stored_files = []
        for upload in files:
            filename = upload.filename or "file"
            if not filename.lower().endswith((".docx", ".pdf", ".vsdx", ".drawio", ".xml")):
                raise InvalidFileTypeError("File type not allowed")
            data = await upload.read()
            size = len(data)
            if size > 2 * 1024 * 1024:
                raise FileTooLargeError("File exceeds limit")
            stored_files.append(
                {
                    "filename": filename,
                    "size_bytes": size,
                    "status": "pending",
                    "content": data,
                }
            )

        record = {
            "assessment_id": assessment_id,
            "user_id": user_id,
            "status": "uploaded",
            "stage": "ingestion",
            "progress": 10,
            "files": stored_files,
            "errors": [],
        }
        self.assessments[assessment_id] = record
        return {
            "assessment_id": assessment_id,
            "status": "uploaded",
            "files": [
                {"filename": f["filename"], "size_bytes": f["size_bytes"]} for f in stored_files
            ],
        }

    async def get_assessment(self, assessment_id: str):
        return self.assessments.get(assessment_id)

    async def list_assessments(self, user_id: str, limit: int = 20, last_key=None):
        items = [record for record in self.assessments.values() if record["user_id"] == user_id]
        return {"items": items[:limit], "last_evaluated_key": None}

    async def update_status(self, assessment_id: str, status: str | None = None, extra=None):
        record = self.assessments[assessment_id]
        if status:
            record["status"] = status
        if extra:
            record.update(extra)

    async def get_report_json(self, *_):
        return {"cloud_readiness_score": 88, "key_findings": ["Mock finding"]}

    async def get_report_stream(self, *_):
        return b"%PDF-1.4 mock report", "application/pdf"

    async def complete_assessment(self, assessment_id: str):
        record = self.assessments[assessment_id]
        record.update(
            {
                "status": "completed",
                "stage": "completed",
                "progress": 100,
                "report_url": f"s3://reports/{assessment_id}.pdf",
                "report_json_url": f"s3://reports/{assessment_id}.json",
            }
        )

    async def fail_assessment(self, assessment_id: str, message: str):
        record = self.assessments[assessment_id]
        record["status"] = "failed"
        record["errors"].append(message)


class FakeWorkflow:
    def __init__(self, assessment_id: str, *_args, **_kwargs):
        self.assessment_id = assessment_id
        self.workflow_id = f"wf-{assessment_id}"

    async def run(self):
        await asyncio.sleep(0)
        if fake_service:
            await fake_service.complete_assessment(self.assessment_id)


@pytest.fixture
def fake_service(monkeypatch):
    service = FakeQuickAssessService()
    # Provide FakeWorkflow with access to this service
    global fake_service
    fake_service = service
    monkeypatch.setattr(api_module, "QuickAssessWorkflow", FakeWorkflow)
    return service


@pytest.fixture
async def client(fake_service, monkeypatch):
    settings.quick_assess_api_key = API_KEY
    settings.default_user_id = "test-user"

    async def override_user():
        return AuthenticatedUser({"user_id": "test-user"})

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_quick_assess_service] = lambda: fake_service

    async with AsyncClient(app=app, base_url="http://testserver") as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _multipart_file(name: str, content: bytes, content_type: str) -> tuple:
    return (name, BytesIO(content), content_type)


@pytest.mark.asyncio
async def test_end_to_end_workflow(client):
    files = [
        ("files", _multipart_file("infrastructure-design.docx", sample_docx_bytes(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
        ("files", _multipart_file("architecture-diagram.vsdx", sample_vsdx_bytes(), "application/vnd.visio")),
    ]
    upload = await client.post(
        "/api/v1/quick-assess/upload",
        headers={"X-API-Key": API_KEY},
        files=files,
    )
    assert upload.status_code == status.HTTP_201_CREATED
    assessment_id = upload.json()["assessment_id"]

    execute = await client.post(
        f"/api/v1/quick-assess/{assessment_id}/execute",
        headers={"X-API-Key": API_KEY},
    )
    assert execute.status_code == status.HTTP_202_ACCEPTED

    await asyncio.sleep(0.05)

    status_resp = await client.get(
        f"/api/v1/quick-assess/{assessment_id}/status",
        headers={"X-API-Key": API_KEY},
    )
    assert status_resp.json()["status"] == "completed"

    results = await client.get(
        f"/api/v1/quick-assess/{assessment_id}/results",
        headers={"X-API-Key": API_KEY},
    )
    assert results.json()["results"]["cloud_readiness_score"] == 88

    report = await client.get(
        f"/api/v1/quick-assess/{assessment_id}/report",
        headers={"X-API-Key": API_KEY},
    )
    assert report.status_code == status.HTTP_200_OK
    assert report.headers["content-type"] == "application/pdf"


@pytest.mark.asyncio
async def test_upload_rejects_invalid_file_type(client):
    files = [
        ("files", _multipart_file("script.exe", b"danger", "application/octet-stream")),
    ]
    response = await client.post(
        "/api/v1/quick-assess/upload",
        headers={"X-API-Key": API_KEY},
        files=files,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_upload_rejects_large_files(client):
    big_payload = b"x" * (3 * 1024 * 1024)
    files = [
        ("files", _multipart_file("infra.pdf", big_payload, "application/pdf")),
    ]
    response = await client.post(
        "/api/v1/quick-assess/upload",
        headers={"X-API-Key": API_KEY},
        files=files,
    )
    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


@pytest.mark.asyncio
async def test_status_surfaces_partial_failures(client, fake_service):
    files = [
        ("files", _multipart_file("infrastructure-design.docx", sample_docx_bytes(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
    ]
    upload = await client.post(
        "/api/v1/quick-assess/upload",
        headers={"X-API-Key": API_KEY},
        files=files,
    )
    assessment_id = upload.json()["assessment_id"]
    record = fake_service.assessments[assessment_id]
    record["files"][0]["status"] = "failed"
    record["errors"].append("Diagram parsing error")

    status_resp = await client.get(
        f"/api/v1/quick-assess/{assessment_id}/status",
        headers={"X-API-Key": API_KEY},
    )
    body = status_resp.json()
    assert body["files"][0]["status"] == "failed"
    assert "Diagram parsing error" in body["error_messages"]

