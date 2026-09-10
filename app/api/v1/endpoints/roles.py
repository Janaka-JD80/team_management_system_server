from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.access_control import RoleResponse, RoleWithPermissionsResponse, RoleCreate
from app.services.access_control_service import access_control_service

router = APIRouter()

@router.get("/", response_model=List[RoleResponse])
async def get_all_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    return await access_control_service.get_all_roles(db, skip=skip, limit=limit, search=search)

@router.get("/{role_id}", response_model=RoleWithPermissionsResponse)
async def get_role(role_id: str, db: AsyncSession = Depends(get_db)):
    return await access_control_service.get_role(db, role_id=role_id)

@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(role_in: RoleCreate, db: AsyncSession = Depends(get_db)):
    return await access_control_service.create_role(db, name=role_in.role_name, description=role_in.role_description)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: str, db: AsyncSession = Depends(get_db)):
    await access_control_service.delete_role(db, role_id=role_id)
