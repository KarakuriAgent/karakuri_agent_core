# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from pydantic import BaseModel

from app.schemas.status import AgentStatusConfig
from app.schemas.schedule import AgentScheduleConfig


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
    schedule_generate_llm_base_url: str
    schedule_generate_llm_api_key: str
    schedule_generate_llm_model: str
    llm_system_prompt: str
    tts_base_url: str
    tts_api_key: str
    tts_type: str
    tts_speaker_model: str
    tts_speaker_id: str
    line_channel_secret: str
    line_channel_access_token: str
    status: AgentStatusConfig
    schedule: AgentScheduleConfig

    def update_status(self, new_status: str) -> "AgentConfig":
        """Update agent status and return new instance"""
        from datetime import datetime
        from app.schemas.status import AgentStatus

        return self.model_copy(
            update={
                "status": self.status.model_copy(
                    update={
                        "current_status": AgentStatus(new_status),
                        "last_status_change": datetime.now().isoformat(),
                    }
                )
            },
            deep=True,
        )


class AgentResponse(BaseModel):
    agent_id: str
    agent_name: str
