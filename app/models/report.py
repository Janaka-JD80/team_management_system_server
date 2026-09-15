import uuid
from sqlalchemy import Column, Date, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Report(Base):
    __tablename__ = "v1_reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("v1_users.user_id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("v1_projects.project_id"), nullable=True)
    week_start_date = Column(Date, nullable=False)
    week_end_date = Column(Date, nullable=False)
    
    current_status_id = Column(UUID(as_uuid=True), ForeignKey("v1_report_statuses.status_id"), nullable=False)
    current_version_num = Column(Integer, default=1, nullable=False)

    # Relationships
    user = relationship("User", back_populates="reports")
    project = relationship("Project", back_populates="reports")
    status = relationship("ReportStatus")
    versions = relationship("ReportVersion", back_populates="report", cascade="all, delete-orphan", order_by="desc(ReportVersion.version_num)")

    @property
    def latest_version(self):
        return self.versions[0] if self.versions else None

    @property
    def past_versions(self):
        return self.versions[1:] if self.versions and len(self.versions) > 1 else []

    @property
    def user_name(self):
        return self.user.full_name if self.user else None

    @property
    def project_name(self):
        return self.project.name if self.project else None
