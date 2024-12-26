# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from pydantic import BaseModel

class AgentConfig(BaseModel):
    id: str
    name: str
    message_generate_llm_base_url: str
    message_generate_llm_api_key: str
    message_generate_llm_model: str
    emotion_generate_llm_base_url: str
    emotion_generate_llm_api_key: str
    emotion_generate_llm_model: str
    vision_generate_llm_base_url: str
    vision_generate_llm_api_key: str
    vision_generate_llm_model: str
    llm_system_prompt: str
    tts_base_url: str
    tts_api_key: str
    tts_type: str
    tts_speaker_model: str
    tts_speaker_id: str
    line_channel_secret: str
    line_channel_access_token: str

class AgentResponse(BaseModel):
    agent_id: str
    agent_name: str
