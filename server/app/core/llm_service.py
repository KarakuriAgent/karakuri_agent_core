from typing import Optional
from litellm import acompletion
from app.schemas.agent import AgentConfig
import logging

logger = logging.getLogger(__name__)

class LLMService:
    @staticmethod
    async def generate_response(
        message_type: str,
        message: str,
        agent_config: AgentConfig,
        conversation_history: Optional[list] = None
    ) -> str:
        messages = []
        
        if agent_config.llm_system_prompt:
            messages.append({
                "role": "system",
                "content": agent_config.llm_system_prompt
            })
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({
            "role": "user",
            "content": message
        })
        response = await acompletion(
            base_url=agent_config.llm_base_url,
            api_key=agent_config.llm_api_key,
            model=agent_config.llm_model,
            messages=messages,
        )
        return response.choices[0].message.content
