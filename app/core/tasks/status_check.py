# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
import asyncio
import logging
from app.core.agent_manager import get_agent_manager
from app.dependencies import get_status_service

logger = logging.getLogger(__name__)


async def check_conversation_timeouts():
    status_service = get_status_service()
    agent_manager = get_agent_manager()

    while True:
        try:
            for agent_id, _ in agent_manager.get_all_agents():
                try:
                    await status_service.check_conversation_timeout(agent_id)
                except Exception as e:
                    logger.error(
                        f"Error checking conversation timeout for agent {agent_id}: {e}",
                        exc_info=True,
                    )
                    continue
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error in check_conversation_timeouts: {e}", exc_info=True)
            await asyncio.sleep(60)
