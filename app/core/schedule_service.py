# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
import json
import logging
from typing import Any, List, Optional, Dict, Union
from datetime import datetime, time, timedelta
import asyncio

import pytz

from app.core import memory_service
from app.core.agent_manager import get_agent_manager
from app.core.llm_service import LLMService
from app.core.memory_service import MemoryService
from app.schemas import agent
from app.schemas.agent import AgentConfig
from app.schemas.schedule import (
    AgentScheduleConfig,
    ScheduleItem,
    DynamicScheduleCache,
)
from app.schemas.status import STATUS_AVAILABILITY, AgentStatus, CommunicationChannel

logger = logging.getLogger(__name__)


class ScheduleService:
    """動的スケジュール管理サービス"""

    def __init__(
        self,
        llm_service: LLMService,
        memory_service: MemoryService,
        lookahead_minutes: int = 30,
        history_retention_hours: int = 24,
    ):
        self.llm_service = llm_service
        self.memory_service = memory_service
        self.cache = DynamicScheduleCache()
        self.lookahead_minutes = lookahead_minutes
        self.history_retention_hours = history_retention_hours
        self._monitoring_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """Initialize schedule monitoring and generation"""
        agent_manager = get_agent_manager()
        for agent_id, agent in agent_manager.agents.items():
            try:
                history = await self.memory_service.get_schedule_history(agent_id)
                shutdown_schedule = history[-1] if history and history[-1].status == AgentStatus.SHUTDOWN else None
                
                if shutdown_schedule:
                    current_time = self._get_local_time(agent.schedule)
                    shutdown_schedule.end_time = current_time
                    await self.memory_service.update_schedule_history(
                        agent_id=agent_id,
                        history=shutdown_schedule,
                        timezone=agent.schedule.timezone,
                        retention_hours=self.history_retention_hours,
                    )
                    logger.info(f"Updated sleep schedule end_time for agent {agent_id}")

                current_schedule = await self._generate_current_schedule(
                    agent
                )
                if current_schedule:
                    self.cache._current_schedules[agent_id] = current_schedule
            except Exception as e:
                logger.error(f"Error initializing schedule for agent {agent_id}: {e}")

        if self._monitoring_task is None:
            self._monitoring_task = asyncio.create_task(
                self._schedule_monitoring_loop()
            )

    async def _schedule_monitoring_loop(self):
        """スケジュールモニタリングループ"""
        while True:
            try:
                await self._check_and_generate_next_schedules()
                await asyncio.sleep(60)
            except Exception:
                await asyncio.sleep(60)

    async def _check_and_generate_next_schedules(self):
        """Check and generate next schedules as needed"""
        agent_manager = get_agent_manager()
        for agent_id, agent in agent_manager.agents.items():
            try:
                current_schedule = self.cache._current_schedules.get(agent_id)
                if current_schedule:
                    local_time = self._get_local_time(agent.schedule)
                    end_time = current_schedule.end_time.time()
                    current_time = local_time.time()

                    is_schedule_ended = current_time >= end_time

                    minutes_until_end = (
                        datetime.combine(local_time.date(), end_time)
                        - datetime.combine(local_time.date(), current_time)
                    ).total_seconds() / 60
                    should_generate_next = minutes_until_end <= self.lookahead_minutes

                    if is_schedule_ended:
                        await self._add_completed_schedule_to_history(
                            agent_id, agent.schedule.timezone, current_schedule
                        )

                        next_schedule = self.cache._next_schedules.get(agent_id)
                        if next_schedule:
                            self.cache._current_schedules[agent_id] = next_schedule
                            if agent_id in self.cache._next_schedules:
                                del self.cache._next_schedules[agent_id]

                    if (
                        should_generate_next
                        and agent_id not in self.cache._next_schedules
                    ):
                        next_schedule = await self._generate_next_schedule(
                            agent, current_schedule
                        )
                        if next_schedule:
                            self.cache._next_schedules[agent_id] = next_schedule

            except Exception as e:
                logger.error(f"Error checking schedule for agent {agent_id}: {e}")

    async def stop_schedule_monitoring(self):
        """Stop schedule monitoring gracefully"""
        logger.info("Stopping schedule monitoring...")
        
        agent_manager = get_agent_manager()
        for agent_id, agent in agent_manager.agents.items():
            try:
                history = await self.memory_service.get_schedule_history(agent_id)
                shutdown_schedule = history[-1] if history and history[-1].status == AgentStatus.SHUTDOWN else None
                if shutdown_schedule:
                    return
                current_time = self._get_local_time(agent.schedule)
                shutdown_schedule = ScheduleItem(
                    start_time=current_time,
                    end_time=current_time,
                    activity="shutdown",
                    status=AgentStatus.SHUTDOWN,
                    description="shutdown",
                    location="None",
                    )

                await self._add_completed_schedule_to_history(
                    agent_id, agent.schedule.timezone, shutdown_schedule
                )
                logger.info(f"Added sleep schedule to history for agent {agent_id}")
            except Exception as e:
                logger.error(f"Error saving sleep schedule for agent {agent_id}: {e}")

        self._running = False

        if self._monitoring_task and not self._monitoring_task.done():
            try:
                self._monitoring_task.cancel()
                await self._monitoring_task
            except asyncio.CancelledError:
                logger.info("Schedule monitoring task cancelled")
            except Exception as e:
                logger.error(f"Error while stopping schedule monitoring: {e}")

        logger.info("Schedule monitoring stopped")

    def get_current_schedule(self, agent_id: str) -> Optional[ScheduleItem]:
        return self.cache._current_schedules.get(agent_id)

    async def update_current_schedule(
        self,
        agent_id: str,
        schedule_item: ScheduleItem,
    ):
        """現在のスケジュールを更新"""
        try:
            self.cache._current_schedules[agent_id] = schedule_item
        except Exception as e:
            logger.error(f"Failed to update schedule for agent {agent_id}: {e}")
            raise

    @staticmethod
    def get_agent_local_time(schedule_config: AgentScheduleConfig) -> datetime:
        """エージェントのローカル時間を取得"""
        tz = pytz.timezone(schedule_config.timezone)
        return datetime.now(tz)

    @staticmethod
    def _get_local_time(schedule_config: AgentScheduleConfig) -> datetime:
        """ローカル時間を取得"""
        return ScheduleService.get_agent_local_time(schedule_config)

    def _parse_schedule_response(
        self, schedule_json: Union[str, Dict[str, Any]], timezone: str
    ) -> ScheduleItem:
        try:
            if isinstance(schedule_json, str):
                schedule_data = json.loads(schedule_json)
            else:
                schedule_data = schedule_json

            required_fields = ["start_time", "end_time", "activity", "status"]
            missing_fields = [f for f in required_fields if f not in schedule_data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")

            start_time = self._validate_datetime(schedule_data["start_time"], timezone)
            end_time = self._validate_datetime(schedule_data["end_time"], timezone)

            status = schedule_data["status"].lower()
            if status not in [s.value for s in AgentStatus]:
                raise ValueError(f"Invalid status: {status}")

            description = schedule_data.get("description", "")
            location = schedule_data.get("location", "")

            return ScheduleItem(
                start_time=start_time,
                end_time=end_time,
                activity=schedule_data["activity"],
                status=AgentStatus(status),
                description=description,
                location=location,
            )
        except Exception as e:
            logger.error(f"Schedule parsing error: {e}")
            raise ValueError(f"Failed to parse schedule: {e}")

    def _validate_datetime(self, datetime_str: str, timezone: str) -> datetime:
        """
        日時文字列を検証してdatetimeオブジェクトに変換

        Args:
            datetime_str: "YYYY-MM-DD HH:MM"形式の日時文字列

        Returns:
            datetime: 変換された日時オブジェクト

        Raises:
            ValueError: 無効な日時形式
        """
        try:
            tz = pytz.timezone(timezone)
            return tz.localize(datetime.strptime(datetime_str, "%Y-%m-%d %H:%M"))
        except Exception as e:
            logger.error(f"Datetime validation error: {e}")
            raise ValueError(f"Invalid datetime format: {datetime_str}")

    async def _generate_current_schedule(
        self, agent_config: AgentConfig
    ) -> Optional[ScheduleItem]:
        """Generate current schedule based on current time"""
        try:
            current_time = self._get_local_time(agent_config.schedule)
            wake_time = self._parse_time(agent_config.schedule.wake_time)
            sleep_time = self._parse_time(agent_config.schedule.sleep_time)

            if not self._is_within_active_hours(
                current_time.time(), wake_time, sleep_time
            ):
                return self._create_sleep_schedule(current_time, wake_time, agent_config.schedule.timezone)

            prompt = await self._create_current_schedule_prompt(
                current_time, agent_config
            )
            schedule_json = await self.llm_service.generate_next_schedule(
                prompt, agent_config
            )

            schedule = self._parse_schedule_response(schedule_json, agent_config.schedule.timezone)

            logger.info(
                f"Generated current schedule for agent {agent_config.id}: "
                f"activity={schedule.activity}, "
                f"time={schedule.start_time}-{schedule.end_time}"
            )

            return schedule

        except Exception as e:
            logger.error(
                f"Failed to generate current schedule for agent {agent_config.id}: {e}"
            )
            return None

    async def _generate_next_schedule(
        self, agent_config: AgentConfig, current_schedule: ScheduleItem
    ) -> Optional[ScheduleItem]:
        """Generate next schedule based on current schedule"""
        try:
            current_time = self._get_local_time(agent_config.schedule)
            wake_time = self._parse_time(agent_config.schedule.wake_time)
            sleep_time = self._parse_time(agent_config.schedule.sleep_time)

            end_time = current_schedule.end_time.time()
            if end_time == sleep_time:
                return self._create_sleep_schedule(
                    datetime.combine(current_time.date(), end_time), wake_time, agent_config.schedule.timezone
                )

            prompt = await self._create_next_schedule_prompt(
                current_schedule, current_time, agent_config
            )

            next_schedule_json = await self.llm_service.generate_next_schedule(
                prompt, agent_config
            )

            next_schedule = self._parse_schedule_response(next_schedule_json, agent_config.schedule.timezone)

            logger.info(
                f"Generated next schedule for agent {agent_config.id}: "
                f"activity={next_schedule.activity}, "
                f"time={next_schedule.start_time}-{next_schedule.end_time}"
            )

            return next_schedule

        except Exception as e:
            logger.error(
                f"Failed to generate next schedule for agent {agent_config.id}: {e}"
            )
            return None

    async def _create_current_schedule_prompt(
        self, current_time: datetime, agent_config: AgentConfig
    ) -> str:
        """Create prompt for current schedule generation"""
        recent_history = await self.memory_service.get_schedule_history(agent_config.id)
        wake_time = self._parse_time(agent_config.schedule.wake_time)
        sleep_time = self._parse_time(agent_config.schedule.sleep_time)

        recent_activities = "\n".join([f"- {h.activity})" for h in recent_history[-5:]])

        return f"""
        Generate the current schedule for {agent_config.name} based on the current time.
        Current time is {current_time}.
        Agent is active between {wake_time} and {sleep_time}.
        
        Recent activity history:
        {recent_activities}
        
        Please generate an appropriate current activity considering:
        1. The current time
        2. The recent history of activities
        3. The agent's personality and behavior guidelines
        4. Natural flow of daily activities
        5. Appropriate time allocation
        
        Return the schedule in JSON format as specified.
        """

    async def _create_next_schedule_prompt(
        self,
        current_schedule: ScheduleItem,
        current_time: datetime,
        agent_config: AgentConfig,
    ) -> str:
        """
        次のスケジュール生成用のプロンプトを作成

        Args:
            context: スケジュール生成に必要なコンテキスト情報

        Returns:
            str: 生成されたプロンプト
        """
        recent_history = await self.memory_service.get_schedule_history(agent_config.id)
        wake_time = self._parse_time(agent_config.schedule.wake_time)
        sleep_time = self._parse_time(agent_config.schedule.sleep_time)

        recent_activities = "\n".join([f"- {h.activity})" for h in recent_history[-5:]])

        return f"""
        You are an AI assistant that helps generate schedules for {agent_config.name}.
        Here is the agent's personality and behavior guidelines:
        {agent_config.llm_system_prompt}

        Current time is {current_time}.
        Agent is active between {wake_time} and {sleep_time}.

        Current activity: {current_schedule.activity if current_schedule else 'None'}
        
        Recent activity history:
        {recent_activities}
        
        Please generate a natural next activity considering:
        1. The current time and activity
        2. The recent history of activities
        3. The agent's personality and behavior guidelines
        4. Natural flow and transitions between activities
        5. Appropriate time allocation for the activity
        
        Important Notes:
        - The activity should align with the agent's personality and role
        - Consider the agent's typical daily patterns and preferences
        - Ensure the activity makes sense in the current context
        - If the next activity extends beyond {sleep_time.strftime("%H:%M")}, end it at {sleep_time.strftime("%H:%M")} and schedule sleep
        
        Return the schedule in JSON format with the following fields:
        {{
            "start_time": "YYYY-MM-DD HH:MM",
            "end_time": "YYYY-MM-DD HH:MM",
            "activity": "Activity name",
            "status": "available/working/eating/etc",
            "description": "Brief description",
            "location": "Location"
        }}
        """

    def _parse_time(self, time_str: str) -> time:
        """時刻文字列をdatetime.timeオブジェクトに変換"""
        return datetime.strptime(time_str, "%H:%M").time()

    def _is_within_active_hours(
        self, current_time: time, wake_time: time, sleep_time: time
    ) -> bool:
        """現在時刻が活動時間内かどうかをチェック"""
        if wake_time <= sleep_time:
            return wake_time <= current_time <= sleep_time
        else:
            return current_time >= wake_time or current_time <= sleep_time

    def get_current_availability(
        self, agent_config: AgentConfig, channel: CommunicationChannel
    ) -> bool:
        """Get the current availability of an agent for a specific communication channel"""
        current_item = self.get_current_schedule(agent_config.id)
        if not current_item:
            return False
        availability = STATUS_AVAILABILITY[current_item.status]
        return getattr(availability, channel.value)

    async def get_agent_schedule_history(
        self, agent_id: str
    ) -> Optional[List[ScheduleItem]]:
        """エージェントのスケジュール履歴を取得"""
        return await self.memory_service.get_schedule_history(agent_id)

    def _create_sleep_schedule(
        self, current_time: datetime, wake_time: time, timezone: str
    ) -> ScheduleItem:
        """Create sleep schedule when outside active hours"""
        next_wake_time = (
            datetime.combine(current_time.date() + timedelta(days=1), wake_time)
            if current_time.time() > wake_time
            else datetime.combine(current_time.date(), wake_time)
        )
        tz = pytz.timezone(timezone)
        return ScheduleItem(
            start_time=current_time,
            end_time=tz.localize(next_wake_time),
            activity="sleeping",
            status=AgentStatus.SLEEPING,
            description="sleep time",
            location="bead room",
        )

    async def _add_completed_schedule_to_history(
        self,
        agent_id: str,
        timezone: str,
        schedule: ScheduleItem,
    ):
        """Add completed schedule to history with actual start and end times"""
        try:
            await self.memory_service.add_schedule_history(
                agent_id=agent_id,
                history=schedule,
                timezone=timezone,
                retention_hours=self.history_retention_hours,
            )

            logger.info(
                f"Added schedule history for agent {agent_id}: "
                f"activity={schedule.activity}, "
            )

        except Exception as e:
            logger.error(f"Failed to add schedule history for agent {agent_id}: {e}")
