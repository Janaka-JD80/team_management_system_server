from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class UserRole(Base):
    __tablename__ = "v1_user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("v1_users.user_id"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("v1_roles.role_id"), primary_key=True)
