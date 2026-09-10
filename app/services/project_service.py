from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.project import Project
from app.repositories.project_repository import project_repository

class ProjectService:
    async def get_all_projects(self, db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Project]:
        return await project_repository.get_all_projects(db, skip=skip, limit=limit, search=search)

    async def create_project(self, db: AsyncSession, name: str, description: Optional[str] = None) -> Project:
        project = Project(name=name, description=description)
        project = await project_repository.create_project(db, project)
        await db.commit()
        return project

    async def update_project(self, db: AsyncSession, project_id: str, data: dict) -> Project:
        project = await project_repository.update_project(db, project_id, data)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await db.commit()
        return project

    async def delete_project(self, db: AsyncSession, project_id: str):
        success = await project_repository.delete_project(db, project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        await db.commit()

project_service = ProjectService()
