from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional


from app.auth.api_key import get_api_key
from app.core.agent_manager import get_agent_manager
from app.core.schedule_service import ScheduleService
from app.dependencies import get_schedule_service
from app.schemas.status import AgentStatus
from app.schemas.schedule import DailySchedule, ScheduleItem
from app.core.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()


@router.put("/{agent_id}/update")
async def update_agent_schedule(
    agent_id: str,
    activity: str,
    status: AgentStatus,
    description: Optional[str] = None,
    location: Optional[str] = None,
    api_key: str = Depends(get_api_key),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleItem:
    """Update the status of an agent"""
    agent_manager = get_agent_manager()

    try:
        agent_config = agent_manager.get_agent(agent_id=agent_id)
        current_time = schedule_service._get_agent_local_time(agent_config)
        current_schedule = schedule_service._get_current_schedule_item(
            agent_config=agent_config, current_time=current_time
        )
        if current_schedule:
            schedule_item = ScheduleItem(
                start_time=current_schedule.start_time,
                end_time=current_schedule.end_time,
                activity=activity,
                status=status,
                description=description,
                location=location,
            )
            schedule_service.update_current_schedule(agent_config, schedule_item)
            return schedule_item
        else:
            raise HTTPException(status_code=404, detail="Schedule not found")
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.get("/{agent_id}")
async def get_agent_schedule(
    agent_id: str,
    api_key: str = Depends(get_api_key),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> DailySchedule:
    """Get the current day's schedule for an agent"""
    agent_manager = get_agent_manager()
    try:
        agent_manager.get_agent(agent_id)  # Verify agent exists
        schedule = schedule_service._schedule_cache.get(agent_id)
        if not schedule:
            raise HTTPException(
                status_code=404,
                detail="Schedule not found. Wait for next schedule generation.",
            )
        return schedule
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.get("/agts/{agent_id}/availability")
async def get_agent_availability(
    agent_id: str,
    api_key: str = Depends(get_api_key),
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> Dict[str, bool]:
    """Get the current availability of all communication channels for an agent"""
    agent_manager = get_agent_manager()
    try:
        agent = agent_manager.get_agent(agent_id)
        from app.schemas.status import CommunicationChannel

        availability = {
            "chat": schedule_service.get_current_availability(
                agent, CommunicationChannel.CHAT
            ),
            "voice": schedule_service.get_current_availability(
                agent, CommunicationChannel.VOICE
            ),
            "video": schedule_service.get_current_availability(
                agent, CommunicationChannel.VIDEO
            ),
        }
        return availability
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")
