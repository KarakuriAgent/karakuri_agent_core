# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
import logging
import pytz
import redis.asyncio as redis  # type: ignore
import json
import asyncio
from typing import List
from datetime import datetime, timedelta

from litellm import (
    AllMessageValues,
    ChatCompletionSystemMessage,
    model_cost,
    token_counter,  # type: ignore
)

from app.core.config import get_settings
from app.schemas.schedule import ScheduleItem

settings = get_settings()
REDIS_URL = settings.redis_url
REDIS_PASSWORD = settings.redis_password
threshold_tokens_percentage = settings.threshold_tokens_percentage
redis_client = redis.from_url(REDIS_URL, password=REDIS_PASSWORD, decode_responses=True)
conversation_history_lock = asyncio.Lock()

logger = logging.getLogger(__name__)


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

    async def add_schedule_history(
        self, agent_id: str, history: ScheduleItem, timezone: str, retention_hours: int = 24
    ) -> None:
        """スケジュール履歴をRedisに追加し、古い履歴を削除"""
        key = f"schedule_history:{agent_id}"
        async with conversation_history_lock:
            existing_history = await self.get_schedule_history(agent_id)
            existing_history.append(history)
            existing_history = self._cleanup_old_history(
                existing_history, retention_hours, timezone
            )
            # BaseModelのjson()メソッドを使用
            await redis_client.set(
                key, json.dumps([h.model_dump_json() for h in existing_history])
            )

    async def get_schedule_history(self, agent_id: str) -> List[ScheduleItem]:
        """スケジュール履歴をRedisから取得"""
        key = f"schedule_history:{agent_id}"
        history_json = await redis_client.get(key)
        if history_json:
            # pydanticモデルとして解析
            return [
                ScheduleItem.model_validate_json(h) for h in json.loads(history_json)
            ]
        return []

    async def update_schedule_history(
        self, agent_id: str, history: ScheduleItem, timezone: str, retention_hours: int = 24
    ) -> None:
        key = f"schedule_history:{agent_id}"
        async with conversation_history_lock:
            existing_history = await self.get_schedule_history(agent_id)
            updated = False
            for i, h in enumerate(existing_history):
                if h.start_time == history.start_time:
                    existing_history[i] = history
                    updated = True
                    break
            if not updated:
                existing_history.append(history)
            existing_history = self._cleanup_old_history(
                existing_history, retention_hours, timezone
            )
            await redis_client.set(
                key, json.dumps([h.model_dump_json() for h in existing_history])
            )

    def _cleanup_old_history(
        self,  history: List[ScheduleItem], retention_hours: int, timezone: str,
    ) -> List[ScheduleItem]:
        """指定時間より古い履歴を削除"""
        cutoff_time = datetime.now(pytz.timezone(timezone)) - timedelta(hours=retention_hours)
        return [h for h in history if h.start_time > cutoff_time]

    async def delete_old_schedule_history(
        self, agent_id: str, retention_hours: int, timezone: str,
    ) -> int:
        key = f"schedule_history:{agent_id}"
        async with conversation_history_lock:
            existing_history = await self.get_schedule_history(agent_id)
            original_count = len(existing_history)
            cleaned_history = self._cleanup_old_history(
                existing_history, retention_hours, timezone
            )
            await redis_client.set(
                key, json.dumps([h.model_dump_json() for h in cleaned_history])
            )
            return original_count - len(cleaned_history)
