from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from datetime import date, timedelta
from app.repositories.report_repository import report_repository
from app.repositories.user_repository import user_repository
from fastapi import HTTPException

class AnalyticsService:
    async def get_dashboard_summary(self, db: AsyncSession, week_start_date: date) -> Dict[str, Any]:
        from app.repositories.user_repository import user_repository
        
        team_members = await user_repository.get_team_members(db)
        reports = await report_repository.get_reports_by_week(db, week_start_date)
        
        total_submitted = 0
        needs_correction = 0
        open_blockers = 0
        drafts = 0
        
        for report in reports:
            status = report.status.status_name
            if status in ["SUBMITTED", "APPROVED"]:
                total_submitted += 1
            if status == "NEEDS_CORRECTION":
                needs_correction += 1
            if status == "DRAFT":
                drafts += 1
                
            if status != "DRAFT" and report.versions:
                latest_version = report.versions[0]
                blockers = latest_version.blockers or []
                open_blockers += len(blockers)
                
        pending = drafts + needs_correction + max(0, len(team_members) - len(reports))
        
        return {
            "total_submitted": total_submitted,
            "needs_correction": needs_correction,
            "open_blockers": open_blockers,
            "compliance_rate": {
                "submitted": total_submitted,
                "pending": pending
            }
        }

    async def get_dashboard_charts(self, db: AsyncSession, end_date: date) -> Dict[str, Any]:
        from app.repositories.user_repository import user_repository
        from app.models.report import Report
        
        start_date = end_date - timedelta(days=28)
        week_start_date = end_date - timedelta(days=end_date.weekday())
        
        reports = await report_repository.get_all_reports(db, start_date=start_date, end_date=end_date, limit=1000, exclude_drafts=False)
        team_members = await user_repository.get_team_members(db)
        
        status_by_member_map = {str(tm.user_id): {"user_id": str(tm.user_id), "full_name": tm.full_name, "status": "NOT STARTED"} for tm in team_members}
        
        time_by_task_type: Dict[str, float] = {}
        tasks_completed_trend_map: Dict[str, int] = {}
        workload_by_project: Dict[str, int] = {}
        
        for report in reports:
            week_str = report.week_start_date.isoformat()
            
            if report.week_start_date == week_start_date:
                uid = str(report.user_id)
                if uid in status_by_member_map:
                    status_by_member_map[uid]["status"] = report.status.status_name
                    
            if report.status.status_name == "DRAFT":
                continue
                
            if week_str not in tasks_completed_trend_map:
                tasks_completed_trend_map[week_str] = 0
                
            proj_name = report.project.name if report.project else "No Project"
            if proj_name not in workload_by_project:
                workload_by_project[proj_name] = 0
                
            if report.versions:
                latest_version = report.versions[0]
                tasks_completed = latest_version.tasks_completed or []
                
                num_tasks = len(tasks_completed)
                tasks_completed_trend_map[week_str] += num_tasks
                workload_by_project[proj_name] += num_tasks
                
                hours_by_type = latest_version.hours_worked_by_type or {}
                for task_type, hours in hours_by_type.items():
                    if task_type not in time_by_task_type:
                        time_by_task_type[task_type] = 0.0
                    time_by_task_type[task_type] += hours

        # Recent Activity Feed
        recent_versions = await report_repository.get_recent_report_versions(db, limit=10)
        
        recent_activity = []
        for rv in recent_versions:
            action = f"Submitted Version {rv.version_num}"
            if rv.status.status_name == "NEEDS_CORRECTION":
                action = f"Manager requested changes on Version {rv.version_num}"
            elif rv.status.status_name == "APPROVED":
                action = f"Manager approved Version {rv.version_num}"
            elif rv.status.status_name == "DRAFT":
                action = f"Saved Draft Version {rv.version_num}"
                
            recent_activity.append({
                "report_id": str(rv.report_id),
                "full_name": rv.report.user.full_name if rv.report and rv.report.user else "Unknown User",
                "action": action,
                "timestamp": rv.created_at.isoformat() if rv.created_at else ""
            })

        tasks_completed_trend = [{"date": k, "value": v} for k, v in sorted(tasks_completed_trend_map.items())]
        status_by_member = list(status_by_member_map.values())
        
        return {
            "time_by_task_type": time_by_task_type,
            "tasks_completed_trend": tasks_completed_trend,
            "status_by_member": status_by_member,
            "workload_by_project": workload_by_project,
            "recent_activity": recent_activity
        }

    async def get_team_member_stats(self, db: AsyncSession, user_id: str) -> Dict[str, Any]:
        
        user = await user_repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        reports = await report_repository.get_all_reports(db, user_id=user_id, exclude_drafts=True, limit=1000)
        
        total_tasks_completed = 0
        total_hours_logged = 0.0
        tasks_completed_trend_map: Dict[str, int] = {}
        time_by_task_type: Dict[str, float] = {}
        
        for report in reports:
            week_str = report.week_start_date.isoformat()
            
            if week_str not in tasks_completed_trend_map:
                tasks_completed_trend_map[week_str] = 0
                
            if report.versions:
                latest_version = report.versions[0]
                tasks_completed = latest_version.tasks_completed or []
                
                num_tasks = len(tasks_completed)
                total_tasks_completed += num_tasks
                tasks_completed_trend_map[week_str] += num_tasks
                
                hours_by_type = latest_version.hours_worked_by_type or {}
                for task_type, hours in hours_by_type.items():
                    if task_type not in time_by_task_type:
                        time_by_task_type[task_type] = 0.0
                    time_by_task_type[task_type] += hours
                    total_hours_logged += hours

        total_reports = len(reports)
        avg_tasks_per_week = (total_tasks_completed / total_reports) if total_reports > 0 else 0.0
        
        tasks_completed_trend = [{"date": k, "value": v} for k, v in sorted(tasks_completed_trend_map.items())]

        return {
            "user_id": str(user.user_id),
            "full_name": user.full_name or "Unknown User",
            "total_reports": total_reports,
            "total_tasks_completed": total_tasks_completed,
            "avg_tasks_per_week": avg_tasks_per_week,
            "total_hours_logged": total_hours_logged,
            "tasks_completed_trend": tasks_completed_trend,
            "time_by_task_type": time_by_task_type
        }

analytics_service = AnalyticsService()
