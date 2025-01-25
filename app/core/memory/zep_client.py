# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

from abc import ABC, abstractmethod
from typing import Optional, Sequence, Union
from fastapi import HTTPException
from litellm import (
    ChatCompletionUserMessage,
    ChatCompletionAssistantMessage,
    AllMessageValues,
)
import zep_python.client
import zep_cloud.client
from app.schemas.memory import KarakuriMemory
from app.schemas.user import UserResponse


class ZepClient(ABC):
    @abstractmethod
    async def add_session(self, user_id: str, session_id: str):
        pass

    @abstractmethod
    async def get_memory(self, session_id: str, lastn: int) -> KarakuriMemory:
        pass

    @abstractmethod
    async def add_memory(
        self, user_id: str, session_id: str, messages: list[AllMessageValues]
    ):
        pass

    @abstractmethod
    async def add_user(self, user_id: str):
        pass

    @abstractmethod
    async def delete_user(self, user_id: str):
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> UserResponse:
        pass

    @abstractmethod
    async def list_users(self) -> list[UserResponse]:
        pass


class ZepPythonClient(ZepClient):
    def __init__(self, base_url: str, api_key: str):
        self.client = zep_python.client.AsyncZep(base_url=base_url, api_key=api_key)

    async def add_session(self, user_id: str, session_id: str):
        try:
            await self.client.memory.add_session(user_id=user_id, session_id=session_id)
        except zep_python.BadRequestError as e:
            if "session already exists" not in str(e):
                # logger.error(f"Failed to add session: {e}")
                raise

    async def get_memory(self, session_id: str, lastn: int) -> KarakuriMemory:
        memory = await self.client.memory.get(session_id=session_id, lastn=lastn)
        context = (
            f"relevant_facts: ({','.join(fact.json() for fact in memory.relevant_facts)})"
            if memory.relevant_facts
            else ""
        )
        return KarakuriMemory(
            messages=_create_litellm_messages(memory),
            facts=context,
            context=context,
        )

    async def add_memory(
        self, user_id: str, session_id: str, messages: list[AllMessageValues]
    ):
        await self.add_session(
            session_id=session_id,
            user_id=user_id,
        )
        zep_messages = _create_zep_messeges(is_cloud=False, messages=messages)
        await self.client.memory.add(
            session_id=session_id,
            messages=zep_messages,  # type: ignore
        )

    async def add_user(self, user_id: str):
        await self.client.user.add(user_id=user_id)

    async def delete_user(self, user_id: str):
        await self.client.user.delete(user_id=user_id)

    async def get_user(self, user_id: str) -> UserResponse:
        user = await self.client.user.get(user_id=user_id)
        if not user.user_id:
            raise HTTPException(
                status_code=404, detail="User ID is required and cannot be empty"
            )
        return UserResponse(user_id=user.user_id)

    async def list_users(self) -> list[UserResponse]:
        response = await self.client.user.list_ordered()
        if not response or not response.users:
            return []
        return [
            UserResponse(user_id=user.user_id)
            for user in response.users
            if user.user_id is not None
        ]


class ZepCloudClient(ZepClient):
    def __init__(self, api_key: str):
        self.client = zep_cloud.client.AsyncZep(api_key=api_key)

    async def add_session(self, user_id: str, session_id: str):
        try:
            await self.client.memory.add_session(user_id=user_id, session_id=session_id)
        except zep_python.BadRequestError as e:
            if "session already exists" not in str(e):
                # logger.error(f"Failed to add session: {e}")
                raise

    async def get_memory(self, session_id: str, lastn: int) -> KarakuriMemory:
        memory = await self.client.memory.get(session_id=session_id, lastn=lastn)
        context = (
            "\n".join(
                fact.fact for fact in memory.relevant_facts if fact.fact is not None
            )
            if memory.relevant_facts
            else ""
        )
        facts = (
            f"relevant_facts: ({','.join(fact.json() for fact in memory.relevant_facts)})"
            if memory.relevant_facts
            else ""
        )
        return KarakuriMemory(
            messages=_create_litellm_messages(memory),
            facts=facts,
            context=context,
        )

    async def add_memory(
        self, user_id: str, session_id: str, messages: list[AllMessageValues]
    ):
        await self.add_session(user_id=user_id, session_id=session_id)
        zep_messages = _create_zep_messeges(is_cloud=True, messages=messages)
        await self.client.memory.add(
            session_id=session_id,
            messages=zep_messages,  # type: ignore
        )

    async def add_user(self, user_id: str):
        await self.client.user.add(user_id=user_id)

    async def delete_user(self, user_id: str):
        await self.client.user.delete(user_id=user_id)

    async def get_user(self, user_id: str) -> UserResponse:
        user = await self.client.user.get(user_id=user_id)
        if not user.user_id:
            raise HTTPException(
                status_code=404, detail="User ID is required and cannot be empty"
            )
        return UserResponse(user_id=user.user_id)

    async def list_users(self) -> list[UserResponse]:
        response = await self.client.user.list_ordered()
        if not response or not response.users:
            return []
        return [
            UserResponse(user_id=user.user_id)
            for user in response.users
            if user.user_id is not None
        ]


def create_zep_client(base_url: str, api_key: str) -> ZepClient:
    if base_url == "https://api.getzep.com":
        return ZepCloudClient(api_key)
    else:
        return ZepPythonClient(base_url, api_key)


def _create_litellm_messages(
    memory: Optional[zep_python.Memory | zep_cloud.Memory],
) -> list[AllMessageValues]:
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


def _create_zep_messeges(
    is_cloud: bool, messages: list[AllMessageValues]
) -> Sequence[Union[zep_python.Message, zep_cloud.Message]]:
    zep_messages = []
    last_user_index = -1
    for i in range(len(messages) - 1, -1, -1):
        if messages[i]["role"] == "user":
            last_user_index = i
            break
    for msg in messages[last_user_index:]:
        content = msg.get("content")
        if content is None:
            text_content = ""
        elif isinstance(content, str):
            text_content = content
        else:
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            text_content = " ".join(text_parts) if text_parts else ""

        message = (
            zep_cloud.Message(role_type=msg["role"], content=text_content)
            if is_cloud
            else zep_python.Message(role_type=msg["role"], content=text_content)
        )
        zep_messages.append(message)
    return zep_messages
