from pydantic import BaseModel
from typing import Dict, List

class LineChartDataPoint(BaseModel):
    date: str
    value: int

class MemberStatus(BaseModel):
    user_id: str
    full_name: str
    status: str

class ActivityFeedItem(BaseModel):
    report_id: str
    full_name: str
    action: str
    timestamp: str

class DashboardChartsResponse(BaseModel):
    time_by_task_type: Dict[str, float]
    tasks_completed_trend: List[LineChartDataPoint]
    status_by_member: List[MemberStatus]
    workload_by_project: Dict[str, int]
    recent_activity: List[ActivityFeedItem]

class DashboardSummaryResponse(BaseModel):
    total_submitted: int
    needs_correction: int
    open_blockers: int
    compliance_rate: Dict[str, int]
