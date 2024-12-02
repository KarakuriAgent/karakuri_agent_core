from typing import Optional
from litellm import acompletion
from app.schemas.agent import AgentConfig
from app.schemas.emotion import Emotion
import logging
import json


logger = logging.getLogger(__name__)

class LLMService:

    def create_emotion_analysis_prompt(self, text: str) -> str:
            emotions = Emotion.to_request_values()
            return f"""Analyze the following text by dividing it into meaningful units and identifying the emotions expressed in each part.
    Respond ONLY in the specified JSON format without any additional explanation.

    Input text: {text}

    Required JSON format:
    {{
        "responses": [
            {{
                "emotion": One of these emotions: {', '.join(emotions)},
                "divided_message": "A meaningful segment of the text"
            }},
            ... (repeat for each segment)
        ]
    }}"""

    async def generate_response(
        self, 
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
            base_url=agent_config.message_generate_llm_base_url,
            api_key=agent_config.message_generate_llm_api_key,
            model=agent_config.message_generate_llm_model,
            messages=messages
        )
        return await self.generate_emotion_response(response.choices[0].message.content, agent_config)

    async def generate_emotion_response(
        self, 
        message: str,
        agent_config: AgentConfig,
    ) -> str:
        logger.info(message)
        emotion_prompt = self.create_emotion_analysis_prompt(message)

        emotion_messages = [
                {
                    "role": "system",
                    "content": "You are an expert emotion analyzer. Always respond in the exact JSON format requested."
                },
                {
                    "role": "user",
                    "content": emotion_prompt
                }
            ]
        emotion_response = await acompletion(
                base_url=agent_config.emotion_generate_llm_base_url,
                api_key=agent_config.emotion_generate_llm_api_key,
                model=agent_config.emotion_generate_llm_model,
                messages=emotion_messages,
                response_format={ "type": "json_object" },
            )

        try:
            json.loads(emotion_response.choices[0].message.content)
            return emotion_response.choices[0].message.content
        except json.JSONDecodeError:
            fallback_response = {
                "responses": [{
                    "emotion": Emotion.NEUTRAL,
                    "divided_message": message
                }]
            }
            return json.dumps(fallback_response)
