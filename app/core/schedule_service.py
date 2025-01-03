import asyncio
import json
from datetime import datetime, date, timedelta
from typing import Optional, Dict
import pytz
import logging

from app.core.config import get_settings
from app.core.llm_service import LLMService
from app.schemas.schedule import DailySchedule, ScheduleItem
from app.schemas.status import CommunicationChannel, STATUS_AVAILABILITY
from app.schemas.agent import AgentConfig

settings = get_settings()
logger = logging.getLogger(__name__)


class ScheduleService:
    def __init__(self, llm_service: LLMService):
        self._schedule_cache: Dict[str, DailySchedule] = {}
        self.llm_service = llm_service
        self._schedule_generation_task = None
        
        asyncio.create_task(self._initialize_schedules())

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
                logger.error(f"Initial schedule generation failed for agent {agent_id}: {e}")

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

    async def _check_and_generate_schedules(self):
        """Check and generate schedules for agents"""
        from app.core.agent_manager import get_agent_manager

        agent_manager = get_agent_manager()

        for agent_id, agent in agent_manager.agents.items():
            try:
                local_time = self._get_agent_local_time(agent)
                wake_time = datetime.strptime(agent.schedule.wake_time, "%H:%M").time()
                schedule_gen_time = (
                    datetime.combine(date.today(), wake_time) - timedelta(minutes=30)
                ).time()

                if (
                    local_time.time().hour == schedule_gen_time.hour
                    and local_time.time().minute == schedule_gen_time.minute
                ):
                    tomorrow = local_time.date() + timedelta(days=1)
                    schedule = await self.generate_daily_schedule(agent, tomorrow)
                    self._schedule_cache[agent_id] = schedule

            except Exception as e:
                logger.error(f"Schedule generation failed for agent {agent_id}: {e}")

    async def generate_daily_schedule(
        self, agent: AgentConfig, target_date: date
    ) -> DailySchedule:
        """Generate a daily schedule for the agent"""
        schedule_prompt = self._create_schedule_prompt(agent, target_date)
        schedule_response = await self.llm_service.generate_schedule(schedule_prompt)

        try:
            schedule_data = json.loads(schedule_response)
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

    def _create_schedule_prompt(self, agent: AgentConfig, target_date: date) -> str:
        """Create prompt for schedule generation"""
        return f"""
        Generate a daily schedule for {agent.name} for {target_date.strftime('%Y-%m-%d')}.

        Agent Profile:
        - Name: {agent.name}
        - Role: {self._extract_role_from_system_prompt(agent.llm_system_prompt)}
        - Wake time: {agent.schedule.wake_time}
        - Sleep time: {agent.schedule.sleep_time}
        - Regular meal times: {json.dumps(agent.schedule.meal_times)}

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

    def _get_agent_local_time(self, agent: AgentConfig) -> datetime:
        """Get the current time in agent's timezone"""
        tz = pytz.timezone(agent.schedule.timezone)
        return datetime.now(tz)

    def get_current_availability(
        self, agent: AgentConfig, channel: CommunicationChannel
    ) -> bool:
        """Check if the communication channel is available in current status"""
        current_status = agent.status.current_status
        availability = STATUS_AVAILABILITY[current_status]
        return getattr(availability, channel.value)

    async def generate_status_response(
        self,
        agent: AgentConfig,
        channel: CommunicationChannel,
        user_message: str,
        lang: str = "ja",
    ) -> str:
        """Generate contextual status response using LLM"""
        current_time = self._get_agent_local_time(agent)
        current_schedule = self._get_current_schedule_item(agent, current_time)
        next_available = self._get_next_available_schedule(agent, channel, current_time)

        context = {
            "current_time": current_time.strftime("%H:%M"),
            "current_status": agent.status.current_status,
            "current_activity": (
                current_schedule.activity
                if current_schedule
                else "No specific activity"
            ),
            "location": (
                current_schedule.location if current_schedule else "Not specified"
            ),
            "next_available": (
                next_available.start_time if next_available else "Not determined"
            ),
            "user_message": user_message,
            "agent_profile": agent.llm_system_prompt,
            "language": "Japanese" if lang == "ja" else "English",
        }

        return await self.llm_service.generate_status_response(context)

    def _get_current_schedule_item(
        self, agent: AgentConfig, current_time: datetime
    ) -> Optional[ScheduleItem]:
        """Get current schedule item"""
        schedule = self._schedule_cache.get(agent.id)
        if not schedule:
            return None

        for item in schedule.items:
            start = datetime.strptime(item.start_time, "%H:%M").time()
            end = datetime.strptime(item.end_time, "%H:%M").time()
            if start <= current_time.time() <= end:
                return item

        return None

    def _get_next_available_schedule(
        self, agent: AgentConfig, channel: CommunicationChannel, current_time: datetime
    ) -> Optional[ScheduleItem]:
        """Get next schedule item where the requested channel is available"""
        schedule = self._schedule_cache.get(agent.id)
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
