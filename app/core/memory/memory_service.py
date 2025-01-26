# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

import logging
import asyncio
from typing import List

from app.core.date_util import DateUtil
from app.schemas.llm import ToolDefinition
from app.schemas.memory import KarakuriMemory, AllMessageValues
from app.core.memory.valkey_client import ValkeyClient
from app.core.agent_manager import get_agent_manager
from app.core.config import get_settings
from app.core.memory.zep_client import ZepClient, create_zep_client
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)
settings = get_settings()
_valkey_client = ValkeyClient(settings.valkey_url, settings.valkey_password)
conversation_history_lock = asyncio.Lock()


class MemoryService:
    async def get_session_memory(
        self,
        agent_id: str,
        user_id: str,
        message_type: str,
    ) -> KarakuriMemory:
        session_key = self._create_session_key(agent_id, user_id, message_type)
        session_id = await _valkey_client.get_session_id(session_key)
        return await _valkey_client.get_memory(session_id, agent_id, user_id)

    async def update_session_memory(
        self,
        agent_id: str,
        user_id: str,
        message_type: str,
        conversation_history: List[AllMessageValues],
    ):
        async with conversation_history_lock:
            zep_client = self._create_zep_client(agent_id)
            messages = conversation_history[
                next(
                    (
                        i
                        for i, msg in reversed(list(enumerate(conversation_history)))
                        if msg["role"] == "user"
                    ),
                    0,
                ) :
            ]

            session_key = self._create_session_key(agent_id, user_id, message_type)
            session_id = await _valkey_client.get_session_id(session_key)
            await zep_client.add_memory(
                session_id=session_id,
                user_id=user_id,
                messages=messages,
            )
            memory = await zep_client.get_memory(
                session_id=session_id,
                lastn=30,
            )
            await _valkey_client.update_memory(session_id, memory)
            await _valkey_client.update_facts(agent_id, user_id, memory.facts or "")

    async def tool_call(
        self, agent_id: str, user_id: str, method_name: str, query: str
    ) -> str:
        if method_name == "search_facts":
            return "\n".join(await self.search_facts(agent_id, user_id, query))
        elif method_name == "search_nodes":
            return "\n".join(await self.search_nodes(agent_id, user_id, query))
        else:
            raise ValueError(f"Unsupported tool called: {method_name}")

    async def search_facts(self, agent_id: str, user_id: str, query: str) -> list[str]:
        zep_client = self._create_zep_client(agent_id)
        return await zep_client.search_facts(user_id, query)

    async def search_nodes(self, agent_id: str, user_id: str, query: str) -> list[str]:
        zep_client = self._create_zep_client(agent_id)
        return await zep_client.search_nodes(user_id, query)

    def _create_zep_client(self, agent_id: str) -> ZepClient:
        agent_config = get_agent_manager().get_agent(agent_id)
        return create_zep_client(
            base_url=agent_config.zep_url, api_key=agent_config.zep_api_secret
        )

    def _create_session_key(
        self, agent_id: str, user_id: str, message_type: str
    ) -> str:
        return f"karakuri_agent_{str(DateUtil.today())}_{agent_id}_{user_id}_{message_type}"

    async def add_user(self, agent_id: str, user_id: str):
        zep_client = self._create_zep_client(agent_id)
        await zep_client.add_user(user_id=user_id)

    async def delete_user(self, agent_id: str, user_id: str):
        zep_client = self._create_zep_client(agent_id)
        await zep_client.delete_user(user_id=user_id)

    async def get_user(self, agent_id: str, user_id: str) -> UserResponse:
        zep_client = self._create_zep_client(agent_id)
        return await zep_client.get_user(user_id=user_id)

    async def list_users(self, agent_id: str) -> List[UserResponse]:
        zep_client = self._create_zep_client(agent_id)
        return await zep_client.list_users()

    def get_support_tools(self, agent_id: str) -> List[ToolDefinition]:
        zep_client = self._create_zep_client(agent_id)
        return zep_client.get_support_tools()
