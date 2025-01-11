import json
import logging
from typing import Any, List, Optional, Dict, Union
from datetime import datetime, time, timedelta
import asyncio

import pytz

from app.core.agent_manager import get_agent_manager
from app.core.llm_service import LLMService
from app.core.memory_service import MemoryService
from app.schemas.agent import AgentConfig
from app.schemas.schedule import (
    AgentScheduleConfig,
    ScheduleItem,
    ScheduleHistory,
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
                current_schedule = await self._generate_current_schedule(
                    agent_id, agent
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
                    end_time = datetime.strptime(
                        current_schedule.end_time, "%H:%M"
                    ).time()
                    current_time = local_time.time()

                    # スケジュール終了時刻を過ぎているかチェック
                    is_schedule_ended = current_time >= end_time

                    # 次のスケジュール生成が必要かチェック
                    minutes_until_end = (
                        datetime.combine(local_time.date(), end_time)
                        - datetime.combine(local_time.date(), current_time)
                    ).total_seconds() / 60
                    should_generate_next = minutes_until_end <= self.lookahead_minutes

                    if is_schedule_ended:
                        # スケジュールが終了した場合のみ履歴に追加
                        await self._add_completed_schedule_to_history(
                            agent_id, current_schedule, "completed"
                        )

                        # next_schedulesから次のスケジュールを取得して現在のスケジュールに設定
                        next_schedule = self.cache._next_schedules.get(agent_id)
                        if next_schedule:
                            self.cache._current_schedules[agent_id] = next_schedule
                            # Noneの代わりにキーを削除
                            if agent_id in self.cache._next_schedules:
                                del self.cache._next_schedules[agent_id]

                    if (
                        should_generate_next
                        and agent_id not in self.cache._next_schedules
                    ):
                        # 次のスケジュールを生成（まだ生成されていない場合）
                        next_schedule = await self._generate_next_schedule(
                            agent_id, agent, current_schedule
                        )
                        if next_schedule:
                            self.cache._next_schedules[agent_id] = next_schedule

            except Exception as e:
                logger.error(f"Error checking schedule for agent {agent_id}: {e}")

    async def stop_schedule_monitoring(self):
        """Stop schedule monitoring gracefully"""
        logger.info("Stopping schedule monitoring...")
        self._running = False

        # モニタリングタスクの停止
        if self._monitoring_task and not self._monitoring_task.done():
            try:
                self._monitoring_task.cancel()
                await self._monitoring_task
            except asyncio.CancelledError:
                logger.info("Schedule monitoring task cancelled")
            except Exception as e:
                logger.error(f"Error while stopping schedule monitoring: {e}")

        await self._cleanup_monitoring_tasks()
        logger.info("Schedule monitoring stopped")

    async def _cleanup_monitoring_tasks(self):
        """Clean up monitoring related tasks"""
        try:
            async with self.cache._lock:
                for agent_id, schedule in self.cache._current_schedules.items():
                    await self._add_completed_schedule_to_history(
                        agent_id=agent_id,
                        schedule=schedule,
                        completion_status="interrupted",
                        notes="Service shutdown",
                    )

        except Exception as e:
            logger.error(f"Error during monitoring cleanup: {e}")

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
        self, schedule_json: Union[str, Dict[str, Any]]
    ) -> ScheduleItem:
        """
        LLMからのスケジュールレスポンスをパース

        Args:
            schedule_json: JSON文字列またはdict

        Returns:
            ScheduleItem: パースされたスケジュールアイテム

        Raises:
            ValueError: パース失敗時
        """
        try:
            # 文字列の場合はdictに変換
            if isinstance(schedule_json, str):
                schedule_data = json.loads(schedule_json)
            else:
                schedule_data = schedule_json

            # 必須フィールドの存在確認
            required_fields = ["start_time", "end_time", "activity", "status"]
            missing_fields = [f for f in required_fields if f not in schedule_data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")

            # 時刻のバリデーション
            start_time = self._validate_time(schedule_data["start_time"])
            end_time = self._validate_time(schedule_data["end_time"])

            # statusの正規化（小文字に変換）
            status = schedule_data["status"].lower()
            if status not in [s.value for s in AgentStatus]:
                raise ValueError(f"Invalid status: {status}")

            # オプションフィールドのデフォルト値設定
            description = schedule_data.get("description", "")
            location = schedule_data.get("location", "")

            return ScheduleItem(
                start_time=start_time.strftime("%H:%M"),
                end_time=end_time.strftime("%H:%M"),
                activity=schedule_data["activity"],
                status=AgentStatus(status),
                description=description,
                location=location,
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
        except KeyError as e:
            logger.error(f"Missing required field: {e}")
            raise ValueError(f"Missing required field: {e}")
        except Exception as e:
            logger.error(f"Schedule parsing error: {e}")
            raise ValueError(f"Failed to parse schedule: {e}")

    def _validate_time(self, time_str: str) -> time:
        """
        時刻文字列を検証してdatetime.timeオブジェクトに変換

        Args:
            time_str: "HH:MM"形式の時刻文字列

        Returns:
            datetime.time: 変換された時刻オブジェクト

        Raises:
            ValueError: 無効な時刻形式
        """
        try:
            # 複数の一般的な時刻形式に対応
            for format_str in ["%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M%p"]:
                try:
                    return datetime.strptime(time_str, format_str).time()
                except ValueError:
                    continue

            # すべての形式で失敗した場合
            raise ValueError(f"Invalid time format: {time_str}")

        except Exception as e:
            logger.error(f"Time validation error: {e}")
            raise ValueError(f"Invalid time format: {time_str}")

    async def _generate_current_schedule(
        self, agent_id: str, agent: AgentConfig
    ) -> Optional[ScheduleItem]:
        """Generate current schedule based on current time"""
        try:
            current_time = self._get_local_time(agent.schedule)
            wake_time = self._parse_time(agent.schedule.wake_time)
            sleep_time = self._parse_time(agent.schedule.sleep_time)

            # Check if outside active hours
            if not self._is_within_active_hours(
                current_time.time(), wake_time, sleep_time
            ):
                return self._create_sleep_schedule(current_time, wake_time)

            # Get recent history
            recent_history = await self.memory_service.get_schedule_history(agent_id)

            # Create context for schedule generation
            context = {
                "recent_history": recent_history,
                "current_time": current_time,
                "agent_config": agent,
            }

            # Generate schedule using LLM
            schedule_json = await self.llm_service.generate_next_schedule(
                self._create_current_schedule_prompt(context), agent
            )

            # Parse response
            schedule = self._parse_schedule_response(schedule_json)

            # Log generated schedule
            logger.info(
                f"Generated current schedule for agent {agent_id}: "
                f"activity={schedule.activity}, "
                f"time={schedule.start_time}-{schedule.end_time}"
            )

            return schedule

        except Exception as e:
            logger.error(
                f"Failed to generate current schedule for agent {agent_id}: {e}"
            )
            return None

    async def _generate_next_schedule(
        self, agent_id: str, agent: AgentConfig, current_schedule: ScheduleItem
    ) -> Optional[ScheduleItem]:
        """Generate next schedule based on current schedule"""
        try:
            current_time = self._get_local_time(agent.schedule)
            wake_time = self._parse_time(agent.schedule.wake_time)
            sleep_time = self._parse_time(agent.schedule.sleep_time)

            end_time = datetime.strptime(current_schedule.end_time, "%H:%M").time()
            if end_time == sleep_time:
                return self._create_sleep_schedule(
                    datetime.combine(current_time.date(), end_time), wake_time
                )

            # Get recent history
            recent_history = await self.memory_service.get_schedule_history(agent_id)

            # Create context for next schedule generation
            context = {
                "recent_history": recent_history,
                "current_schedule": current_schedule,
                "current_time": current_time,
                "agent_config": agent,
            }

            # Generate next schedule using LLM
            next_schedule_json = await self.llm_service.generate_next_schedule(
                self._create_next_schedule_prompt(context), agent
            )

            # Parse response
            next_schedule = self._parse_schedule_response(next_schedule_json)

            # Log generated schedule
            logger.info(
                f"Generated next schedule for agent {agent_id}: "
                f"activity={next_schedule.activity}, "
                f"time={next_schedule.start_time}-{next_schedule.end_time}"
            )

            return next_schedule

        except Exception as e:
            logger.error(f"Failed to generate next schedule for agent {agent_id}: {e}")
            return None

    def _create_current_schedule_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for current schedule generation"""
        current_time = context["current_time"]
        wake_time = self._parse_time(context["agent_config"].schedule.wake_time)
        sleep_time = self._parse_time(context["agent_config"].schedule.sleep_time)

        recent_activities = "\n".join(
            [
                f"- {h.schedule_item.activity} ({h.completion_status})"
                for h in context["recent_history"][-5:]
            ]
        )

        return f"""
        Generate the current schedule for {context['agent_config'].name} based on the current time.
        Current time is {current_time.strftime("%H:%M")}.
        Agent is active between {wake_time.strftime("%H:%M")} and {sleep_time.strftime("%H:%M")}.
        
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

    def _create_next_schedule_prompt(self, context: Dict[str, Any]) -> str:
        """
        次のスケジュール生成用のプロンプトを作成

        Args:
            context: スケジュール生成に必要なコンテキスト情報

        Returns:
            str: 生成されたプロンプト
        """
        current_time = context["current_time"]
        wake_time = self._parse_time(context["agent_config"].schedule.wake_time)
        sleep_time = self._parse_time(context["agent_config"].schedule.sleep_time)

        recent_activities = "\n".join(
            [
                f"- {h.schedule_item.activity} ({h.completion_status})"
                for h in context["recent_history"][-5:]
            ]
        )

        return f"""
        You are an AI assistant that helps generate schedules for {context['agent_config'].name}.
        Here is the agent's personality and behavior guidelines:
        {context['agent_config'].llm_system_prompt}

        Current time is {current_time.strftime("%H:%M")}.
        Agent is active between {wake_time.strftime("%H:%M")} and {sleep_time.strftime("%H:%M")}.

        Current activity: {context['current_schedule'].activity if context['current_schedule'] else 'None'}
        
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
            "start_time": "HH:MM",
            "end_time": "HH:MM",
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
        else:  # 日付をまたぐ場合（例：wake_time=23:00, sleep_time=07:00）
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
    ) -> Optional[List[ScheduleHistory]]:
        """エージェントのスケジュール履歴を取得"""
        return await self.memory_service.get_schedule_history(agent_id)

    def _create_sleep_schedule(
        self, current_time: datetime, wake_time: time
    ) -> ScheduleItem:
        """Create sleep schedule when outside active hours"""
        next_wake_time = (
            datetime.combine(current_time.date() + timedelta(days=1), wake_time)
            if current_time.time() > wake_time
            else datetime.combine(current_time.date(), wake_time)
        )

        return ScheduleItem(
            start_time=current_time.strftime("%H:%M"),
            end_time=next_wake_time.strftime("%H:%M"),
            activity="睡眠",
            status=AgentStatus.SLEEPING,
            description="睡眠時間",
            location="自室",
        )

    async def _add_completed_schedule_to_history(
        self,
        agent_id: str,
        schedule: ScheduleItem,
        completion_status: str,
        notes: Optional[str] = None,
    ):
        """Add completed schedule to history with actual start and end times"""
        try:
            current_time = datetime.now()
            start_time = datetime.combine(
                current_time.date(),
                datetime.strptime(schedule.start_time, "%H:%M").time(),
            )

            # 実際の終了時間は現在時刻
            history = ScheduleHistory(
                schedule_item=schedule,
                actual_start=start_time,
                actual_end=current_time,
                completion_status=completion_status,
                notes=notes,
            )

            await self.memory_service.add_schedule_history(
                agent_id=agent_id,
                history=history,
                retention_hours=self.history_retention_hours,
            )

            logger.info(
                f"Added schedule history for agent {agent_id}: "
                f"activity={schedule.activity}, "
                f"status={completion_status}"
            )

        except Exception as e:
            logger.error(f"Failed to add schedule history for agent {agent_id}: {e}")
