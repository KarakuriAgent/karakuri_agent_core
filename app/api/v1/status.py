from fastapi import APIRouter, Depends, HTTPException
from typing import Dict

from app.auth.api_key import get_api_key
from app.core.agent_manager import get_agent_manager
from app.schemas.status import AgentStatus, AgentStatusConfig
from app.schemas.schedule import DailySchedule
from app.core.schedule_service import ScheduleService
from app.core.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()
schedule_service = ScheduleService(llm_service=llm_service)


@router.get("/agents/{agent_id}/status")
async def get_agent_status(
    agent_id: str,
    api_key: str = Depends(get_api_key),
) -> AgentStatusConfig:
    """Get the current status of an agent"""
    agent_manager = get_agent_manager()
    try:
        agent = agent_manager.get_agent(agent_id)
        return agent.status
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.put("/agents/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status: AgentStatus,
    api_key: str = Depends(get_api_key),
) -> AgentStatusConfig:
    """Update the status of an agent"""
    agent_manager = get_agent_manager()
    try:
        agent = agent_manager.get_agent(agent_id)
        agent.status.current_status = status
        return agent.status
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.get("/agents/{agent_id}/schedule")
async def get_agent_schedule(
    agent_id: str,
    api_key: str = Depends(get_api_key),
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


@router.get("/agents/{agent_id}/availability")
async def get_agent_availability(
    agent_id: str,
    api_key: str = Depends(get_api_key),
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
