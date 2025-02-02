# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

import asyncio
import logging
from app.core.agent_manager import get_agent_manager
from app.dependencies import (
    get_line_chat_client,
    get_llm_service,
    get_memory_service,
    get_tts_service,
    get_status_service,
)
from app.core.valkey_client import ValkeyClient
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def send_pending_messages():
    llm_service = get_llm_service()
    tts_service = get_tts_service()
    memory_service = get_memory_service()
    status_service = get_status_service()
    line_chat_client = get_line_chat_client()
    valkey_client = ValkeyClient(settings.valkey_url, settings.valkey_password)

    while True:
        try:
            agent_manager = get_agent_manager()
            for agent_id, _ in agent_manager.get_all_agents():
                try:
                    agent_config = agent_manager.get_agent(agent_id)

                    current_status = await status_service.get_current_status(agent_id)
                    if not current_status.is_chat_available:
                        continue

                    session_id = await valkey_client.get_session_id(agent_id)
                    if not session_id:
                        continue

                    pending_message = await valkey_client.get_pending_messages(
                        session_id
                    )
                    if not pending_message:
                        continue

                    line_chat_client.create(agent_config)

                    try:
                        await line_chat_client.process_and_send_messages(
                            pending_message.chat_messages,
                            agent_config,
                            llm_service,
                            tts_service,
                            memory_service,
                            pending_message.base_url,
                            use_reply=False,
                        )

                        await valkey_client.delete_pending_messages(session_id)

                    finally:
                        await line_chat_client.close()

                except Exception as e:
                    logger.error(f"Error processing messages for agent {agent_id}: {e}")
                    continue

            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Error in send_pending_messages: {e}")
            await asyncio.sleep(60)
