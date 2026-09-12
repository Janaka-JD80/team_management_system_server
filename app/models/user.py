import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "v1_users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    roles = relationship("Role", secondary="v1_user_roles", back_populates="users", lazy="selectin")
    reports = relationship("Report", back_populates="user")
