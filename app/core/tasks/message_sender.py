# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

import asyncio
import logging
from app.core.agent_manager import get_agent_manager
from app.dependencies import (
    get_chat_service,
    get_line_chat_client,
    get_llm_service,
    get_memory_service,
    get_tts_service,
)

logger = logging.getLogger(__name__)


async def send_pending_messages():
    llm_service = get_llm_service()
    tts_service = get_tts_service()
    memory_service = get_memory_service()
    chat_service = get_chat_service()
    line_chat_client = get_line_chat_client()
    agent_manager = get_agent_manager()

    while True:
        try:
            for agent_id, _ in agent_manager.get_all_agents():
                users = await memory_service.list_users(agent_id)
                for user in users:
                    try:
                        agent_config = agent_manager.get_agent(agent_id)

                        if not await chat_service.is_chat_available(agent_id):
                            continue

                        pending_message = await chat_service.get_pending_messages(
                            agent_id=agent_id, user_id=user.id
                        )
                        if not pending_message:
                            continue

                        line_chat_client.create(agent_config)

                        try:
                            await line_chat_client.process_and_send_messages(
                                pending_message.message_type,
                                pending_message.chat_messages,
                                agent_config,
                                user,
                                llm_service,
                                tts_service,
                                pending_message.base_url,
                                False,
                            )
                            await chat_service.delete_pending_messages(
                                agent_id=agent_id, user_id=user.id
                            )

                        finally:
                            await line_chat_client.close()

                    except Exception as e:
                        logger.error(
                            f"Error processing messages for agent {agent_id}: {e}"
                        )
                        continue

            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Error in send_pending_messages: {e}")
            await asyncio.sleep(60)
