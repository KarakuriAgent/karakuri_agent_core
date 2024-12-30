import redis.asyncio as redis  # type: ignore
import json
import asyncio
from typing import List

from litellm import (
    AllMessageValues,
    ChatCompletionSystemMessage,
    model_cost,
    token_counter,  # type: ignore
)

from app.core.config import get_settings

settings = get_settings()
REDIS_URL = settings.redis_url
threshold_tokens_percentage = settings.threshold_tokens_percentage
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
conversation_history_lock = asyncio.Lock()


class MemoryService:
    async def get_conversation_history(self, agent_id: str) -> List[AllMessageValues]:
        key = f"conversation_history:{agent_id}"
        conversation_json = await redis_client.get(key)
        if conversation_json:
            return json.loads(conversation_json)
        return []

    async def update_conversation_history(
        self,
        model,
        agent_id: str,
        systemMessage: ChatCompletionSystemMessage,
        conversation_history: List[AllMessageValues],
    ):
        async with conversation_history_lock:
            try:
                max_tokens: int = model_cost[model]["max_input_tokens"] or 8192
            except Exception:
                max_tokens: int = 8192

            threshold = int(max_tokens * threshold_tokens_percentage)
            current_tokens = token_counter(
                model=model, messages=[systemMessage] + conversation_history[:]
            )
            if current_tokens > threshold:
                self._remove_first_user_to_next_user(conversation_history)
            key = f"conversation_history:{agent_id}"
            await redis_client.set(key, json.dumps(conversation_history))

    def _remove_first_user_to_next_user(
        self, conversation_history: List[AllMessageValues]
    ) -> None:
        first_user_index = None
        second_user_index = None
        user_count = 0
        for i, msg in enumerate(conversation_history):
            if msg["role"] == "user":
                user_count += 1
                if user_count == 1:
                    first_user_index = i
                elif user_count == 2:
                    second_user_index = i
                    break

        if first_user_index is None or second_user_index is None:
            return

        del conversation_history[first_user_index:second_user_index]
