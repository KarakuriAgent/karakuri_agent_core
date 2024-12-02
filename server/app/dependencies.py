from app.core.llm_service import LLMService
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
