from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from datetime import date, timedelta
from app.repositories.report_repository import report_repository

class AnalyticsService:
    async def get_dashboard_summary(self, db: AsyncSession, week_start_date: date) -> Dict[str, int]:
        # Get all reports for this week
        reports = await report_repository.get_reports_by_week(db, week_start_date)
        
        total_submitted = 0
        needs_correction = 0
        open_blockers = 0
        
        for report in reports:
            status = report.status.status_name
            if status in ["SUBMITTED", "APPROVED"]:
                total_submitted += 1
            if status == "NEEDS_CORRECTION":
                needs_correction += 1
                
            if status != "DRAFT" and report.versions:
                latest_version = report.versions[0]
                blockers = latest_version.blockers or []
                open_blockers += len(blockers)
                
        return {
            "total_submitted": total_submitted,
            "needs_correction": needs_correction,
            "open_blockers": open_blockers
        }

    async def get_dashboard_charts(self, db: AsyncSession, end_date: date) -> Dict[str, Any]:
        # We will fetch all reports from the last 4 weeks for the line chart
        start_date = end_date - timedelta(days=28)
        
        # Use existing repo method to get all reports in range
        reports = await report_repository.get_all_reports(db, start_date=start_date, end_date=end_date, limit=1000)
        
        time_by_task_type: Dict[str, float] = {}
        tasks_completed_trend_map: Dict[str, int] = {}
        
        for report in reports:
            if report.status.status_name == "DRAFT":
                continue
                
            # Line chart: aggregate completed tasks by week
            week_str = report.week_start_date.isoformat()
            if week_str not in tasks_completed_trend_map:
                tasks_completed_trend_map[week_str] = 0
                
            if report.versions:
                latest_version = report.versions[0]
                tasks_completed = latest_version.tasks_completed or []
                tasks_completed_trend_map[week_str] += len(tasks_completed)
                
                # Pie chart: aggregate hours by task type
                hours_by_type = latest_version.hours_worked_by_type or {}
                for task_type, hours in hours_by_type.items():
                    if task_type not in time_by_task_type:
                        time_by_task_type[task_type] = 0.0
                    time_by_task_type[task_type] += hours

        tasks_completed_trend = [{"date": k, "value": v} for k, v in sorted(tasks_completed_trend_map.items())]
        
        return {
            "time_by_task_type": time_by_task_type,
            "tasks_completed_trend": tasks_completed_trend
        }

analytics_service = AnalyticsService()
