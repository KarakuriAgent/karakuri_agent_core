from pydantic import BaseModel

class TextChatRequest(BaseModel):
    agent_id: str
    message: str
