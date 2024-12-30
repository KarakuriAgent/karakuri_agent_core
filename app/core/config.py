# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from dotenv import load_dotenv
from functools import lru_cache
import os
from typing import List

from numpy import double


class Settings:
    def __init__(self):
        load_dotenv()
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.api_keys: List[str] = [
            key.strip() for key in os.getenv("API_KEYS", "").split(",") if key.strip()
        ]
        self.line_max_audio_files = int(os.getenv("LINE_MAX_AUDIO_FILES", "5"))
        self.line_audio_files_dir = str(
            os.getenv("LINE_AUDIO_FILES_DIR", "line_audio_files")
        )
        self.chat_max_audio_files = int(os.getenv("CHAT_MAX_AUDIO_FILES", "5"))
        self.chat_audio_files_dir = str(
            os.getenv("CHAT_AUDIO_FILES_DIR", "chat_audio_files")
        )
        self.web_socket_max_audio_files = int(
            os.getenv("WEB_SOCKET_MAX_AUDIO_FILES", "5")
        )
        self.web_socket_audio_files_dir = str(
            os.getenv("WEB_SOCKET_AUDIO_FILES_DIR", "chat_audio_files")
        )
        self.check_support_vision_model = (
            os.getenv("CHECK_SUPPORT_VISION_MODEL", "True").lower() == "true"
        )
        self.redis_url = str(os.getenv("REDIS_URL", "redis://karakuri-redis"))
        self.threshold_tokens_percentage = double(
            os.getenv("THRESHOLD_TOKENS_PERCENTAGE", 0.8)
        )

    def get_agent_env(self, agent_id: int, key: str) -> str:
        return os.getenv(f"AGENT_{agent_id}_{key}") or ""

    def is_valid_api_key(self, api_key: str) -> bool:
        return api_key in self.api_keys


@lru_cache()
def get_settings() -> Settings:
    return Settings()
