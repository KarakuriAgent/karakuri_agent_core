from dotenv import load_dotenv
from functools import lru_cache
import os

class Settings:
    def __init__(self):
        load_dotenv()
        self.environment = os.getenv("ENVIRONMENT", "development")
    
    def get_agent_env(self, agent_id: int, key: str) -> str:
        return os.getenv(f"AGENT_{agent_id}_{key}")

@lru_cache()
def get_settings() -> Settings:
    return Settings()
