import enum
import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.agency import Agency
    from app.models.client import Client
    from app.models.project_member import ProjectMember
    from app.models.task import Task
    from app.models.time_entry import TimeEntry


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"

    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus, native_enum=False), default=ProjectStatus.ACTIVE, nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    agency: Mapped["Agency"] = relationship("Agency", back_populates="projects")
    client: Mapped["Client"] = relationship("Client", back_populates="projects")
    members: Mapped[List["ProjectMember"]] = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    time_entries: Mapped[List["TimeEntry"]] = relationship("TimeEntry", back_populates="project", cascade="all, delete-orphan")
