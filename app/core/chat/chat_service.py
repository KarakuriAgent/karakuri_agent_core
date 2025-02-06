# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

import logging
from typing import List
from app.core.config import get_settings
from app.core.valkey_client import ValkeyClient
from app.schemas.chat_message import ChatMessage
from app.schemas.pending_message import PendingMessageContext

logger = logging.getLogger(__name__)
settings = get_settings()
_valkey_client = ValkeyClient(settings.valkey_url, settings.valkey_password)


class ChatServiceError(Exception):
    pass


class ChatService:
    async def update_pending_messages(
        self,
        agent_id: str,
        message_type: str,
        user_id: str,
        base_url: str,
        messages: List[ChatMessage],
    ):
        session_key = f"chat:{agent_id}:{user_id}"
        try:
            session_id = await _valkey_client.get_session_id(session_key)
            await _valkey_client.update_pending_messages(
                session_id, message_type, base_url, messages
            )
            logger.info(
                f"Saved {len(messages)} messages to Valkey for agent {agent_id}, user {user_id}"
            )
        except Exception as e:
            error_msg = f"Failed to update pending messages for agent {agent_id}, user {user_id}"
            logger.error(f"{error_msg}: {str(e)}")
            raise ChatServiceError(error_msg) from e

    async def get_pending_messages(
        self, agent_id: str, user_id: str
    ) -> PendingMessageContext | None:
        session_key = f"chat:{agent_id}:{user_id}"
        try:
            session_id = await _valkey_client.get_session_id(session_key)
            return await _valkey_client.get_pending_messages(session_id)
        except Exception as e:
            error_msg = (
                f"Failed to get pending messages for agent {agent_id}, user {user_id}"
            )
            logger.error(f"{error_msg}: {str(e)}")
            raise ChatServiceError(error_msg) from e

    async def delete_pending_messages(self, agent_id: str, user_id: str):
        session_key = f"chat:{agent_id}:{user_id}"
        try:
            session_id = await _valkey_client.get_session_id(session_key)
            await _valkey_client.delete_pending_messages(session_id)
        except Exception as e:
            error_msg = f"Failed to delete pending messages for agent {agent_id}, user {user_id}"
            logger.error(f"{error_msg}: {str(e)}")
            raise ChatServiceError(error_msg) from e

    async def is_chat_available(self, agent_id: str) -> bool:
        try:
            status = await _valkey_client.get_current_status(agent_id)
            if status:
                return status.is_chat_available
            return False
        except Exception as e:
            error_msg = f"Failed to check chat availability for agent {agent_id}"
            logger.error(f"{error_msg}: {str(e)}")
            raise ChatServiceError(error_msg) from e
