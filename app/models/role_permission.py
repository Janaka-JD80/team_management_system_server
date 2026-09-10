from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class RolePermission(Base):
    __tablename__ = "v1_role_permissions"

    role_id = Column(UUID(as_uuid=True), ForeignKey("v1_roles.role_id"), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("v1_permissions.permission_id"), primary_key=True)
