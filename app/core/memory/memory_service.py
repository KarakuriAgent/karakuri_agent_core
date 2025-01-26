# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

import redis.asyncio as redis  # type: ignore
import json
import asyncio
from typing import List
import logging
from app.core.date_util import DateUtil

from litellm import (
    AllMessageValues,
)

from app.core.config import get_settings
from app.core.memory.zep_client import create_zep_client
from app.schemas.memory import KarakuriMemory
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)
settings = get_settings()
zep_client = create_zep_client(
    base_url=settings.zep_url, api_key=settings.zep_api_secret
)
redis_client = redis.from_url(
    settings.redis_url, password=settings.redis_password, decode_responses=True
)
conversation_history_lock = asyncio.Lock()

REDIS_KEYS = {
    "FACTS": "facts",
}


class MemoryService:
    async def get_session_memory(
        self,
        agent_id: str,
        user_id: str,
        message_type: str,
    ) -> KarakuriMemory:
        memory_json = await redis_client.get(
            self._create_session_id(agent_id, user_id, message_type)
        )
        if memory_json:
            return KarakuriMemory.model_validate(json.loads(memory_json))
        else:
            facts_json = await redis_client.get(REDIS_KEYS["FACTS"]) or ""
            return KarakuriMemory(messages=[], facts=facts_json, context=facts_json)

    async def update_session_memory(
        self,
        agent_id: str,
        user_id: str,
        message_type: str,
        conversation_history: List[AllMessageValues],
    ):
        async with conversation_history_lock:
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

            session_id = self._create_session_id(agent_id, user_id, message_type)
            await zep_client.add_memory(
                session_id=session_id,
                user_id=user_id,
                messages=messages,
            )
            memory = await zep_client.get_memory(
                session_id=session_id,
                lastn=30,
            )
            await redis_client.set(session_id, memory.model_dump_json())
            await redis_client.set(REDIS_KEYS["FACTS"], memory.facts or "")

    def _create_session_id(self, agent_id: str, user_id: str, message_type: str) -> str:
        return f"{str(DateUtil.today())}_{agent_id}_{user_id}_{message_type}"

    async def add_user(self, user_id: str):
        await zep_client.add_user(user_id=user_id)

    async def delete_user(self, user_id: str):
        await zep_client.delete_user(user_id=user_id)

    async def get_user(self, user_id: str) -> UserResponse:
        return await zep_client.get_user(user_id=user_id)

    async def list_users(self) -> List[UserResponse]:
        return await zep_client.list_users()
