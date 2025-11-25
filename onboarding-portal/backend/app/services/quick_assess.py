"""Service for managing Quick Assess uploads."""
from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import SpooledTemporaryFile
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import UploadFile

from app.config import settings

logger = logging.getLogger(__name__)


class InvalidFileTypeError(ValueError):
    """Raised when a file extension is not allowed."""


class FileTooLargeError(ValueError):
    """Raised when a file exceeds the configured size limit."""


class StorageUploadError(RuntimeError):
    """Raised when S3 upload fails."""


class MetadataWriteError(RuntimeError):
    """Raised when DynamoDB metadata persistence fails."""


@dataclass
class UploadedFileResult:
    """Represents a file that was uploaded to S3."""

    filename: str
    size_bytes: int
    s3_key: str


class QuickAssessService:
    """Handles validation, storage, and metadata for Quick Assess files."""

    allowed_extensions = {".docx", ".pdf", ".vsdx", ".drawio", ".xml"}
    max_file_size_bytes = 50 * 1024 * 1024  # 50 MB
    upload_chunk_size = 1024 * 1024  # 1 MB

    def __init__(
        self,
        s3_bucket: Optional[str] = None,
        dynamodb_table_name: Optional[str] = None,
    ):
        # Check if we're in local development mode
        # Use local storage if:
        # 1. We're in development mode AND
        # 2. No real AWS credentials (empty or test/dummy values)
        is_test_credentials = (
            not settings.aws_access_key_id or 
            settings.aws_access_key_id in ("test", "dummy", "") or
            settings.aws_secret_access_key in ("test", "dummy", "")
        )
        self.use_local_storage = settings.app_env == "development" and is_test_credentials
        
        if self.use_local_storage:
            # Use local file storage instead of S3
            self.local_storage_path = Path("/tmp/quick-assess-uploads")
            self.local_storage_path.mkdir(parents=True, exist_ok=True)
            self.s3 = None
            self.bucket = None
            logger.info(f"QuickAssess using LOCAL file storage at {self.local_storage_path}")
        else:
            # Use S3 (production or with AWS credentials)
            logger.info(f"QuickAssess using S3 bucket: {s3_bucket or settings.s3_quick_assess_bucket}")
            session = boto3.session.Session(
                aws_access_key_id=settings.aws_access_key_id or None,
                aws_secret_access_key=settings.aws_secret_access_key or None,
                region_name=settings.aws_region,
            )
            # Check for LocalStack endpoint (for local S3 emulation)
            s3_endpoint = os.getenv("S3_ENDPOINT_URL") or os.getenv("AWS_ENDPOINT_URL")
            if s3_endpoint:
                self.s3 = session.client("s3", endpoint_url=s3_endpoint)
            else:
                self.s3 = session.client("s3")
            self.bucket = s3_bucket or settings.s3_quick_assess_bucket
        
        # DynamoDB setup
        dynamodb_endpoint = os.getenv("DYNAMODB_ENDPOINT")
        if dynamodb_endpoint:
            logger.info(f"Connecting to DynamoDB at {dynamodb_endpoint}")
            dynamodb = boto3.resource(
                "dynamodb",
                endpoint_url=dynamodb_endpoint,
                aws_access_key_id=settings.aws_access_key_id or "test",
                aws_secret_access_key=settings.aws_secret_access_key or "test",
                region_name=settings.aws_region or "us-east-1",
            )
        else:
            session = boto3.session.Session(
                aws_access_key_id=settings.aws_access_key_id or None,
                aws_secret_access_key=settings.aws_secret_access_key or None,
                region_name=settings.aws_region,
            )
            dynamodb = session.resource("dynamodb")
        
        table_name = dynamodb_table_name or settings.dynamodb_quick_assess_table
        logger.info(f"Using DynamoDB table: {table_name}")
        self.table = dynamodb.Table(table_name)
        errors_table = getattr(settings, "dynamodb_quick_assess_errors_table", None)
        self.errors_table = dynamodb.Table(errors_table) if errors_table else None

    @staticmethod
    def generate_assessment_id() -> str:
        """Create a unique assessment identifier."""
        return f"qa-{uuid4().hex}"

    def _validate_extension(self, filename: str) -> None:
        suffix = Path(filename).suffix.lower()
        if suffix not in self.allowed_extensions:
            raise InvalidFileTypeError(
                f"File type '{suffix or 'unknown'}' is not supported"
            )

    async def _read_file_to_spool(self, file: UploadFile) -> Tuple[SpooledTemporaryFile, int]:
        spool = SpooledTemporaryFile(max_size=self.max_file_size_bytes)
        total_bytes = 0

        while True:
            chunk = await file.read(self.upload_chunk_size)
            if not chunk:
                break

            total_bytes += len(chunk)
            if total_bytes > self.max_file_size_bytes:
                spool.close()
                raise FileTooLargeError(
                    f"{file.filename} exceeds the 50 MB limit"
                )

            spool.write(chunk)

        spool.seek(0)
        return spool, total_bytes

    async def upload_files(
        self,
        assessment_id: str,
        files: List[UploadFile],
    ) -> List[UploadedFileResult]:
        """Validate and upload files to S3."""
        uploaded: List[UploadedFileResult] = []

        for upload_file in files:
            if not upload_file.filename:
                raise InvalidFileTypeError("Each file must include a filename")

            self._validate_extension(upload_file.filename)
            spool, total_bytes = await self._read_file_to_spool(upload_file)
            key = f"quick-assess/{assessment_id}/{Path(upload_file.filename).name}"

            try:
                if self.use_local_storage:
                    # Store locally for development
                    local_file_path = self.local_storage_path / assessment_id / Path(upload_file.filename).name
                    local_file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(local_file_path, "wb") as f:
                        spool.seek(0)
                        f.write(spool.read())
                    # Use a file:// URL for local storage
                    s3_key = f"file://{str(local_file_path)}"
                else:
                    # Upload to S3
                    await asyncio.to_thread(
                        self.s3.upload_fileobj,
                        spool,
                        self.bucket,
                        key,
                        {"ContentType": upload_file.content_type or "application/octet-stream"},
                    )
                    s3_key = key
            except (BotoCoreError, ClientError) as exc:
                raise StorageUploadError(f"Failed to upload {upload_file.filename}: {exc}") from exc
            except Exception as exc:
                raise StorageUploadError(f"Failed to upload {upload_file.filename}: {exc}") from exc
            finally:
                spool.close()
                await upload_file.close()

            uploaded.append(
                UploadedFileResult(
                    filename=upload_file.filename,
                    size_bytes=total_bytes,
                    s3_key=s3_key,
                )
            )

        return uploaded

    async def persist_metadata(
        self,
        assessment_id: str,
        uploaded_files: List[UploadedFileResult],
        user_id: str,
    ) -> None:
        """Store assessment metadata in DynamoDB."""
        item = {
            "assessment_id": assessment_id,
            "status": "uploaded",
            "upload_time": datetime.now(timezone.utc).isoformat(),
            "files": [
                {
                    "filename": file.filename,
                    "size_bytes": file.size_bytes,
                    "s3_key": file.s3_key,
                }
                for file in uploaded_files
            ],
            "user_id": user_id,
            "stage": "ingestion",
            "progress": 10,
            "errors": [],
        }

        try:
            await asyncio.to_thread(self.table.put_item, Item=item)
        except (BotoCoreError, ClientError) as exc:
            logger.error(f"DynamoDB write failed: {exc}", exc_info=True)
            raise MetadataWriteError(f"Failed to persist assessment metadata: {exc}") from exc
        except Exception as exc:
            logger.error(f"Unexpected error writing metadata: {exc}", exc_info=True)
            raise MetadataWriteError(f"Failed to persist assessment metadata: {exc}") from exc

    async def create_assessment(
        self,
        files: List[UploadFile],
        user_id: str,
    ) -> Dict[str, Any]:
        assessment_id = self.generate_assessment_id()
        uploaded = await self.upload_files(assessment_id, files)
        await self.persist_metadata(assessment_id, uploaded, user_id=user_id)
        return {
            "assessment_id": assessment_id,
            "status": "uploaded",
            "files": [
                {"filename": file.filename, "size_bytes": file.size_bytes}
                for file in uploaded
            ],
        }

    async def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = await asyncio.to_thread(
                self.table.get_item, Key={"assessment_id": assessment_id}
            )
            return response.get("Item")
        except (BotoCoreError, ClientError) as exc:
            raise MetadataWriteError("Failed to read assessment metadata") from exc

    async def list_assessments(
        self,
        user_id: str,
        limit: int = 20,
        last_key: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        scan_kwargs: Dict[str, Any] = {
            "FilterExpression": "#uid = :user_id",
            "ExpressionAttributeNames": {"#uid": "user_id"},
            "ExpressionAttributeValues": {":user_id": user_id},
            "Limit": limit,
        }
        if last_key:
            scan_kwargs["ExclusiveStartKey"] = last_key

        response = await asyncio.to_thread(self.table.scan, **scan_kwargs)
        return {
            "items": response.get("Items", []),
            "last_evaluated_key": response.get("LastEvaluatedKey"),
        }

    async def update_status(
        self,
        assessment_id: str,
        status: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        update_expression = ["updated_at = :ts"]
        expression_values: Dict[str, Any] = {":ts": datetime.now(timezone.utc).isoformat()}
        expression_names: Dict[str, str] = {}

        if status:
            expression_names["#s"] = "status"
            expression_values[":status"] = status
            update_expression.append("#s = :status")

        if extra:
            for idx, (key, value) in enumerate(extra.items()):
                placeholder = f"#f{idx}"
                value_placeholder = f":v{idx}"
                expression_names[placeholder] = key
                expression_values[value_placeholder] = value
                update_expression.append(f"{placeholder} = {value_placeholder}")

        await asyncio.to_thread(
            self.table.update_item,
            Key={"assessment_id": assessment_id},
            UpdateExpression="SET " + ", ".join(update_expression),
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names or None,
        )

    async def append_error(self, assessment_id: str, message: str) -> None:
        if not self.errors_table:
            return
        await asyncio.to_thread(
            self.errors_table.put_item,
            Item={
                "assessment_id": assessment_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": message,
            },
        )

    async def get_report_json(self, s3_uri: str) -> Dict[str, Any]:
        bucket, key = self._parse_s3_uri(s3_uri)
        response = await asyncio.to_thread(
            self.s3.get_object,
            Bucket=bucket,
            Key=key,
        )
        import json

        return json.loads(response["Body"].read())

    async def get_report_stream(self, s3_uri: str) -> Tuple[bytes, str]:
        bucket, key = self._parse_s3_uri(s3_uri)
        response = await asyncio.to_thread(
            self.s3.get_object,
            Bucket=bucket,
            Key=key,
        )
        return response["Body"].read(), response.get("ContentType", "application/pdf")

    def _parse_s3_uri(self, s3_uri: str) -> Tuple[str, str]:
        if not s3_uri.startswith("s3://"):
            raise ValueError("Invalid S3 URI")
        bucket_key = s3_uri.replace("s3://", "", 1)
        bucket, _, key = bucket_key.partition("/")
        if not bucket or not key:
            raise ValueError("S3 URI missing bucket/key")
        return bucket, key

