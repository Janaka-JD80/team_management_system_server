from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.repositories.user_repository import user_repository
from app.repositories.role_repository import role_repository
from app.repositories.permission_repository import permission_repository

class AccessControlService:
    async def get_all_users(self, db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[User]:
        return await user_repository.get_users_with_roles(db, skip=skip, limit=limit, search=search)

    async def get_all_roles(self, db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Role]:
        return await role_repository.get_all_roles(db, skip=skip, limit=limit, search=search)

    async def get_role(self, db: AsyncSession, role_id: str) -> Role:
        role = await role_repository.get_role_with_permissions(db, role_id=role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role

    async def create_role(self, db: AsyncSession, name: str, description: Optional[str] = None) -> Role:
        existing = await role_repository.get_role_by_name(db, name=name)
        if existing:
            raise HTTPException(status_code=400, detail="Role already exists")
        role = Role(role_name=name, role_description=description)
        return await role_repository.create_role(db, role)

    async def delete_role(self, db: AsyncSession, role_id: str):
        success = await role_repository.delete_role(db, role_id=role_id)
        if not success:
            raise HTTPException(status_code=404, detail="Role not found")

    async def get_all_permissions(self, db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Permission]:
        return await permission_repository.get_all_permissions(db, skip=skip, limit=limit, search=search)

access_control_service = AccessControlService()
