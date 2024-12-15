# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from functools import lru_cache
from typing import Dict, List, Tuple
from app.schemas.agent import AgentConfig
from app.core.config import get_settings

class AgentManager:
    def __init__(self):
        self.settings = get_settings()
        self.agents: Dict[str, AgentConfig] = self._load_agents_from_env()

    def _load_agents_from_env(self) -> Dict[str, AgentConfig]:
        agents: Dict[str, AgentConfig] = {}
        i = 1
        while True:
            name = self.settings.get_agent_env(i, "NAME")
            message_generate_llm_base_url=self.settings.get_agent_env(i, "MESSAGE_GENERATE_LLM_BASE_URL")
            message_generate_llm_api_key=self.settings.get_agent_env(i, "MESSAGE_GENERATE_LLM_API_KEY")
            message_generate_llm_model=self.settings.get_agent_env(i, "MESSAGE_GENERATE_LLM_MODEL")
            emotion_generate_llm_base_url=self.settings.get_agent_env(i, "EMOTION_GENERATE_LLM_BASE_URL")
            emotion_generate_llm_api_key=self.settings.get_agent_env(i, "EMOTION_GENERATE_LLM_API_KEY")
            emotion_generate_llm_model=self.settings.get_agent_env(i, "EMOTION_GENERATE_LLM_MODEL")
            required_values = [
                name,
                message_generate_llm_base_url,
                message_generate_llm_api_key,
                message_generate_llm_model,
                emotion_generate_llm_base_url,
                emotion_generate_llm_api_key,
                emotion_generate_llm_model,
                ]

            if not all(required_values):
                break
            
            agents[str(i)] = AgentConfig(
                id=str(i),
                name=name,
                message_generate_llm_base_url=message_generate_llm_base_url,
                message_generate_llm_api_key=message_generate_llm_api_key,
                message_generate_llm_model=message_generate_llm_model,
                emotion_generate_llm_base_url=emotion_generate_llm_base_url,
                emotion_generate_llm_api_key=emotion_generate_llm_api_key,
                emotion_generate_llm_model=emotion_generate_llm_model,
                llm_system_prompt=self.settings.get_agent_env(i, "LLM_SYSTEM_PROMPT") or "",
                tts_base_url=self.settings.get_agent_env(i, "TTS_BASE_URL") or "",
                tts_api_key=self.settings.get_agent_env(i, "TTS_API_KEY") or "",
                tts_type=self.settings.get_agent_env(i, "TTS_TYPE") or "",
                tts_speaker_model=self.settings.get_agent_env(i, "TTS_SPEAKER_MODEL") or "",
                tts_speaker_id=self.settings.get_agent_env(i, "TTS_SPEAKER_ID") or "",
                line_channel_secret=self.settings.get_agent_env(i, "LINE_CHANNEL_SECRET") or "",
                line_channel_access_token=self.settings.get_agent_env(i, "LINE_CHANNEL_ACCESS_TOKEN") or "",
            )
            i += 1
        return agents

    def get_agent(self, agent_id: str) -> AgentConfig:
        agent = self.agents.get(agent_id)
        if agent is None:
            raise KeyError(f"Agent with ID '{agent_id}' not found.")
        return agent

    def get_all_agents(self) -> List[Tuple[str, str]]:
        return [(id, config.name) for id, config in self.agents.items()]

@lru_cache()
def get_agent_manager() -> AgentManager:
    return AgentManager()
