from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel

from app.schemas.status import AgentStatus


class ScheduleItem(BaseModel):
    start_time: str  # HH:MM format
    end_time: str  # HH:MM format
    activity: str
    status: AgentStatus
    description: Optional[str] = None
    location: Optional[str] = None


class DailySchedule(BaseModel):
    date: date
    items: List[ScheduleItem]
    generated_at: datetime
    last_updated: datetime


class AgentScheduleConfig(BaseModel):
    timezone: str = "Asia/Tokyo"
    wake_time: str = "08:00"
    sleep_time: str = "22:00"
    meal_times: List[dict[str, str]] = [
        {"start": "12:00", "end": "13:00"},
        {"start": "19:00", "end": "20:00"},
    ]
    custom_schedules: List[dict] = []  # For special events or custom schedules


class StatusContext(BaseModel):
    """Context for generating status responses"""

    available: bool
    current_time: datetime
    current_status: str
    current_schedule: Optional[ScheduleItem]
    next_schedule: Optional[ScheduleItem]
