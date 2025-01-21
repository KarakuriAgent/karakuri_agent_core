# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from app.core.llm_service import LLMService
from app.core.memory_service import MemoryService
from app.core.tts_service import TTSService
from app.core.stt_service import STTService
from functools import lru_cache


@lru_cache()
def get_llm_service() -> LLMService:
    memory_service = get_memory_service()
    return LLMService(memory_service=memory_service)


@lru_cache()
def get_tts_service() -> TTSService:
    return TTSService()


@lru_cache()
def get_stt_service() -> STTService:
    return STTService()


@lru_cache()
def get_memory_service() -> MemoryService:
    return MemoryService()
