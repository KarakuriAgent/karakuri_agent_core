import uuid
import json
import redis.asyncio as redis  # type: ignore

from app.schemas.memory import KarakuriMemory


class RedisClient:
    REDIS_KEYS = {
        "SESSION_ID": "karakuri_agent_session_id",
        "MEMORY": "karakuri_agent_memory",
        "FACTS": "karakuri_agent_facts",
    }

    def __init__(self, url: str, password: str):
        self._redis_client = redis.from_url(
            url, password=password, decode_responses=True
        )
        self._default_ttl = 60 * 60 * 24 * 7

    async def get_session_id(self, session_key: str) -> str:
        session_id = await self._redis_client.hget(
            self.REDIS_KEYS["SESSION_ID"], session_key
        )  # type: ignore
        if not session_id:
            session_id = uuid.uuid4().hex
            await self._redis_client.hset(
                self.REDIS_KEYS["SESSION_ID"], session_key, session_id
            )  # type: ignore
            await self._redis_client.hexpire(
                self.REDIS_KEYS["SESSION_ID"], self._default_ttl, session_key
            )
            return session_id
        else:
            return str(session_id)

    async def update_facts(self, agent_id: str, user_id: str, fact: str):
        await self._redis_client.hset(
            self.REDIS_KEYS["FACTS"], f"{agent_id}_{user_id}", fact
        )  # type: ignore

    async def get_facts(self, agent_id: str, user_id: str) -> str:
        return (
            await self._redis_client.hget(
                self.REDIS_KEYS["FACTS"], f"{agent_id}_{user_id}"
            ) # type: ignore
            or ""  # type: ignore
        ) 

    async def update_memory(self, session_id: str, memory: KarakuriMemory):
        await self._redis_client.hset(
            self.REDIS_KEYS["MEMORY"], session_id, memory.model_dump_json()
        )  # type: ignore
        await self._redis_client.hexpire(
            self.REDIS_KEYS["MEMORY"], self._default_ttl, session_id
        )

    async def get_memory(
        self, session_id: str, agent_id: str, user_id: str
    ) -> KarakuriMemory:
        memory_json = await self._redis_client.hget(
            self.REDIS_KEYS["MEMORY"], session_id
        )  # type: ignore
        if memory_json:
            return KarakuriMemory.model_validate(json.loads(memory_json))
        else:
            facts = await self.get_facts(agent_id, user_id)
            return KarakuriMemory(messages=[], facts=facts, context=facts)
