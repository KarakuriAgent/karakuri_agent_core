from datetime import datetime, date, timedelta
import json
from typing import Dict, Optional
import pytz
import logging
import asyncio
from collections import defaultdict

from app.core.config import get_settings
from app.core.llm_service import LLMService
from app.schemas.schedule import (
    ScheduleItem,
    ScheduleContext,
    DailySchedule,
    AgentScheduleConfig,
)
from app.schemas.status import AgentStatus, CommunicationChannel, STATUS_AVAILABILITY
from app.schemas.agent import AgentConfig
from app.core.agent_manager import get_agent_manager

logger = logging.getLogger(__name__)
settings = get_settings()


class ScheduleCache:
    """スケジュールキャッシュを管理するクラス"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, DailySchedule]] = defaultdict(dict)
        self._current: Dict[str, ScheduleItem] = {}

    def get_schedule(self, agent_id: str) -> Optional[Dict[str, DailySchedule]]:
        return self._cache[agent_id]

    def set_schedule(self, agent_id: str, schedule: Dict[str, DailySchedule]):
        self._cache[agent_id] = schedule

    def get_daily_schedule(
        self, agent_id: str, date_key: str
    ) -> Optional[DailySchedule]:
        return self._cache[agent_id].get(date_key)

    def set_daily_schedule(self, agent_id: str, date_key: str, schedule: DailySchedule):
        self._cache[agent_id][date_key] = schedule

    def get_current_schedule(self, agent_id: str) -> Optional[ScheduleItem]:
        return self._current.get(agent_id)

    def set_current_schedule(self, agent_id: str, schedule: ScheduleItem):
        self._current[agent_id] = schedule


class ScheduleService:
    """エージェントのスケジュール管理を行うサービス"""

    def __init__(self, llm_service: LLMService):
        self.schedule_generation_task: Optional[asyncio.Task] = None
        self.schedule_execution_task: Optional[asyncio.Task] = None
        self.llm_service = llm_service
        self.cache = ScheduleCache()
        self._schedule_tasks: Dict[str, asyncio.Task] = {}
        self._initialized = False

    async def initialize(self):
        """サービスの初期化"""
        if not self._initialized:
            await self._initialize_schedules()
            await self._start_background_tasks()
            self._initialized = True

    async def shutdown(self):
        """サービスのシャットダウン"""
        for task in self._schedule_tasks.values():
            task.cancel()
        await asyncio.gather(*self._schedule_tasks.values(), return_exceptions=True)

    async def stop_schedule_generation(self):
        """スケジュール生成タスクを停止"""
        if self.schedule_generation_task and not self.schedule_generation_task.done():
            self.schedule_generation_task.cancel()
            try:
                await self.schedule_generation_task
            except asyncio.CancelledError:
                logger.info("Schedule generation task cancelled")
            self.schedule_generation_task = None

    async def stop_schedule_execution(self):
        """スケジュール実行タスクを停止"""
        if self.schedule_execution_task and not self.schedule_execution_task.done():
            self.schedule_execution_task.cancel()
            try:
                await self.schedule_execution_task
            except asyncio.CancelledError:
                logger.info("Schedule execution task cancelled")
            self.schedule_execution_task = None

    async def cleanup(self):
        """全てのスケジュール関連タスクを停止"""
        await self.stop_schedule_generation()
        await self.stop_schedule_execution()

    async def _initialize_schedules(self):
        """初期スケジュールの生成"""
        agent_manager = get_agent_manager()
        for agent_id, agent in agent_manager.agents.items():
            await self._generate_agent_schedules(agent_id, agent)

    async def _generate_agent_schedules(self, agent_id: str, agent: AgentConfig):
        """エージェントの今日と明日のスケジュールを生成"""
        try:
            local_time = self._get_local_time(agent.schedule)
            for delta in [0, 1]:  # 今日と明日
                target_date = local_time.date() + timedelta(days=delta)
                schedule = await self._generate_daily_schedule(agent, target_date)
                self.cache.set_daily_schedule(
                    agent_id, self._format_date_key(target_date), schedule
                )
        except Exception as e:
            logger.error(f"Failed to generate schedules for agent {agent_id}: {e}")

    async def _start_background_tasks(self):
        """バックグラウンドタスクの開始"""
        self._schedule_tasks.update(
            {
                "schedule_generation": asyncio.create_task(
                    self._schedule_generation_loop()
                ),
                "schedule_execution": asyncio.create_task(
                    self._schedule_execution_loop()
                ),
            }
        )

    async def _schedule_generation_loop(self):
        """スケジュール生成ループ"""
        while True:
            try:
                await self._generate_future_schedules()
                await asyncio.sleep(600)  # 10分間隔
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Schedule generation error: {e}")
                await asyncio.sleep(60)

    async def _schedule_execution_loop(self):
        """スケジュール実行ループ"""
        while True:
            try:
                await self._update_current_schedules()
                await asyncio.sleep(60)  # 1分間隔
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Schedule execution error: {e}")
                await asyncio.sleep(60)

    async def _generate_future_schedules(self):
        """将来のスケジュール生成"""
        agent_manager = get_agent_manager()
        tasks = [
            self._generate_agent_schedules(agent_id, agent)
            for agent_id, agent in agent_manager.agents.items()
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _update_current_schedules(self):
        """現在のスケジュール更新"""
        agent_manager = get_agent_manager()
        for agent_id, agent in agent_manager.agents.items():
            try:
                current_item = self._get_current_schedule_item(agent)
                if current_item:
                    self.cache.set_current_schedule(agent_id, current_item)
            except Exception as e:
                logger.error(f"Failed to update schedule for agent {agent_id}: {e}")

    async def _generate_daily_schedule(
        self, agent_config: AgentConfig, target_date: date
    ) -> DailySchedule:
        """1日分のスケジュール生成"""
        schedule_prompt = self._create_schedule_prompt(agent_config, target_date)
        schedule_json = await self.llm_service.generate_schedule(
            schedule_prompt, agent_config
        )
        return self._parse_schedule_response(schedule_json, target_date, agent_config)

    def get_current_schedule_context(
        self, agent_config: AgentConfig, communication_channel: CommunicationChannel
    ) -> ScheduleContext:
        """現在のスケジュールコンテキストを取得"""
        return ScheduleContext(
            available=self.get_current_availability(
                agent_config, communication_channel
            ),
            current_time=self._get_local_time(agent_config.schedule),
            schedule=self.get_today_schedule(agent_config),
        )

    def get_current_availability(
        self, agent_config: AgentConfig, channel: CommunicationChannel
    ) -> bool:
        """現在の利用可能状態を取得"""
        current_item = self.cache.get_current_schedule(agent_config.id)
        if not current_item:
            return False
        availability = STATUS_AVAILABILITY[current_item.status]
        return getattr(availability, channel.value)

    def get_today_schedule(self, agent_config: AgentConfig) -> Optional[DailySchedule]:
        """今日のスケジュールを取得"""
        current_time = self._get_local_time(agent_config.schedule)
        date_key = self._format_date_key(current_time.date())
        return self.cache.get_daily_schedule(agent_config.id, date_key)

    def get_current_schedule_item(
        self, agent_config: AgentConfig, current_time: Optional[datetime] = None
    ) -> Optional[ScheduleItem]:
        """現在のスケジュールアイテムを取得"""
        schedule = self.get_today_schedule(agent_config)
        if not schedule:
            return None

        if current_time is None:
            current_time = self.get_agent_local_time(agent_config.schedule)

        current_time_str = current_time.strftime("%H:%M")

        for item in schedule.items:
            if item.start_time <= current_time_str <= item.end_time:
                return item
        return None

    def _get_current_schedule_item(
        self, agent_config: AgentConfig
    ) -> Optional[ScheduleItem]:
        """内部使用の現在のスケジュールアイテム取得メソッド"""
        return self.get_current_schedule_item(agent_config)

    @staticmethod
    def get_agent_local_time(schedule_config: AgentScheduleConfig) -> datetime:
        """エージェントのローカル時間を取得"""
        tz = pytz.timezone(schedule_config.timezone)
        return datetime.now(tz)

    @staticmethod
    def _get_local_time(schedule_config: AgentScheduleConfig) -> datetime:
        """ローカル時間を取得"""
        return ScheduleService.get_agent_local_time(schedule_config)

    @staticmethod
    def _format_date_key(target_date: date) -> str:
        """日付キーをフォーマット"""
        return f"{target_date.month:02d}-{target_date.day:02d}"

    @staticmethod
    def _create_schedule_prompt(agent_config: AgentConfig, target_date: date) -> str:
        """スケジュール生成用プロンプトを作成"""
        return f"""
        Generate a daily schedule for {agent_config.name} for {target_date.strftime('%Y-%m-%d')}.
        
        Agent Profile:
        - Name: {agent_config.name}
        - Role: {agent_config.llm_system_prompt}
        - Active time: {agent_config.schedule.wake_time} ~ {agent_config.schedule.sleep_time}
        
        Requirements:
        1. Include regular daily activities and any special events
        2. Include appropriate work/activity periods
        3. End the day with wind-down activities before sleep time
        4. Create a schedule within active hours
        5. The schedule is in 30 minute increments
        6. Consider the agent's personality and preferences
        """

    def _parse_schedule_response(
        self, schedule_json: str, target_date: date, agent_config: AgentConfig
    ) -> DailySchedule:
        """スケジュールレスポンスをパース"""
        try:
            schedule_data = json.loads(schedule_json)
            for item in schedule_data["schedule"]:
                if "status" in item:
                    item["status"] = item["status"].lower()
            items = [
                ScheduleItem(
                    start_time="00:00",
                    end_time=agent_config.schedule.wake_time,
                    activity="Sleep",
                    status=AgentStatus.SLEEPING,
                    description="Sleeping comfortably.",
                    location="Bedroom",
                )
            ]
            items.extend(ScheduleItem(**item) for item in schedule_data["schedule"])
            items.append(
                ScheduleItem(
                    start_time=agent_config.schedule.sleep_time,
                    end_time="23:59",
                    activity="Sleep",
                    status=AgentStatus.SLEEPING,
                    description="Sleeping comfortably.",
                    location="Bedroom",
                )
            )
            return DailySchedule(
                date=target_date,
                items=items,
                generated_at=datetime.now(),
                last_updated=datetime.now(),
            )
        except Exception as e:
            logger.error(f"Failed to parse schedule response: {e}")
            raise

    def get_cached_schedule(self, agent_id: str) -> Optional[Dict[str, DailySchedule]]:
        """キャッシュされたスケジュールを取得"""
        return self.cache.get_schedule(agent_id)

    def set_cached_schedule(
        self, agent_id: str, schedule: Dict[str, DailySchedule]
    ) -> None:
        """スケジュールをキャッシュに設定"""
        self.cache.set_schedule(agent_id, schedule)

    def set_current_schedule(
        self, agent_config: AgentConfig, schedule_item: ScheduleItem
    ) -> None:
        """現在のスケジュールを更新"""
        agent_id = agent_config.id
        current_time = self._get_local_time(agent_config.schedule)
        date_key = self._format_date_key(current_time.date())
        
        daily_schedule = self.cache.get_daily_schedule(agent_id, date_key)
        if daily_schedule:
            current_time_str = current_time.strftime("%H:%M")
            updated_items = []
            
            for item in daily_schedule.items:
                if item.start_time <= current_time_str <= item.end_time:
                    updated_items.append(schedule_item)
                else:
                    updated_items.append(item)
            
            updated_schedule = DailySchedule(
                date=daily_schedule.date,
                items=updated_items,
                generated_at=daily_schedule.generated_at,
                last_updated=datetime.now()
            )
            
            self.cache.set_daily_schedule(agent_id, date_key, updated_schedule)
        
        self.cache.set_current_schedule(agent_id, schedule_item)

    def get_cached_current_schedule(self, agent_id: str) -> Optional[ScheduleItem]:
        """キャッシュされた現在のスケジュールアイテムを取得"""
        return self.cache.get_current_schedule(agent_id)
