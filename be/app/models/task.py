import enum
import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User
    from app.models.comment import Comment
    from app.models.task_file import TaskFile
    from app.models.time_entry import TimeEntry


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "tasks"

    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, native_enum=False), default=TaskStatus.TODO, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority, native_enum=False), default=TaskPriority.MEDIUM, nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    assignee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to])
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])

    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    files: Mapped[List["TaskFile"]] = relationship("TaskFile", back_populates="task", cascade="all, delete-orphan")
    time_entries: Mapped[List["TimeEntry"]] = relationship("TimeEntry", back_populates="task", cascade="all, delete-orphan")
