from fastapi import APIRouter

from app.api.v1.endpoints import (
    agencies,
    auth,
    clients,
    comments,
    dashboard,
    files,
    invitations,
    projects,
    tasks,
    time_entries,
    users
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(agencies.router, prefix="/agencies", tags=["agencies"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(time_entries.router, prefix="/time-entries", tags=["time-entries"])
api_router.include_router(invitations.router, prefix="/invitations", tags=["invitations"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
