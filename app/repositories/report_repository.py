from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.report_status import ReportStatus
from app.models.report import Report
from app.models.report_version import ReportVersion

class ReportRepository:
    # --- Status Management ---
    async def get_status_by_name(self, db: AsyncSession, name: str) -> Optional[ReportStatus]:
        stmt = select(ReportStatus).where(ReportStatus.status_name == name)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create_status(self, db: AsyncSession, name: str, description: str = None) -> ReportStatus:
        status = ReportStatus(status_name=name, description=description)
        db.add(status)
        await db.flush()
        await db.refresh(status)
        return status

    # --- Reports ---
    async def create_report(self, db: AsyncSession, report: Report) -> Report:
        db.add(report)
        await db.flush()
        await db.refresh(report)
        return report

    async def create_report_version(self, db: AsyncSession, version: ReportVersion) -> ReportVersion:
        db.add(version)
        await db.flush()
        await db.refresh(version)
        return version

    async def update_report(self, db: AsyncSession, report: Report) -> Report:
        db.add(report)
        await db.flush()
        await db.refresh(report)
        return report

    async def get_report_by_id(self, db: AsyncSession, report_id: str) -> Optional[Report]:
        stmt = (
            select(Report)
            .options(
                selectinload(Report.status),
                selectinload(Report.project),
                selectinload(Report.versions).selectinload(ReportVersion.status)
            )
            .where(Report.report_id == report_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_user_reports(
        self, db: AsyncSession, user_id: str, skip: int = 0, limit: int = 100,
        start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[Report]:
        stmt = (
            select(Report)
            .options(selectinload(Report.status), selectinload(Report.project))
            .where(Report.user_id == user_id)
        )
        if start_date:
            stmt = stmt.where(Report.week_start_date >= start_date)
        if end_date:
            stmt = stmt.where(Report.week_end_date <= end_date)
            
        stmt = stmt.order_by(Report.week_start_date.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_all_reports(
        self, db: AsyncSession, skip: int = 0, limit: int = 100,
        user_id: Optional[str] = None, project_id: Optional[str] = None,
        start_date: Optional[date] = None, end_date: Optional[date] = None,
        status_id: Optional[str] = None
    ) -> List[Report]:
        stmt = select(Report).options(selectinload(Report.status), selectinload(Report.project), selectinload(Report.user))
        
        if user_id:
            stmt = stmt.where(Report.user_id == user_id)
        if project_id:
            stmt = stmt.where(Report.project_id == project_id)
        if start_date:
            stmt = stmt.where(Report.week_start_date >= start_date)
        if end_date:
            stmt = stmt.where(Report.week_end_date <= end_date)
        if status_id:
            stmt = stmt.where(Report.current_status_id == status_id)
            
        stmt = stmt.order_by(Report.week_start_date.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_reports_by_week(self, db: AsyncSession, week_start_date: date) -> List[Report]:
        stmt = (
            select(Report)
            .options(
                selectinload(Report.user),
                selectinload(Report.versions)
            )
            .where(Report.week_start_date == week_start_date)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_report_versions(self, db: AsyncSession, report_id: str) -> List[ReportVersion]:
        stmt = (
            select(ReportVersion)
            .options(selectinload(ReportVersion.status))
            .where(ReportVersion.report_id == report_id)
            .order_by(ReportVersion.version_num.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

report_repository = ReportRepository()
