from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from uuid import UUID
from datetime import date, datetime

class TaskCompleted(BaseModel):
    task_name: str
    priority: str
    planned_percent: int
    actual_percent: int
    status: str
    time_planned_hours: float
    time_spent_hours: float
    output_produced: Optional[str] = None

class TaskPlanned(BaseModel):
    task_name: str
    priority: str
    time_planned_hours: float

class Blocker(BaseModel):
    description: str
    is_key_issue: bool = False

class Achievement(BaseModel):
    description: str
    is_key_achievement: bool = False

class ReportStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status_id: UUID
    status_name: str
    description: Optional[str] = None

class ReportVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    version_id: UUID
    report_id: UUID
    version_num: int
    status: ReportStatusResponse
    manager_comment: Optional[str] = None
    tasks_completed: List[TaskCompleted] = []
    tasks_planned: List[TaskPlanned] = []
    blockers: List[Blocker] = []
    achievements: List[Achievement] = []
    hours_worked_by_type: Dict[str, float] = {}
    optional_notes: Optional[str] = None
    created_at: datetime

class ReportCreate(BaseModel):
    project_id: Optional[UUID] = None
    week_start_date: date
    week_end_date: date
    # Content for the initial draft
    tasks_completed: List[TaskCompleted] = []
    tasks_planned: List[TaskPlanned] = []
    blockers: List[Blocker] = []
    achievements: List[Achievement] = []
    hours_worked_by_type: Dict[str, float] = {}
    optional_notes: Optional[str] = None

class ReportUpdate(BaseModel):
    tasks_completed: Optional[List[TaskCompleted]] = None
    tasks_planned: Optional[List[TaskPlanned]] = None
    blockers: Optional[List[Blocker]] = None
    achievements: Optional[List[Achievement]] = None
    hours_worked_by_type: Optional[Dict[str, float]] = None
    optional_notes: Optional[str] = None
    
class ManagerReview(BaseModel):
    action: str # "APPROVE" or "REQUEST_CHANGES"
    comment: Optional[str] = None

class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    report_id: UUID
    user_id: UUID
    user_name: Optional[str] = None
    project_id: Optional[UUID] = None
    project_name: Optional[str] = None
    week_start_date: date
    week_end_date: date
    current_status_id: UUID
    current_version_num: int
    status: ReportStatusResponse

class ReportWithLatestVersionResponse(ReportResponse):
    # For getting the full report, we include the latest version content
    latest_version: ReportVersionResponse

class ReportSummaryResponse(BaseModel):
    user_id: UUID
    full_name: Optional[str] = None
    data: List[Any]
