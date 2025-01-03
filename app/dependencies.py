# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from app.core.llm_service import LLMService
from app.core.schedule_service import ScheduleService
from app.core.tts_service import TTSService
from app.core.stt_service import STTService
from functools import lru_cache


@lru_cache()
def get_llm_service() -> LLMService:
    return LLMService()


@lru_cache()
def get_tts_service() -> TTSService:
    return TTSService()


@lru_cache()
def get_stt_service() -> STTService:
    return STTService()


@lru_cache()
def get_schedule_service() -> ScheduleService:
    return ScheduleService(get_llm_service())
