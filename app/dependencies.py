# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from app.core.chat.line_chat_client import LineChatClient
from app.core.chat.chat_service import ChatService
from app.core.facade.talk_facade import TalkFacade
from app.core.llm_service import LLMService
from app.core.memory.memory_service import MemoryService
from app.core.status_service import StatusService
from app.core.tts_service import TTSService
from app.core.stt_service import STTService
from functools import lru_cache
from app.core.config import get_settings
from app.core.agent_manager import get_agent_manager


@lru_cache()
def get_llm_service() -> LLMService:
    memory_service = get_memory_service()
    status_service = get_status_service()
    return LLMService(memory_service=memory_service, status_service=status_service)


@lru_cache()
def get_tts_service() -> TTSService:
    return TTSService()


@lru_cache()
def get_stt_service() -> STTService:
    return STTService()


@lru_cache()
def get_memory_service() -> MemoryService:
    return MemoryService()


@lru_cache()
def get_status_service() -> StatusService:
    return StatusService()


@lru_cache()
def get_line_chat_client() -> LineChatClient:
    return LineChatClient()


@lru_cache()
def get_chat_service() -> ChatService:
    return ChatService()


def get_talk_facade() -> TalkFacade:
    """Get TalkFacade instance."""
    return TalkFacade(
        llm_service=get_llm_service(),
        tts_service=get_tts_service(),
        stt_service=get_stt_service(),
        memory_service=get_memory_service(),
        agent_manager=get_agent_manager(),
        settings=get_settings(),
    )
