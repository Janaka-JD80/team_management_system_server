from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_

from app.models.user import User
from app.models.role import Role

class UserRepository:
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.user_email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        stmt = select(User).options(selectinload(User.roles)).where(User.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_users_with_roles(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None
    ) -> List[User]:
        stmt = select(User).options(selectinload(User.roles).selectinload(Role.permissions))
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    User.user_email.ilike(search_term),
                    User.full_name.ilike(search_term)
                )
            )
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().unique().all()

    async def get_team_members(self, db: AsyncSession) -> List[User]:
        stmt = select(User).join(User.roles).where(Role.role_name == "team_member")
        result = await db.execute(stmt)
        return result.scalars().unique().all()

    async def create_user(self, db: AsyncSession, user: User) -> User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

user_repository = UserRepository()
