from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import platform
import sys
from datetime import datetime, timezone

from app.db.session import get_db
from app.core.config import settings

router = APIRouter()

START_TIME = datetime.now(timezone.utc)

@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    # Verify Database Connection
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    current_time = datetime.now(timezone.utc)
    uptime = current_time - START_TIME
    
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "server": {
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": sys.version.split(" ")[0],
            "machine": platform.machine()
        },
        "time": {
            "current_time_utc": current_time.isoformat(),
            "uptime_seconds": int(uptime.total_seconds())
        }
    }
