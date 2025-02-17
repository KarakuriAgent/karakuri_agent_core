# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import APIRouter, Depends, HTTPException
from app.auth.api_key import verify_token
from app.core.agent_manager import AgentManager, get_agent_manager
from app.dependencies import get_status_service
from app.schemas.agent import AgentResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/agents")
async def list_agents(
    api_key: str = Depends(verify_token),
    agent_manager: AgentManager = Depends(get_agent_manager),
):
    try:
        agents = agent_manager.get_all_agents()
        return [AgentResponse(agent_id=id, agent_name=name) for id, name in agents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agents: {str(e)}")


@router.get("/agents/{agent_id}/status")
async def get_agent_status(
    agent_id: str,
    api_key: str = Depends(verify_token),
    agent_manager: AgentManager = Depends(get_agent_manager),
):
    try:
        agent_config = agent_manager.get_agent(agent_id)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Agent with ID '{agent_id}' not found."
        )
    status_service = get_status_service()
    return await status_service.get_current_status(agent_config.id)
