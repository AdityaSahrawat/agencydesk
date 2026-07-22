from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_membership, get_db
from app.models.user import User
from app.models.membership import AgencyMembership
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    membership: AgencyMembership = Depends(get_tenant_membership),
    db: AsyncSession = Depends(get_db)
):
    dashboard_service = DashboardService(db, membership.agency_id)
    return await dashboard_service.get_summary(
        user_id=current_user.id,
        role=membership.role,
        client_id=membership.client_id
    )
