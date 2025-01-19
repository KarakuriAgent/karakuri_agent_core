# import redis.asyncio as redis  # type: ignore
# import json
import asyncio
from typing import List
from zep_python.client import AsyncZep
from zep_python.types import Message

from litellm import (
    AllMessageValues,
    ChatCompletionAssistantMessage,
    ChatCompletionSystemMessage,
    ChatCompletionUserMessage,
    # model_cost,
    # token_counter,  # type: ignore
)

from app.core.config import get_settings

settings = get_settings()
# threshold_tokens_percentage = settings.threshold_tokens_percentage
# redis_client = redis.from_url(
#     settings.redis_url, password=settings.redis_password, decode_responses=True
# )
zep_client = AsyncZep(base_url=settings.zep_url, api_key=settings.zep_api_secret)
conversation_history_lock = asyncio.Lock()


class MemoryService:
    async def get_conversation_history(self, agent_id: str) -> List[AllMessageValues]:
        try:
            memory = await zep_client.memory.get(session_id=agent_id)
            conversation_history = []
            if memory and memory.messages:
                for msg in memory.messages:
                    if msg.role_type == "user":
                        conversation_history.append(
                            ChatCompletionUserMessage(
                                role=msg.role_type,
                                content=msg.content if msg.content is not None else "",
                            )
                        )
                    elif msg.role_type == "assistant":
                        conversation_history.append(
                            ChatCompletionAssistantMessage(
                                role=msg.role_type,
                                content=msg.content if msg.content is not None else "",
                            )
                        )
            return conversation_history
        except Exception:
            return []

    async def update_conversation_history(
        self,
        model,
        agent_id: str,
        systemMessage: ChatCompletionSystemMessage,
        conversation_history: List[AllMessageValues],
    ):
        async with conversation_history_lock:
            # TODO over token
            # try:
            #     max_tokens: int
            #     max_tokens = model_cost[model]["max_input_tokens"] or 8192
            # except Exception:
            #     max_tokens = 8192

            # threshold = int(max_tokens * threshold_tokens_percentage)
            # current_tokens = token_counter(
            #     model=model, messages=[systemMessage] + conversation_history[:]
            # )
            # if current_tokens > threshold:
            #     self._remove_first_user_to_next_user(conversation_history)

            zep_messages = []
            last_user_index = -1
            for i in range(len(conversation_history) - 1, -1, -1):
                if conversation_history[i]["role"] == "user":
                    last_user_index = i
                    break
            for msg in conversation_history[last_user_index:]:
                content = msg.get("content")
                if content is None:
                    text_content = None
                elif isinstance(content, str):
                    text_content = content
                else:
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                    text_content = " ".join(text_parts) if text_parts else None

                zep_messages.append(
                    Message(role_type=msg["role"], content=text_content)
                )

            await zep_client.memory.add(session_id=agent_id, messages=zep_messages)

    # def _remove_first_user_to_next_user(
    #     self, conversation_history: List[AllMessageValues]
    # ) -> None:
    #     first_user_index = None
    #     second_user_index = None
    #     user_count = 0
    #     for i, msg in enumerate(conversation_history):
    #         if msg["role"] == "user":
    #             user_count += 1
    #             if user_count == 1:
    #                 first_user_index = i
    #             elif user_count == 2:
    #                 second_user_index = i
    #                 break

    #     if first_user_index is None or second_user_index is None:
    #         return

    #     del conversation_history[first_user_index:second_user_index]
