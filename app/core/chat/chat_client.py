# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

from abc import ABC, abstractmethod
from typing import Any, Union

from app.schemas.agent import AgentConfig


class ChatClient(ABC):
    @abstractmethod
    def create(self, agent_config: AgentConfig):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def process_message(
        self, events: list[Any]
    ) -> list[tuple[str, Union[bytes, str]]]:
        pass

    @abstractmethod
    async def reply_message(
        self, token: str, message: str, audio_url: str, duration: int
    ):
        pass

    @abstractmethod
    async def push_message(self, id: str, message: str, audio_url: str, duration: int):
        pass
