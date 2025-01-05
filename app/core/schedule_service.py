import asyncio
import json
from datetime import datetime, date, timedelta
from typing import Optional, Dict
import pytz
import logging

from app.core.config import get_settings
from app.core.llm_service import LLMService
from app.schemas.schedule import DailySchedule, ScheduleItem, ScheduleContext
from app.schemas.status import AgentStatus, CommunicationChannel, STATUS_AVAILABILITY
from app.schemas.agent import AgentConfig

settings = get_settings()
logger = logging.getLogger(__name__)


class ScheduleService:
    def __init__(self, llm_service: LLMService):
        self._schedule_cache: Dict[str, DailySchedule] = {}
        self._current_schedule: Dict[str, ScheduleItem] = {}
        self.llm_service = llm_service
        self._schedule_generation_task = None
        self._schedule_execution_task = None

        # Initialize schedules in a way that works with FastAPI's dependency injection
        self._initialized = False

    async def initialize(self):
        """Initialize schedules after the event loop is running"""
        if not self._initialized:
            await self._initialize_schedules()
            await self.start_schedule_execution()
            self._initialized = True

    async def _initialize_schedules(self):
        """Generate initial schedules on server startup"""
        from app.core.agent_manager import get_agent_manager

        agent_manager = get_agent_manager()
        for agent_id, agent in agent_manager.agents.items():
            try:
                local_time = self._get_agent_local_time(agent)
                schedule = await self.generate_daily_schedule(agent, local_time.date())
                self._schedule_cache[agent_id] = schedule
            except Exception as e:
                logger.error(
                    f"Initial schedule generation failed for agent {agent_id}: {e}"
                )

    async def start_schedule_generation(self):
        """Start the background task for schedule generation"""
        if self._schedule_generation_task is None:
            self._schedule_generation_task = asyncio.create_task(
                self.schedule_generation_task()
            )

    async def stop_schedule_generation(self):
        """Stop the background task"""
        if self._schedule_generation_task is not None:
            self._schedule_generation_task.cancel()
            try:
                await self._schedule_generation_task
            except asyncio.CancelledError:
                pass
            self._schedule_generation_task = None

    async def schedule_generation_task(self):
        """Background task for schedule generation"""
        while True:
            try:
                await self._check_and_generate_schedules()
                await asyncio.sleep(10)  # Check every minute
            except Exception as e:
                logger.error(f"Error in schedule generation task: {e}")
                await asyncio.sleep(10)  # Wait before retrying

    async def start_schedule_execution(self):
        """Start the background task for schedule execution"""
        if self._schedule_execution_task is None:
            self._schedule_execution_task = asyncio.create_task(
                self.schedule_execution_task()
            )

    async def stop_schedule_execution(self):
        """Stop the background task"""
        if self._schedule_execution_task is not None:
            self._schedule_execution_task.cancel()
            try:
                await self._schedule_execution_task
            except asyncio.CancelledError:
                pass
            self._schedule_execution_task = None

    async def schedule_execution_task(self):
        """Background task for schedule execution and status updates"""
        while True:
            try:
                await self._execute_current_schedules()
                await asyncio.sleep(10)  # Check every minute
            except Exception as e:
                logger.error(f"Error in schedule execution task: {e}")
                await asyncio.sleep(10)  # Wait before retrying

    async def _execute_current_schedules(self):
        """Execute current schedules and update agent statuses"""
        from app.core.agent_manager import get_agent_manager

        agent_manager = get_agent_manager()
        for agent_id, agent_config in agent_manager.agents.items():
            try:
                local_time = self._get_agent_local_time(agent_config)
                current_item = self._get_current_schedule_item(agent_config, local_time)
                if current_item:
                    self._current_schedule[agent_id] = current_item
                    logger.info(
                        f"Updated status for agent {agent_id} to {current_item.status}"
                    )

            except Exception as e:
                logger.error(f"Failed to execute schedule for agent {agent_id}: {e}")

    async def _check_and_generate_schedules(self):
        """Check and generate schedules for agents"""
        from app.core.agent_manager import get_agent_manager

        agent_manager = get_agent_manager()

        for agent_id, agent_config in agent_manager.agents.items():
            try:
                local_time = self._get_agent_local_time(agent_config)
                wake_time = datetime.strptime(
                    agent_config.schedule.wake_time, "%H:%M"
                ).time()
                schedule_gen_time = (
                    datetime.combine(date.today(), wake_time) - timedelta(minutes=30)
                ).time()

                if (
                    local_time.time().hour == schedule_gen_time.hour
                    and local_time.time().minute == schedule_gen_time.minute
                ):
                    tomorrow = local_time.date() + timedelta(days=1)
                    schedule = await self.generate_daily_schedule(
                        agent_config, tomorrow
                    )
                    self._schedule_cache[agent_id] = schedule

            except Exception as e:
                logger.error(f"Schedule generation failed for agent {agent_id}: {e}")

    async def generate_daily_schedule(
        self, agent_config: AgentConfig, target_date: date
    ) -> DailySchedule:
        """Generate a daily schedule for the agent"""
        schedule_prompt = self._create_schedule_prompt(agent_config, target_date)
        schedule_response = await self.llm_service.generate_schedule(
            schedule_prompt, agent_config
        )

        try:
            schedule_data = json.loads(schedule_response)
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

    def _create_schedule_prompt(
        self, agent_config: AgentConfig, target_date: date
    ) -> str:
        """Create prompt for schedule generation"""
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
        5. The schedule is in 30 minute increments.
        6. Consider the agent's personality and preferences

        Please generate a complete schedule following the specified format.
        """

    def _get_agent_local_time(self, agent_config: AgentConfig) -> datetime:
        """Get the current time in agent's timezone"""
        tz = pytz.timezone(agent_config.schedule.timezone)
        return datetime.now(tz)

    def get_current_availability(
        self, agent_config: AgentConfig, channel: CommunicationChannel
    ) -> bool:
        """Check if the communication channel is available in current status"""
        current_status = self._current_schedule[agent_config.id].status
        availability = STATUS_AVAILABILITY[current_status]
        return getattr(availability, channel.value)

    def _get_current_schedule_item(
        self, agent_config: AgentConfig, current_time: datetime
    ) -> Optional[ScheduleItem]:
        """Get current schedule item"""
        schedule = self._schedule_cache.get(agent_config.id)
        if not schedule:
            return None

        for item in schedule.items:
            start = datetime.strptime(item.start_time, "%H:%M").time()
            end = datetime.strptime(item.end_time, "%H:%M").time()
            if start <= current_time.time() <= end:
                return item

        return None

    def _get_next_available_schedule(
        self,
        agent_config: AgentConfig,
        channel: CommunicationChannel,
        current_time: datetime,
    ) -> Optional[ScheduleItem]:
        """Get next schedule item where the requested channel is available"""
        schedule = self._schedule_cache.get(agent_config.id)
        if not schedule:
            return None

        for item in schedule.items:
            start = datetime.strptime(item.start_time, "%H:%M").time()
            if start > current_time.time():
                availability = STATUS_AVAILABILITY[item.status]
                if (
                    (channel == CommunicationChannel.CHAT and availability.chat)
                    or (channel == CommunicationChannel.VOICE and availability.voice)
                    or (channel == CommunicationChannel.VIDEO and availability.video)
                ):
                    return item

        return None

    def get_current_schedule_context(
        self, agent_config: AgentConfig, communication_channel: CommunicationChannel
    ) -> ScheduleContext:
        current_time = self._get_agent_local_time(agent_config=agent_config)
        schedule = self._schedule_cache.get(agent_config.id)
        return ScheduleContext(
            available=self.get_current_availability(
                agent_config=agent_config, channel=communication_channel
            ),
            current_time=current_time,
            schedule=schedule,
        )

    def update_current_schedule(
        self, agent_config: AgentConfig, new_item: ScheduleItem
    ) -> None:
        schedule = self._schedule_cache[agent_config.id]
        for i, item in enumerate(schedule.items):
            if (
                item.start_time == new_item.start_time
                and item.end_time == new_item.end_time
            ):
                schedule.items[i] = new_item
                schedule.last_updated = datetime.now()
                break

        self._schedule_cache[agent_config.id] = schedule
        self._current_schedule[agent_config.id] = new_item

        logger.info(
            f"Updated current schedule for agent {agent_config.id} to {new_item.status}"
        )
