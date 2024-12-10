# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from abc import ABC, abstractmethod
import aiohttp
from typing import Optional
from app.schemas.agent import AgentConfig
import logging

logger = logging.getLogger(__name__)
class TTSProvider(ABC):
    @abstractmethod
    async def generate_speech(self, text: str, agent_config: AgentConfig) -> bytes:
        pass

class VoicevoxProvider(TTSProvider):
    async def generate_speech(self, text: str, agent_config: AgentConfig) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{agent_config.tts_base_url}/audio_query",
                params={
                    "text": text,
                    "speaker": agent_config.tts_speaker_id
                }
            ) as query_response:
                query_response.raise_for_status()
                query_data = await query_response.json()

            async with session.post(
                f"{agent_config.tts_base_url}/synthesis",
                params={
                    "speaker": agent_config.tts_speaker_id
                },
                json=query_data
            ) as synthesis_response:
                synthesis_response.raise_for_status()
                return await synthesis_response.read()

class OtherServiceProvider(TTSProvider):
    async def generate_speech(self, text: str, agent_config: AgentConfig) -> bytes:
        return b""

class TTSService:
    def __init__(self):
        self.providers = {
            "voicevox": VoicevoxProvider(),
            "other_service": OtherServiceProvider()
        }

    async def generate_speech(
        self,
        text: str,
        agent_config: AgentConfig,
    ) -> bytes:
        provider = self.providers.get(agent_config.tts_type)
        if not provider:
            raise ValueError(f"Unsupported TTS provider: {agent_config.tts_type}")
        
        try:
            return await provider.generate_speech(
                text,
                agent_config
            )
        except Exception as e:
            raise Exception(f"Failed to generate speech: {str(e)}")
