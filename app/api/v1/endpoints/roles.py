from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.access_control import RoleResponse, RoleWithPermissionsResponse, RoleCreate, AssignPermissions
from app.schemas.base import StandardResponse
from app.services.access_control_service import access_control_service
from app.core.deps import RequirePermission
from app.schemas.auth import JwtPayload

router = APIRouter()

@router.get("/", response_model=StandardResponse[List[RoleResponse]])
async def get_all_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    data = await access_control_service.get_all_roles(db, skip=skip, limit=limit, search=search)
    return StandardResponse(data=data)

@router.get("/{role_id}", response_model=StandardResponse[RoleWithPermissionsResponse])
async def get_role(role_id: str, db: AsyncSession = Depends(get_db)):
    data = await access_control_service.get_role(db, role_id=role_id)
    return StandardResponse(data=data)

@router.post("/", response_model=StandardResponse[RoleResponse], status_code=status.HTTP_201_CREATED)
async def create_role(role_in: RoleCreate, db: AsyncSession = Depends(get_db)):
    data = await access_control_service.create_role(db, name=role_in.role_name, description=role_in.role_description)
    return StandardResponse(data=data)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: str, db: AsyncSession = Depends(get_db)):
    await access_control_service.delete_role(db, role_id=role_id)
    return StandardResponse(message="Role deleted successfully")

@router.put("/{role_id}/permissions", response_model=StandardResponse[RoleWithPermissionsResponse])
async def assign_permissions(
    role_id: str,
    payload: AssignPermissions,
    db: AsyncSession = Depends(get_db),
    user: JwtPayload = Depends(RequirePermission("manage:roles"))
):
    permission_ids = [str(pid) for pid in payload.permission_ids]
    data = await access_control_service.assign_permissions_to_role(db, role_id, permission_ids)
    return StandardResponse(data=data)
