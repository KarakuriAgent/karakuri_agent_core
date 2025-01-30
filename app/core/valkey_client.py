# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

import logging
import uuid
import json
import valkey.asyncio as valkey

from app.core.date_util import DateUtil
from app.schemas.memory import KarakuriMemory
from app.schemas.status import (
    ActiveStatusData,
    RestingStatusData,
    SleepingStatusData,
    Status,
    StatusType,
    TalkingStatusData,
)


logger = logging.getLogger(__name__)


class ValkeyClient:
    VALKEY_KEYS = {
        "SESSION_ID": "karakuri_agent_session_id",
        "MEMORY": "karakuri_agent_memory",
        "FACTS": "karakuri_agent_facts",
        "STATUS": "karakuri_agent_status",
    }

    def __init__(self, url: str, password: str):
        self._valkey_client = valkey.from_url(
            url, password=password, decode_responses=True
        )
        self._default_ttl = 60 * 60 * 24 * 7

    async def get_session_id(self, session_key: str) -> str:
        session_id = await self._valkey_client.get(
            f"{self.VALKEY_KEYS['SESSION_ID']}:{session_key}"
        )  # type: ignore
        if not session_id:
            session_id = f"{session_key}_{uuid.uuid4().hex}"
            await self._valkey_client.set(
                f"{self.VALKEY_KEYS['SESSION_ID']}:{session_key}", session_id
            )  # type: ignore
            await self._valkey_client.expire(
                f"{self.VALKEY_KEYS['SESSION_ID']}:{session_key}", self._default_ttl
            )
            return session_id
        else:
            return str(session_id)

    async def update_facts(self, agent_id: str, user_id: str, fact: str):
        await self._valkey_client.hset(
            self.VALKEY_KEYS["FACTS"], f"{agent_id}_{user_id}", fact
        )  # type: ignore

    async def get_facts(self, agent_id: str, user_id: str) -> str:
        return (
            await self._valkey_client.hget(
                self.VALKEY_KEYS["FACTS"], f"{agent_id}_{user_id}"
            )  # type: ignore
            or ""  # type: ignore
        )

    async def update_memory(self, session_id: str, memory: KarakuriMemory):
        await self._valkey_client.set(
            f"{self.VALKEY_KEYS['MEMORY']}:{session_id}", memory.model_dump_json()
        )  # type: ignore
        await self._valkey_client.expire(
            f"{self.VALKEY_KEYS['MEMORY']}:{session_id}", self._default_ttl
        )

    async def get_memory(
        self, session_id: str, agent_id: str, user_id: str
    ) -> KarakuriMemory:
        memory_json = await self._valkey_client.get(
            f"{self.VALKEY_KEYS['MEMORY']}:{session_id}"
        )  # type: ignore
        if memory_json:
            return KarakuriMemory.model_validate(json.loads(memory_json))
        else:
            facts = await self.get_facts(agent_id, user_id)
            return KarakuriMemory(messages=[], facts=facts, context=facts)

    async def update_current_status(self, agent_id: str, status: Status):
        await self._valkey_client.set(
            f"{self.VALKEY_KEYS['STATUS']}:{agent_id}", status.model_dump_json()
        )

    async def get_current_status(self, agent_id: str) -> Status:
        status_json = await self._valkey_client.get(
            f"{self.VALKEY_KEYS['STATUS']}:{agent_id}"
        )
        if status_json:
            data = json.loads(status_json)
            data["type"] = StatusType(data["type"])
            status_type = data["type"]
            if status_type == StatusType.ACTIVE:
                return ActiveStatusData.model_validate(data)
            elif status_type == StatusType.TALKING:
                return TalkingStatusData.model_validate(data)
            elif status_type == StatusType.RESTING:
                return RestingStatusData.model_validate(data)
            elif status_type == StatusType.SLEEPING:
                return SleepingStatusData.model_validate(data)
            else:
                raise ValueError(f"Unknown status type: {status_type}")
        else:
            return RestingStatusData(
                description="", started_at=DateUtil.now(), end_at=None, location=""
            )
