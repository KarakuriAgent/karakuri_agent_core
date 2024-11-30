from pydantic import BaseModel

class AgentConfig(BaseModel):
    id: str
    name: str
    llm_base_url: str
    llm_api_key: str
    llm_model: str
    llm_system_prompt: str
    tts_base_url: str
    tts_api_key: str
    tts_type: str
    tts_speaker_model: str
    tts_speaker_id: int

class AgentResponse(BaseModel):
    agent_id: str
    agent_name: str
