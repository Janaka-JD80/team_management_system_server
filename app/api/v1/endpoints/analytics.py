from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.db.session import get_db
from app.schemas.analytics import DashboardSummaryResponse, DashboardChartsResponse
from app.schemas.base import StandardResponse
from app.services.analytics_service import analytics_service
from app.core.deps import RequirePermission
from app.schemas.auth import JwtPayload

router = APIRouter()

@router.get("/summary", response_model=StandardResponse[DashboardSummaryResponse])
async def get_dashboard_summary(
    week_start_date: date,
    db: AsyncSession = Depends(get_db),
    user: JwtPayload = Depends(RequirePermission("view:dashboard"))
):
    """Returns top-level KPIs for the manager dashboard for a specific week."""
    data = await analytics_service.get_dashboard_summary(db, week_start_date)
    return StandardResponse(data=data)

@router.get("/charts", response_model=StandardResponse[DashboardChartsResponse])
async def get_dashboard_charts(
    end_date: date,
    db: AsyncSession = Depends(get_db),
    user: JwtPayload = Depends(RequirePermission("view:dashboard"))
):
    """Returns aggregated data for pie charts (time spent) and line charts (tasks completed trend)."""
    data = await analytics_service.get_dashboard_charts(db, end_date)
    return StandardResponse(data=data)
