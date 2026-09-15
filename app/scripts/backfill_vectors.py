import asyncio
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.report import Report
from app.services.ai_assistant_service import ai_assistant_service

async def run_backfill():
    print("Starting Vector DB Backfill...")
    async with AsyncSessionLocal() as db:
        stmt = select(Report)
        result = await db.execute(stmt)
        reports = result.scalars().all()
        
        count = len(reports)
        print(f"Found {count} reports to backfill.")
        
        for i, report in enumerate(reports):
            try:
                print(f"[{i+1}/{count}] Syncing Report {report.report_id}...")
                await ai_assistant_service.sync_report_to_vector_db(db, str(report.report_id))
            except Exception as e:
                print(f"Failed to sync report {report.report_id}: {e}")
                
    print("Vector DB Backfill completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_backfill())
