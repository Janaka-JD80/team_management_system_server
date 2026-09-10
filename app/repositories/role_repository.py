from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.role import Role

class RoleRepository:
    async def get_all_roles(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None
    ) -> List[Role]:
        stmt = select(Role)
        if search:
            stmt = stmt.where(Role.role_name.ilike(f"%{search}%"))
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_role_with_permissions(self, db: AsyncSession, role_id: str) -> Optional[Role]:
        stmt = select(Role).options(selectinload(Role.permissions)).where(Role.role_id == role_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_role_by_name(self, db: AsyncSession, name: str) -> Optional[Role]:
        stmt = select(Role).where(Role.role_name == name)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create_role(self, db: AsyncSession, role: Role) -> Role:
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    async def update_role(self, db: AsyncSession, role_id: str, data: dict) -> Optional[Role]:
        role = await self.get_role_with_permissions(db, role_id)
        if not role:
            return None
        
        for key, value in data.items():
            if hasattr(role, key):
                setattr(role, key, value)
        
        await db.commit()
        await db.refresh(role)
        return role

    async def delete_role(self, db: AsyncSession, role_id: str) -> bool:
        role = await self.get_role_with_permissions(db, role_id)
        if not role:
            return False
        await db.delete(role)
        await db.commit()
        return True

role_repository = RoleRepository()
