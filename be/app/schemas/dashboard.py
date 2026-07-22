import uuid
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.models.task import TaskStatus


class TaskCountByStatus(BaseModel):
    todo: int = 0
    in_progress: int = 0
    review: int = 0
    done: int = 0


class ProjectSummary(BaseModel):
    id: uuid.UUID
    name: str
    client_name: Optional[str] = None
    status: str
    total_hours: float = 0.0
    task_counts: TaskCountByStatus


class DashboardSummaryResponse(BaseModel):
    total_projects: int
    total_tasks: int
    task_count_by_status: TaskCountByStatus
    total_hours_logged: float
    projects_summary: List[ProjectSummary] = []
