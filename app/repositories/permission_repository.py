from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.permission import Permission

class PermissionRepository:
    async def get_all_permissions(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None
    ) -> List[Permission]:
        stmt = select(Permission)
        if search:
            stmt = stmt.where(Permission.permission_name.ilike(f"%{search}%"))
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_permission_by_id(self, db: AsyncSession, permission_id: str) -> Optional[Permission]:
        stmt = select(Permission).where(Permission.permission_id == permission_id)
        result = await db.execute(stmt)
        return result.scalars().first()

permission_repository = PermissionRepository()
