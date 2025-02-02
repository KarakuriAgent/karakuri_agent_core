# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

from abc import ABC, abstractmethod
from typing import Any

from app.schemas.agent import AgentConfig
from app.schemas.chat_message import ChatMessage, MessageType


class ChatClient(ABC):
    @abstractmethod
    def create(self, agent_config: AgentConfig):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def process_message(self, events: list[Any]) -> list[ChatMessage]:
        pass

    @abstractmethod
    async def reply_message(
        self, token: str, message: str, audio_url: str, duration: int
    ):
        pass

    @abstractmethod
    async def push_message(self, id: str, message: str, audio_url: str, duration: int):
        pass

    async def process_and_send_messages(
        self,
        messages: list[ChatMessage],
        agent_config: AgentConfig,
        llm_service: Any,
        tts_service: Any,
        memory_service: Any,
        base_url: str,
        use_reply: bool = True,
    ):
        from typing import cast
        from app.schemas.llm import LLMResponse
        from app.utils.audio import calculate_audio_duration, upload_to_storage
        from app.core.config import get_settings
        import logging

        logger = logging.getLogger(__name__)
        settings = get_settings()

        for message in messages:
            user_config = await memory_service.get_user(agent_config.id, message.id)
            if user_config is None:
                logger.error(f"User not found: {message.id}")
                continue

            text_message = None
            cached_image_bytes = None

            if message.content.type == MessageType.IMAGE:
                if message.content.image:
                    cached_image_bytes = message.content.image
                continue
            elif message.content.type == MessageType.TEXT and message.content.text:
                text_message = message.content.text
            else:
                continue

            llm_response = cast(
                LLMResponse,
                await llm_service.generate_response(
                    "talk",
                    text_message,
                    agent_config,
                    user_config,
                    image=cached_image_bytes,
                ),
            )

            audio_data = await tts_service.generate_speech(
                llm_response.agent_message, agent_config
            )

            audio_url = await upload_to_storage(
                base_url,
                audio_data,
                "line",
                settings.line_audio_files_dir,
                settings.line_max_audio_files,
            )
            duration = calculate_audio_duration(audio_data)

            if use_reply:
                await self.reply_message(
                    message.reply_token,
                    llm_response.agent_message,
                    audio_url,
                    duration,
                )
            else:
                await self.push_message(
                    message.id,
                    llm_response.agent_message,
                    audio_url,
                    duration,
                )
