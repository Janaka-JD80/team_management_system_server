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
            
            report = Report(
                user_id=member.user_id,
                project_id=project.project_id,
                week_start_date=week_start,
                week_end_date=week_end,
                current_version_num=1,
                current_status_id=status_map[status_name]
            )
            db.add(report)
            await db.flush()
            
            version = ReportVersion(
                report_id=report.report_id,
                version_num=1,
                status_id=status_map[status_name],
                tasks_completed=[{"id": 1, "task": f"Completed task for week {week_start}", "status": "Done"}, {"id": 2, "task": "Fixed a critical bug", "status": "Done"}],
                tasks_planned=[{"id": 3, "task": "Plan for next week", "status": "Todo"}],
                blockers=["Database access issues"] if random.random() > 0.7 else [],
                achievements=["Shipped new feature"] if random.random() > 0.6 else [],
                hours_worked_by_type={"Development": random.randint(20, 35), "Meetings": random.randint(2, 10), "Documentation": random.randint(1, 5)}
            )
            db.add(version)
            
    await db.commit()
    print("Reports seeded.")
