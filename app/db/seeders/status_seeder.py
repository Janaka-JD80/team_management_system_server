from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.report_status import ReportStatus

async def seed_statuses(db: AsyncSession):
    statuses = ["DRAFT", "SUBMITTED", "NEEDS_CORRECTION", "APPROVED"]
    
    for s_name in statuses:
        stmt = select(ReportStatus).where(ReportStatus.status_name == s_name)
        result = await db.execute(stmt)
        if not result.scalars().first():
            db.add(ReportStatus(status_name=s_name, description=f"{s_name} Status"))
            
    await db.commit()
    print("Statuses seeded.")
