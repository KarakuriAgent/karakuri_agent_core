from typing import Type, TypeVar, cast
from app.core.llm_service import LLMService
from app.core.tts_service import TTSService
from app.core.stt_service import STTService
from app.core.schedule_service import ScheduleService
from app.core.memory_service import MemoryService

T = TypeVar("T")


class ServiceFactory:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._instances = {}
        self._initialized = True

    async def initialize(self):
        schedule_service = self.get_schedule_service()
        await schedule_service.initialize()

    async def cleanup(self):
        schedule_service = self.get_schedule_service()
        if schedule_service:
            await schedule_service.stop_schedule_monitoring()

    def _get_or_create(self, service_class: Type[T], key: str, **kwargs) -> T:
        if key not in self._instances:
            self._instances[key] = service_class(**kwargs)
        return cast(T, self._instances[key])

    def get_llm_service(self) -> LLMService:
        memory_service = self.get_memory_service()
        return self._get_or_create(LLMService, "llm", memory_service=memory_service)

    def get_tts_service(self) -> TTSService:
        return self._get_or_create(TTSService, "tts")

    def get_stt_service(self) -> STTService:
        return self._get_or_create(STTService, "stt")

    def get_memory_service(self) -> MemoryService:
        return self._get_or_create(MemoryService, "memory")

    def get_schedule_service(self) -> ScheduleService:
        llm_service = self.get_llm_service()
        memory_service = self.get_memory_service()
        return self._get_or_create(
            ScheduleService,
            "schedule",
            llm_service=llm_service,
            memory_service=memory_service,
        )
