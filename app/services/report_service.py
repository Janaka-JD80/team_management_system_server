from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.report import Report
from app.models.report_version import ReportVersion
from app.schemas.report import ReportCreate, ReportUpdate
from app.repositories.report_repository import report_repository

class ReportService:
    async def _get_or_create_status(self, db: AsyncSession, name: str) -> str:
        status = await report_repository.get_status_by_name(db, name)
        if not status:
            status = await report_repository.create_status(db, name)
        return status.status_id

    async def create_draft(self, db: AsyncSession, user_id: str, report_in: ReportCreate) -> Report:
        existing = await report_repository.get_report_by_user_and_week(db, user_id, report_in.week_start_date)
        if existing:
            raise HTTPException(status_code=400, detail="A report already exists for this week.")
            
        draft_status_id = await self._get_or_create_status(db, "DRAFT")
        
        report = Report(
            user_id=user_id,
            project_id=report_in.project_id,
            week_start_date=report_in.week_start_date,
            week_end_date=report_in.week_end_date,
            current_status_id=draft_status_id,
            current_version_num=1
        )
        report = await report_repository.create_report(db, report)
        
        version = ReportVersion(
            report_id=report.report_id,
            version_num=1,
            status_id=draft_status_id,
            tasks_completed=[t.model_dump() for t in report_in.tasks_completed],
            tasks_planned=[t.model_dump() for t in report_in.tasks_planned],
            blockers=[b.model_dump() for b in report_in.blockers],
            achievements=[a.model_dump() for a in report_in.achievements],
            hours_worked_by_type=report_in.hours_worked_by_type,
            optional_notes=report_in.optional_notes
        )
        await report_repository.create_report_version(db, version)
        
        await db.commit()
        return await report_repository.get_report_by_id(db, str(report.report_id))

    async def get_report(self, db: AsyncSession, report_id: str) -> Report:
        report = await report_repository.get_report_by_id(db, report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Manually map nested relationships for Pydantic
        report.user_name = report.user.full_name if report.user else None
        report.project_name = report.project.name if report.project else None
        
        # Attach latest version
        report.latest_version = report.versions[0] if report.versions else None
        return report

    async def get_all_reports(self, db: AsyncSession, **kwargs) -> List[Report]:
        reports = await report_repository.get_all_reports(db, **kwargs)
        for report in reports:
            report.user_name = report.user.full_name if report.user else None
            report.project_name = report.project.name if report.project else None
        return reports

    async def get_user_reports(self, db: AsyncSession, **kwargs) -> List[Report]:
        reports = await report_repository.get_user_reports(db, **kwargs)
        for report in reports:
            report.user_name = report.user.full_name if report.user else None
            report.project_name = report.project.name if report.project else None
        return reports

    async def get_report_versions(self, db: AsyncSession, report_id: str) -> List[ReportVersion]:
        return await report_repository.get_report_versions(db, report_id=report_id)

    async def update_report(self, db: AsyncSession, report_id: str, user_id: str, update_in: ReportUpdate) -> Report:
        report = await self.get_report(db, report_id)
        if str(report.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to edit this report")
        
        if report.status.status_name not in ["DRAFT", "NEEDS_CORRECTION"]:
            raise HTTPException(status_code=400, detail="Can only edit reports in DRAFT or NEEDS_CORRECTION status")

        latest_version = report.latest_version
        
        if report.status.status_name == "NEEDS_CORRECTION":
            report.current_version_num += 1
            await report_repository.update_report(db, report)
            
            new_version = ReportVersion(
                report_id=report.report_id,
                version_num=report.current_version_num,
                status_id=report.current_status_id,
                tasks_completed=latest_version.tasks_completed,
                tasks_planned=latest_version.tasks_planned,
                blockers=latest_version.blockers,
                achievements=latest_version.achievements,
                hours_worked_by_type=latest_version.hours_worked_by_type,
                optional_notes=latest_version.optional_notes
            )
            
            # Apply updates
            if update_in.tasks_completed is not None: new_version.tasks_completed = [t.model_dump() for t in update_in.tasks_completed]
            if update_in.tasks_planned is not None: new_version.tasks_planned = [t.model_dump() for t in update_in.tasks_planned]
            if update_in.blockers is not None: new_version.blockers = [b.model_dump() for b in update_in.blockers]
            if update_in.achievements is not None: new_version.achievements = [a.model_dump() for a in update_in.achievements]
            if update_in.hours_worked_by_type is not None: new_version.hours_worked_by_type = update_in.hours_worked_by_type
            if update_in.optional_notes is not None: new_version.optional_notes = update_in.optional_notes
            
            await report_repository.create_report_version(db, new_version)
        else:
            # It's a draft, just update the current version in place
            if update_in.tasks_completed is not None: latest_version.tasks_completed = [t.model_dump() for t in update_in.tasks_completed]
            if update_in.tasks_planned is not None: latest_version.tasks_planned = [t.model_dump() for t in update_in.tasks_planned]
            if update_in.blockers is not None: latest_version.blockers = [b.model_dump() for b in update_in.blockers]
            if update_in.achievements is not None: latest_version.achievements = [a.model_dump() for a in update_in.achievements]
            if update_in.hours_worked_by_type is not None: latest_version.hours_worked_by_type = update_in.hours_worked_by_type
            if update_in.optional_notes is not None: latest_version.optional_notes = update_in.optional_notes
            
            # Commit the in-place update
            db.add(latest_version)

        await db.commit()
        return await self.get_report(db, report_id)

    async def submit_report(self, db: AsyncSession, report_id: str, user_id: str) -> Report:
        report = await self.get_report(db, report_id)
        if str(report.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        if report.status.status_name not in ["DRAFT", "NEEDS_CORRECTION"]:
            raise HTTPException(status_code=400, detail="Only DRAFT or NEEDS_CORRECTION can be submitted")

        submitted_status_id = await self._get_or_create_status(db, "SUBMITTED")
        report.current_status_id = submitted_status_id
        await report_repository.update_report(db, report)
        
        # Also update the latest version status
        latest_version = report.latest_version
        latest_version.status_id = submitted_status_id
        db.add(latest_version)
        await db.commit()
        
        return await self.get_report(db, report_id)

    async def manager_review(self, db: AsyncSession, report_id: str, action: str, comment: Optional[str]) -> Report:
        report = await self.get_report(db, report_id)
        if report.status.status_name != "SUBMITTED":
            raise HTTPException(status_code=400, detail="Can only review SUBMITTED reports")

        if action not in ["APPROVE", "REQUEST_CHANGES"]:
            raise HTTPException(status_code=400, detail="Invalid action")

        new_status_name = "APPROVED" if action == "APPROVE" else "NEEDS_CORRECTION"
        new_status_id = await self._get_or_create_status(db, new_status_name)

        report.current_status_id = new_status_id
        await report_repository.update_report(db, report)

        latest_version = report.latest_version
        latest_version.status_id = new_status_id
        latest_version.manager_comment = comment
        db.add(latest_version)
        await db.commit()

        return await self.get_report(db, report_id)

    async def get_weekly_section_summary(self, db: AsyncSession, week_start_date: str, section: str) -> List[dict]:
        from datetime import date
        week_date = date.fromisoformat(week_start_date) if isinstance(week_start_date, str) else week_start_date
        reports = await report_repository.get_reports_by_week(db, week_date)
        
        summary = []
        for report in reports:
            # We only want reports that are submitted or approved/needs correction, 
            # meaning they have been shared with the manager. If it's a draft, skip it.
            if report.status.status_name == "DRAFT":
                continue
            
            latest_version = report.versions[0] if report.versions else None
            if not latest_version:
                continue
            
            # Extract the specific section
            data = getattr(latest_version, section, [])
            
            summary.append({
                "user_id": str(report.user_id),
                "full_name": report.user.full_name,
                "data": data
            })
            
        return summary

report_service = ReportService()
