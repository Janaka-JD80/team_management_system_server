from fastapi import APIRouter
from app.api.v1.endpoints import health
from app.api.v1.endpoints import auth, users, roles, permissions, projects, reports, analytics, ai_assistant

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(ai_assistant.router, prefix="/ai", tags=["ai"])