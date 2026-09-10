from pydantic import BaseModel
from typing import Dict, List

class LineChartDataPoint(BaseModel):
    date: str
    value: int

class DashboardChartsResponse(BaseModel):
    time_by_task_type: Dict[str, float]
    tasks_completed_trend: List[LineChartDataPoint]

class DashboardSummaryResponse(BaseModel):
    total_submitted: int
    needs_correction: int
    open_blockers: int
