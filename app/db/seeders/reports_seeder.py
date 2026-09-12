from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.project import Project
from app.models.report_status import ReportStatus
from app.models.report import Report
from app.models.report_version import ReportVersion
import random
from datetime import date, timedelta

async def seed_reports(db: AsyncSession):
    result = await db.execute(select(Report).limit(1))
    if result.scalars().first():
        print("Reports already seeded.")
        return

    users_result = await db.execute(select(User).options(selectinload(User.roles)))
    users = users_result.scalars().unique().all()
    
    projects_result = await db.execute(select(Project))
    projects = projects_result.scalars().all()
    
    status_result = await db.execute(select(ReportStatus))
    statuses = status_result.scalars().all()
    status_map = {s.status_name: s.status_id for s in statuses}
    
    if not users or not projects or not statuses:
        print("Required master data missing for reports seeding.")
        return

    team_members = [u for u in users if any(r.role_name == "team_member" for r in u.roles)]
    today = date.today()
    weeks = [today - timedelta(days=7*i) for i in range(3)]
    
    for member in team_members:
        for week in weeks:
            week_start = week - timedelta(days=week.weekday())
            week_end = week_start + timedelta(days=6)
            
            status_name = random.choice(["SUBMITTED", "APPROVED", "NEEDS_CORRECTION", "DRAFT"])
            project = random.choice(projects)
            
            num_versions = random.randint(1, 3) if status_name != "DRAFT" else 1
            
            report = Report(
                user_id=member.user_id,
                project_id=project.project_id,
                week_start_date=week_start,
                week_end_date=week_end,
                current_version_num=num_versions,
                current_status_id=status_map[status_name]
            )
            db.add(report)
            await db.flush()
            
            for v_num in range(1, num_versions + 1):
                v_status = status_name if v_num == num_versions else random.choice(["DRAFT", "NEEDS_CORRECTION", "SUBMITTED"])
                version = ReportVersion(
                    report_id=report.report_id,
                    version_num=v_num,
                    status_id=status_map[v_status],
                    manager_comment="Please fix the issues." if v_status == "NEEDS_CORRECTION" else None,
                    tasks_completed=[
                        {
                            "task_name": f"Completed task for week {week_start}",
                            "priority": "High",
                            "planned_percent": 100,
                            "actual_percent": 100 if v_num == num_versions else 80,
                            "status": "Done" if v_num == num_versions else "In Progress",
                            "time_planned_hours": 10,
                            "time_spent_hours": 12
                        },
                        {
                            "task_name": "Fixed a critical bug",
                            "priority": "High",
                            "planned_percent": 100,
                            "actual_percent": 100,
                            "status": "Done",
                            "time_planned_hours": 5,
                            "time_spent_hours": 5
                        }
                    ],
                    tasks_planned=[
                        {
                            "task_name": "Plan for next week",
                            "priority": "Medium",
                            "time_planned_hours": 15
                        }
                    ],
                    blockers=[{"description": "Database access issues", "is_key_issue": True}] if random.random() > 0.7 else [],
                    achievements=[{"description": "Shipped new feature", "is_key_achievement": True}] if random.random() > 0.6 else [],
                    hours_worked_by_type={"Development": random.randint(20, 35), "Meetings": random.randint(2, 10), "Documentation": random.randint(1, 5)}
                )
                db.add(version)
            
    await db.commit()
    print("Reports seeded.")
