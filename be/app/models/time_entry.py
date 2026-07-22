import datetime
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Date, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.task import Task
    from app.models.user import User


class TimeEntry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "time_entries"

    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    hours: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="time_entries")
    task: Mapped[Optional["Task"]] = relationship("Task", back_populates="time_entries")
    user: Mapped["User"] = relationship("User")
