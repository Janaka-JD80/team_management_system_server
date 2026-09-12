from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from app.db.session import get_db
from app.schemas.report import (
    ReportResponse, 
    ReportWithLatestVersionResponse, 
    ReportCreate, 
    ReportUpdate, 
    ManagerReview, 
    ReportVersionResponse,
    ReportSummaryResponse
)
from app.schemas.base import StandardResponse
from app.services.report_service import report_service
from app.schemas.auth import JwtPayload
from app.core.deps import get_current_user, RequirePermission

router = APIRouter()

@router.get("/", response_model=StandardResponse[List[ReportResponse]])
async def get_all_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status_id: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: JwtPayload = Depends(RequirePermission("view:all_reports"))
):
    data = await report_service.get_all_reports(
        db, skip=skip, limit=limit, user_id=user_id, project_id=project_id,
        start_date=start_date, end_date=end_date, status_id=status_id, search=search
    )
    return StandardResponse(data=data)

@router.get("/summary", response_model=StandardResponse[List[ReportSummaryResponse]])
async def get_report_summary(
    week_start_date: date,
    section: str = Query(..., description="E.g., blockers, achievements, tasks_completed, tasks_planned"),
    db: AsyncSession = Depends(get_db),
    user: JwtPayload = Depends(RequirePermission("view:all_reports"))
):
    data = await report_service.get_weekly_section_summary(db, week_start_date=str(week_start_date), section=section)
    return StandardResponse(data=data)

@router.post("/", response_model=StandardResponse[ReportWithLatestVersionResponse], status_code=status.HTTP_201_CREATED)
async def create_draft(
    report_in: ReportCreate,
    user: JwtPayload = Depends(RequirePermission("submit:report")),
    db: AsyncSession = Depends(get_db)
):
    data = await report_service.create_draft(db, user_id=user.sub, report_in=report_in)
    return StandardResponse(data=data)

@router.get("/my-reports", response_model=StandardResponse[List[ReportResponse]])
async def get_my_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user: JwtPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    data = await report_service.get_user_reports(
        db, user_id=user.sub, skip=skip, limit=limit, start_date=start_date, end_date=end_date
    )
    return StandardResponse(data=data)

@router.get("/{report_id}", response_model=StandardResponse[ReportWithLatestVersionResponse])
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    data = await report_service.get_report(db, report_id=report_id)
    return StandardResponse(data=data)

@router.get("/{report_id}/history", response_model=StandardResponse[List[ReportVersionResponse]])
async def get_report_history(report_id: str, db: AsyncSession = Depends(get_db)):
    data = await report_service.get_report_versions(db, report_id=report_id)
    return StandardResponse(data=data)

@router.put("/{report_id}", response_model=StandardResponse[ReportWithLatestVersionResponse])
async def update_report(
    report_id: str,
    update_in: ReportUpdate,
    user: JwtPayload = Depends(RequirePermission("edit:own_report")),
    db: AsyncSession = Depends(get_db)
):
    data = await report_service.update_report(db, report_id=report_id, user_id=user.sub, update_in=update_in)
    return StandardResponse(data=data)

@router.post("/{report_id}/submit", response_model=StandardResponse[ReportWithLatestVersionResponse])
async def submit_report(
    report_id: str,
    user: JwtPayload = Depends(RequirePermission("submit:report")),
    db: AsyncSession = Depends(get_db)
):
    data = await report_service.submit_report(db, report_id=report_id, user_id=user.sub)
    return StandardResponse(data=data)

@router.post("/{report_id}/review", response_model=StandardResponse[ReportWithLatestVersionResponse])
async def manager_review(
    report_id: str,
    review_in: ManagerReview,
    db: AsyncSession = Depends(get_db),
    user: JwtPayload = Depends(RequirePermission("review:report"))
):
    data = await report_service.manager_review(db, report_id=report_id, action=review_in.action, comment=review_in.comment)
    return StandardResponse(data=data)
