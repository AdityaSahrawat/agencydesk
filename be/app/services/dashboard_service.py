import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.membership import RoleEnum
from app.models.task import TaskStatus
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.time_entry_repository import TimeEntryRepository
from app.repositories.client_repository import ClientRepository
from app.schemas.dashboard import DashboardSummaryResponse, ProjectSummary, TaskCountByStatus


class DashboardService:
    def __init__(self, db: AsyncSession, agency_id: uuid.UUID):
        self.db = db
        self.agency_id = agency_id
        self.project_repo = ProjectRepository(db, agency_id)
        self.task_repo = TaskRepository(db, agency_id)
        self.time_repo = TimeEntryRepository(db, agency_id)
        self.client_repo = ClientRepository(db, agency_id)

    async def get_summary(
        self,
        user_id: uuid.UUID,
        role: RoleEnum,
        client_id: Optional[uuid.UUID] = None
    ) -> DashboardSummaryResponse:
        projects = await self.project_repo.list_for_user(user_id, role, client_id)

        user_filter_for_tasks = user_id if role == RoleEnum.AGENCY_MEMBER else None
        tasks = await self.task_repo.list_tasks(
            role=role,
            client_id=client_id,
            assigned_to=user_filter_for_tasks
        )

        overall_status_counts = TaskCountByStatus()
        for t in tasks:
            if t.status == TaskStatus.TODO:
                overall_status_counts.todo += 1
            elif t.status == TaskStatus.IN_PROGRESS:
                overall_status_counts.in_progress += 1
            elif t.status == TaskStatus.REVIEW:
                overall_status_counts.review += 1
            elif t.status == TaskStatus.DONE:
                overall_status_counts.done += 1

        total_hours = await self.time_repo.get_total_hours_logged(
            user_id=user_id if role == RoleEnum.AGENCY_MEMBER else None,
            client_id=client_id if role == RoleEnum.CLIENT_USER else None
        )

        project_summaries: List[ProjectSummary] = []
        for p in projects:
            p_tasks = [t for t in tasks if t.project_id == p.id]
            p_status_counts = TaskCountByStatus()
            for pt in p_tasks:
                if pt.status == TaskStatus.TODO:
                    p_status_counts.todo += 1
                elif pt.status == TaskStatus.IN_PROGRESS:
                    p_status_counts.in_progress += 1
                elif pt.status == TaskStatus.REVIEW:
                    p_status_counts.review += 1
                elif pt.status == TaskStatus.DONE:
                    p_status_counts.done += 1

            p_hours = await self.time_repo.get_project_total_hours(p.id)
            client_name = p.client.name if p.client else None

            project_summaries.append(
                ProjectSummary(
                    id=p.id,
                    name=p.name,
                    client_name=client_name,
                    status=p.status.value,
                    total_hours=p_hours,
                    task_counts=p_status_counts
                )
            )

        return DashboardSummaryResponse(
            total_projects=len(projects),
            total_tasks=len(tasks),
            task_count_by_status=overall_status_counts,
            total_hours_logged=total_hours,
            projects_summary=project_summaries
        )
