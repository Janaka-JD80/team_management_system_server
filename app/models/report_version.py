import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class ReportVersion(Base):
    __tablename__ = "v1_report_versions"

    version_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("v1_reports.report_id"), nullable=False)
    version_num = Column(Integer, nullable=False)
    status_id = Column(UUID(as_uuid=True), ForeignKey("v1_report_statuses.status_id"), nullable=False)
    manager_comment = Column(String, nullable=True)
    
    tasks_completed = Column(JSONB, default=list)
    tasks_planned = Column(JSONB, default=list)
    blockers = Column(JSONB, default=list)
    achievements = Column(JSONB, default=list)
    hours_worked_by_type = Column(JSONB, default=dict)
    
    optional_notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    report = relationship("Report", back_populates="versions")
    status = relationship("ReportStatus")
