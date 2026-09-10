from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.project import Project

class ProjectRepository:
    async def get_all_projects(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None
    ) -> List[Project]:
        stmt = select(Project)
        if search:
            stmt = stmt.where(Project.name.ilike(f"%{search}%"))
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_project_by_id(self, db: AsyncSession, project_id: str) -> Optional[Project]:
        stmt = select(Project).where(Project.project_id == project_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create_project(self, db: AsyncSession, project: Project) -> Project:
        db.add(project)
        await db.flush()
        await db.refresh(project)
        return project

    async def update_project(self, db: AsyncSession, project_id: str, data: dict) -> Optional[Project]:
        project = await self.get_project_by_id(db, project_id)
        if not project:
            return None
        
        for key, value in data.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        await db.flush()
        await db.refresh(project)
        return project

    async def delete_project(self, db: AsyncSession, project_id: str) -> bool:
        project = await self.get_project_by_id(db, project_id)
        if not project:
            return False
        await db.delete(project)
        await db.flush()
        return True

project_repository = ProjectRepository()
