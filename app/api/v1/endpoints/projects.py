from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate
from app.services.project_service import project_service
from app.core.deps import get_current_user, RequirePermission
from app.schemas.auth import JwtPayload

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
async def get_all_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    return await project_service.get_all_projects(db, skip=skip, limit=limit, search=search)

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: JwtPayload = Depends(RequirePermission("manage:projects"))
):
    return await project_service.create_project(db, name=project_in.name, description=project_in.description)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str,    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: JwtPayload = Depends(RequirePermission("manage:projects"))
):
    update_data = project_in.model_dump(exclude_unset=True)
    return await project_service.update_project(db, project_id, update_data)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: JwtPayload = Depends(RequirePermission("manage:projects"))
):
    await project_service.delete_project(db, project_id)
