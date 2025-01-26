# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

import uuid
import json
import valkey.asyncio as valkey

from app.schemas.memory import KarakuriMemory


class ValkeyClient:
    VALKEY_KEYS = {
        "SESSION_ID": "karakuri_agent_session_id",
        "MEMORY": "karakuri_agent_memory",
        "FACTS": "karakuri_agent_facts",
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
            session_id = uuid.uuid4().hex
            await self._valkey_client.hset(
                self.VALKEY_KEYS["SESSION_ID"], session_key, session_id
            )  # type: ignore
            await self._valkey_client.hexpire(
                self.VALKEY_KEYS["SESSION_ID"], self._default_ttl, session_key
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
        await self._valkey_client.hset(
            self.VALKEY_KEYS["MEMORY"], session_id, memory.model_dump_json()
        )  # type: ignore
        await self._valkey_client.hexpire(
            self.VALKEY_KEYS["MEMORY"], self._default_ttl, session_id
        )

    async def get_memory(
        self, session_id: str, agent_id: str, user_id: str
    ) -> KarakuriMemory:
        memory_json = await self._valkey_client.hget(
            self.VALKEY_KEYS["MEMORY"], session_id
        )  # type: ignore
        if memory_json:
            return KarakuriMemory.model_validate(json.loads(memory_json))
        else:
            facts = await self.get_facts(agent_id, user_id)
            return KarakuriMemory(messages=[], facts=facts, context=facts)
