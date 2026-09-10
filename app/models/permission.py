import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Permission(Base):
    __tablename__ = "v1_permissions"

    permission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    permission_name = Column(String, unique=True, index=True, nullable=False)
    permission_description = Column(String, nullable=True)

    roles = relationship("Role", secondary="v1_role_permissions", back_populates="permissions")
