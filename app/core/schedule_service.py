import asyncio
import json
from datetime import datetime, date, timedelta
from typing import Optional, Dict
import pytz
import logging

from app.core.config import get_settings
from app.core.llm_service import LLMService
from app.schemas.schedule import DailySchedule, ScheduleItem, StatusContext
from app.schemas.status import CommunicationChannel, STATUS_AVAILABILITY
from app.schemas.agent import AgentConfig

settings = get_settings()
logger = logging.getLogger(__name__)


class ScheduleService:
    def __init__(self, llm_service: LLMService):
        self._schedule_cache: Dict[str, DailySchedule] = {}
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
                tomorrow = local_time.date() + timedelta(days=1)
                schedule = await self.generate_daily_schedule(agent, tomorrow)
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
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in schedule generation task: {e}")
                await asyncio.sleep(60)  # Wait before retrying

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
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in schedule execution task: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _execute_current_schedules(self):
        """Execute current schedules and update agent statuses"""
        from app.core.agent_manager import get_agent_manager

        agent_manager = get_agent_manager()
        for agent_id, agent_config in agent_manager.agents.items():
            try:
                local_time = self._get_agent_local_time(agent_config)
                current_item = self._get_current_schedule_item(agent_config, local_time)

                if (
                    current_item
                    and current_item.status != agent_config.status.current_status
                ):
                    updated_agent = agent_config.update_status(current_item.status)
                    agent_manager.update_agent(agent_id, updated_agent)
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
            items = [ScheduleItem(**item) for item in schedule_data["schedule"]]
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
        - Role: {self._extract_role_from_system_prompt(agent_config.llm_system_prompt)}
        - Wake time: {agent_config.schedule.wake_time}
        - Sleep time: {agent_config.schedule.sleep_time}
        - Regular meal times: {json.dumps(agent_config.schedule.meal_times)}

        Requirements:
        1. Schedule should start 30 minutes before wake time with preparation activities
        2. Include regular daily activities and any special events
        3. Account for meal times as specified
        4. Include appropriate work/activity periods
        5. End the day with wind-down activities before sleep time
        6. Consider the agent's personality and preferences

        Please generate a complete schedule following the specified format.
        """

    def _extract_role_from_system_prompt(self, system_prompt: str) -> str:
        """Extract role information from system prompt"""
        # This would need to be implemented based on your system prompt structure
        return "AI Assistant"  # Placeholder implementation

    def _get_agent_local_time(self, agent_config: AgentConfig) -> datetime:
        """Get the current time in agent's timezone"""
        tz = pytz.timezone(agent_config.schedule.timezone)
        return datetime.now(tz)

    def get_current_availability(
        self, agent_config: AgentConfig, channel: CommunicationChannel
    ) -> bool:
        """Check if the communication channel is available in current status"""
        current_status = agent_config.status.current_status
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

    def get_current_status_context(
        self, agent_config: AgentConfig, communication_channel: CommunicationChannel
    ) -> StatusContext:
        current_time = self._get_agent_local_time(agent_config=agent_config)
        current_schedule = self._get_current_schedule_item(agent_config, current_time)
        next_available = self._get_next_available_schedule(
            agent_config, communication_channel, current_time
        )
        return StatusContext(
            available=self.get_current_availability(
                agent_config=agent_config, channel=communication_channel
            ),
            current_time=current_time,
            current_status=agent_config.status.current_status,
            current_schedule=current_schedule,
            next_schedule=next_available,
        )
