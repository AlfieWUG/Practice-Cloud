"""
Customer model for multi-tenant isolation.
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
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


class DeploymentModel(str, enum.Enum):
    """Deployment model options."""
    SAAS = "saas"
    SINGLE_TENANT = "single_tenant"
    HYBRID = "hybrid"


class CustomerStatus(str, enum.Enum):
    """Customer status options."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Customer(Base):
    """Customer model for multi-tenant isolation."""
    
    __tablename__ = "customers"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    deployment_model = Column(
        SQLEnum(DeploymentModel),
        default=DeploymentModel.SAAS,
        nullable=False
    )
    aws_account_id = Column(String(12), nullable=True)
    api_endpoint = Column(String(512), nullable=True)
    status = Column(
        SQLEnum(CustomerStatus),
        default=CustomerStatus.ACTIVE,
        nullable=False
    )
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    projects = relationship("Project", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer(id={self.id}, company={self.company_name})>"
