# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
import asyncio
import logging
from app.core.status_service import StatusService
from app.core.agent_manager import get_agent_manager

logger = logging.getLogger(__name__)


async def check_conversation_timeouts():
    status_service = StatusService()
    agent_manager = get_agent_manager()

    while True:
        try:
            for agent_id, _ in agent_manager.get_all_agents():
                await status_service.check_conversation_timeout(agent_id)

            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error checking conversation timeouts: {e}")
            await asyncio.sleep(60)
