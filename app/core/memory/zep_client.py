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
from app.schemas.llm import ToolDefinition
from app.schemas.memory import KarakuriMemory
from app.schemas.user import UserConfig

tool_search_facts: ToolDefinition = {
    "type": "function",
    "function": {
        "name": "search_facts",
        "description": "Search user's facts",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search query"}},
            "required": ["query"],
        },
    },
}

tool_search_nodes: ToolDefinition = {
    "type": "function",
    "function": {
        "name": "search_nodes",
        "description": "Search user's memory nodes",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search query"}},
            "required": ["query"],
        },
    },
}


class ZepClient(ABC):
    @abstractmethod
    def get_support_tools(self) -> list[ToolDefinition]:
        pass

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
    async def add_user(self, user_id: str, last_name: str, first_name: str):
        pass

    @abstractmethod
    async def delete_user(self, user_id: str):
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> UserConfig:
        pass

    @abstractmethod
    async def list_users(self) -> list[UserConfig]:
        pass

    @abstractmethod
    async def search_facts(self, user_id: str, query: str, limit: int = 5) -> list[str]:
        pass

    @abstractmethod
    async def search_nodes(self, user_id: str, query: str, limit: int = 5) -> list[str]:
        pass


class ZepPythonClient(ZepClient):
    def __init__(self, base_url: str, api_key: str):
        self.client = zep_python.client.AsyncZep(base_url=base_url, api_key=api_key)

    def get_support_tools(self) -> list[ToolDefinition]:
        return [tool_search_facts]

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

    async def add_user(self, user_id: str, last_name: str, first_name: str):
        await self.client.user.add(
            user_id=user_id, first_name=first_name, last_name=last_name
        )

    async def delete_user(self, user_id: str):
        await self.client.user.delete(user_id=user_id)

    async def get_user(self, user_id: str) -> UserConfig:
        user = await self.client.user.get(user_id=user_id)
        if not user.user_id:
            raise HTTPException(
                status_code=404, detail="User ID is required and cannot be empty"
            )
        return UserConfig(
            id=user.user_id,
            last_name=user.last_name or "user",
            first_name=user.first_name or "user",
        )

    async def list_users(self) -> list[UserConfig]:
        response = await self.client.user.list_ordered()
        if not response or not response.users:
            return []
        return [
            UserConfig(
                id=user.user_id,
                last_name=user.last_name or "user",
                first_name=user.first_name or "user",
            )
            for user in response.users
            if user.user_id is not None
        ]

    async def search_facts(self, user_id: str, query: str, limit: int = 5) -> list[str]:
        edges = await self.client.memory.search_sessions(
            user_id=user_id, text=query, limit=limit, search_scope="facts"
        )
        if edges.results is None:
            return []
        return [
            edge.fact.fact
            for edge in edges.results
            if edge.fact is not None and edge.fact.fact is not None
        ]

    async def search_nodes(self, user_id: str, query: str, limit: int = 5) -> list[str]:
        return []


class ZepCloudClient(ZepClient):
    def __init__(self, api_key: str):
        self.client = zep_cloud.client.AsyncZep(api_key=api_key)

    def get_support_tools(self) -> list[ToolDefinition]:
        return [tool_search_facts, tool_search_nodes]

    async def add_session(self, user_id: str, session_id: str):
        try:
            await self.client.memory.add_session(user_id=user_id, session_id=session_id)
        except zep_cloud.BadRequestError as e:
            if "session already exists" not in str(e):
                # logger.error(f"Failed to add session: {e}")
                raise

    async def get_memory(self, session_id: str, lastn: int) -> KarakuriMemory:
        memory = await self.client.memory.get(session_id=session_id, lastn=lastn)
        facts = (
            f"relevant_facts: ({','.join(fact.json() for fact in memory.relevant_facts)})"
            if memory.relevant_facts
            else ""
        )
        return KarakuriMemory(
            messages=_create_litellm_messages(memory),
            facts=facts,
            context=memory.context or "",
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

    async def add_user(self, user_id: str, last_name: str, first_name: str):
        await self.client.user.add(
            user_id=user_id, first_name=first_name, last_name=last_name
        )

    async def delete_user(self, user_id: str):
        await self.client.user.delete(user_id=user_id)

    async def get_user(self, user_id: str) -> UserConfig:
        user = await self.client.user.get(user_id=user_id)
        if not user.user_id:
            raise HTTPException(
                status_code=404, detail="User ID is required and cannot be empty"
            )
        return UserConfig(
            id=user.user_id,
            last_name=user.last_name or "user",
            first_name=user.first_name or "user",
        )

    async def list_users(self) -> list[UserConfig]:
        response = await self.client.user.list_ordered()
        if not response or not response.users:
            return []
        return [
            UserConfig(
                id=user.user_id,
                last_name=user.last_name or "user",
                first_name=user.first_name or "user",
            )
            for user in response.users
            if user.user_id is not None
        ]

    async def search_facts(self, user_id: str, query: str, limit: int = 5) -> list[str]:
        edges = await self.client.graph.search(
            user_id=user_id, query=query, limit=limit, scope="edges"
        )
        if edges.edges is None:
            return []
        return [edge.fact for edge in edges.edges]

    async def search_nodes(self, user_id: str, query: str, limit: int = 5) -> list[str]:
        nodes = await self.client.graph.search(
            user_id=user_id, query=query, limit=limit, scope="nodes"
        )
        if nodes.nodes is None:
            return []
        return [node.summary for node in nodes.nodes]


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
