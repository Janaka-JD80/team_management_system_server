from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.access_control import PermissionResponse
from app.schemas.base import StandardResponse
from app.services.access_control_service import access_control_service

router = APIRouter()

@router.get("/", response_model=StandardResponse[List[PermissionResponse]])
async def get_all_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    data = await access_control_service.get_all_permissions(db, skip=skip, limit=limit, search=search)
    return StandardResponse(data=data)
