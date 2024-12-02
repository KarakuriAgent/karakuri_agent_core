from dotenv import load_dotenv
from functools import lru_cache
import os
from typing import List

class Settings:
    def __init__(self):
        load_dotenv()
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.api_keys: List[str] = [
            key.strip() 
            for key in os.getenv("API_KEYS", "").split(",") 
            if key.strip()
        ]
        self.line_max_audio_files = int(os.getenv("LINE_MAX_AUDIO_FILES", "5"))
        self.line_audio_files_dir = str(os.getenv("LINE_AUDIO_FILES_DIR", "audio_files"))
    
    def get_agent_env(self, agent_id: int, key: str) -> str:
        return os.getenv(f"AGENT_{agent_id}_{key}")
    
    def is_valid_api_key(self, api_key: str) -> bool:
        return api_key in self.api_keys

@lru_cache()
def get_settings() -> Settings:
    return Settings()
