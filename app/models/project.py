import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Project(Base):
    __tablename__ = "v1_projects"

    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    reports = relationship("Report", back_populates="project")
