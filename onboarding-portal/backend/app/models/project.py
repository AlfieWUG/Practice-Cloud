"""
Project, AgentExecution, and Artifact models.
"""
from sqlalchemy import Column, String, Text, Integer, BigInteger, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
import enum

from app.database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise stores as CHAR(32) for SQLite.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return str(value)
        # For SQLite store without dashes
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(str(value))
        return str(value).replace('-', '')

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        # Convert back to canonical UUID string
        if len(value) == 32:
            value = f"{value[:8]}-{value[8:12]}-{value[12:16]}-{value[16:20]}-{value[20:]}"
        return uuid.UUID(str(value))


class ProjectStatus(str, enum.Enum):
    """Project status options."""
    PLANNING = "planning"
    DISCOVERY = "discovery"
    ASSESSMENT = "assessment"
    EXECUTION = "execution"
    OPTIMIZATION = "optimization"
    COMPLETED = "completed"
    FAILED = "failed"


class MigrationPhase(str, enum.Enum):
    """Migration phase options."""
    DISCOVERY = "discovery"
    ASSESSMENT = "assessment"
    EXECUTION = "execution"
    OPTIMIZATION = "optimization"


class AgentExecutionStatus(str, enum.Enum):
    """Agent execution status options."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ArtifactType(str, enum.Enum):
    """Artifact type options."""
    REPORT = "report"
    DIAGRAM = "diagram"
    EXCEL = "excel"
    PDF = "pdf"
    JSON = "json"
    YAML = "yaml"


class Project(Base):
    """Migration project model."""
    
    __tablename__ = "projects"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    target_cloud = Column(String(50), default="aws", nullable=False)
    status = Column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.PLANNING,
        nullable=False,
        index=True
    )
    current_phase = Column(
        SQLEnum(MigrationPhase),
        nullable=True
    )
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    customer = relationship("Customer", back_populates="projects")
    agent_executions = relationship(
        "AgentExecution",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    artifacts = relationship(
        "Artifact",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"


class AgentExecution(Base):
    """Agent execution tracking model."""
    
    __tablename__ = "agent_executions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    phase = Column(SQLEnum(MigrationPhase), nullable=False, index=True)
    status = Column(
        SQLEnum(AgentExecutionStatus),
        default=AgentExecutionStatus.QUEUED,
        nullable=False,
        index=True
    )
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="agent_executions")
    artifacts = relationship(
        "Artifact",
        back_populates="agent_execution",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<AgentExecution(id={self.id}, agent={self.agent_name}, status={self.status})>"


class Artifact(Base):
    """Generated artifact model."""
    
    __tablename__ = "artifacts"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id"), nullable=False, index=True)
    agent_execution_id = Column(
        GUID(),
        ForeignKey("agent_executions.id"),
        nullable=True,
        index=True
    )
    artifact_type = Column(SQLEnum(ArtifactType), nullable=False)
    file_name = Column(String(255), nullable=False)
    s3_url = Column(String(512), nullable=False)
    size_bytes = Column(BigInteger, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="artifacts")
    agent_execution = relationship("AgentExecution", back_populates="artifacts")
    
    def __repr__(self):
        return f"<Artifact(id={self.id}, file={self.file_name})>"
