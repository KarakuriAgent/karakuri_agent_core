# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional, List

import pytz
from app.auth.api_key import get_api_key
from app.core.agent_manager import get_agent_manager
from app.core.schedule_service import ScheduleService
from app.core.service_factory import ServiceFactory
from app.schemas.status import AgentStatus
from app.schemas.schedule import ScheduleItem

router = APIRouter()
service_factory = ServiceFactory()


@router.put("/{agent_id}/update")
async def update_agent_schedule(
    agent_id: str,
    activity: str,
    status: AgentStatus,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    api_key: str = Depends(get_api_key),
    schedule_service: ScheduleService = Depends(service_factory.get_schedule_service),
) -> ScheduleItem:
    """Update the status of an agent"""
    agent_manager = get_agent_manager()

    try:
        agent_config = agent_manager.get_agent(agent_id=agent_id)
        current_schedule = schedule_service.get_current_schedule(agent_config.id)
        tz = pytz.timezone(agent_config.schedule.timezone)
        if current_schedule:
            if end_time:
                current_end_time: datetime = datetime.strptime(
                    end_time, "%Y-%m-%dT%H:%M:%S"
                )
            else:
                current_end_time: datetime = current_schedule.end_time
            schedule_item = ScheduleItem(
                start_time=tz.localize(current_schedule.start_time),
                end_time=tz.localize(current_end_time),
                activity=activity,
                status=status,
                description=description,
                location=location,
            )
            await schedule_service.update_current_schedule(
                agent_id=agent_config.id,
                schedule_item=schedule_item,
            )
            return schedule_item
        else:
            raise HTTPException(status_code=404, detail="Schedule not found")
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.get("/{agent_id}")
async def get_agent_schedule(
    agent_id: str,
    api_key: str = Depends(get_api_key),
    schedule_service: ScheduleService = Depends(service_factory.get_schedule_service),
) -> ScheduleItem:
    """Get the current day's schedule for an agent"""
    agent_manager = get_agent_manager()
    try:
        agent_manager.get_agent(agent_id)  # Verify agent exists
        schedule = schedule_service.get_current_schedule(agent_id)
        if not schedule:
            raise HTTPException(
                status_code=404,
                detail="Schedule not found. Wait for next schedule generation.",
            )
        return schedule
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.get("/history/{agent_id}")
async def get_agent_schedule_history(
    agent_id: str,
    api_key: str = Depends(get_api_key),
    schedule_service: ScheduleService = Depends(service_factory.get_schedule_service),
) -> Optional[List[ScheduleItem]]:
    """Get the schedule history for an agent"""
    agent_manager = get_agent_manager()
    try:
        agent_manager.get_agent(agent_id)
        history = await schedule_service.get_agent_schedule_history(agent_id)
        return history
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.get("/agts/{agent_id}/availability")
async def get_agent_availability(
    agent_id: str,
    api_key: str = Depends(get_api_key),
    schedule_service: ScheduleService = Depends(service_factory.get_schedule_service),
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
