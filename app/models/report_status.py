import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class ReportStatus(Base):
    __tablename__ = "v1_report_statuses"

    status_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status_name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
