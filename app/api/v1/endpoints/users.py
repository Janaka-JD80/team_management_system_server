from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.access_control import UserWithRolesResponse, AssignRoles
from app.schemas.base import StandardResponse
from app.services.access_control_service import access_control_service
from app.core.deps import RequirePermission
from app.schemas.auth import JwtPayload

router = APIRouter()

@router.get("/", response_model=StandardResponse[List[UserWithRolesResponse]])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    data = await access_control_service.get_all_users(db, skip=skip, limit=limit, search=search)
    return StandardResponse(data=data)

@router.put("/{user_id}/roles", response_model=StandardResponse[UserWithRolesResponse])
async def assign_roles(
    user_id: str,
    payload: AssignRoles,
    db: AsyncSession = Depends(get_db),
    user: JwtPayload = Depends(RequirePermission("manage:users"))
):
    role_ids = [str(rid) for rid in payload.role_ids]
    data = await access_control_service.assign_roles_to_user(db, user_id, role_ids)
    return StandardResponse(data=data)
