import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Role(Base):
    __tablename__ = "v1_roles"

    role_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String, unique=True, index=True, nullable=False)
    role_description = Column(String, nullable=True)

    users = relationship("User", secondary="v1_user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="v1_role_permissions", back_populates="roles")
