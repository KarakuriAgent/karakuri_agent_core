from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
import asyncio
from typing import Dict

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


class ScheduleHistory(BaseModel):
    """スケジュール履歴を保持するクラス"""

    schedule_item: ScheduleItem
    actual_start: datetime
    actual_end: datetime
    completion_status: str  # 'completed', 'interrupted', 'modified'
    notes: Optional[str] = None


class DynamicScheduleCache:
    """動的スケジュール管理用のキャッシュ"""

    def __init__(self):
        self._current_schedules: Dict[str, ScheduleItem] = {}
        self._next_schedules: Dict[str, ScheduleItem] = {}
        self._lock = asyncio.Lock()
