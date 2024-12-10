# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
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
            return f"""analyze the following text emotion.
            Respond ONLY in the specified JSON format without any additional explanation.

    Input text: {text}

    Required JSON format:
    {{
        {{
            "emotion": One of these emotions: {', '.join(emotions)},
        }}
    }}"""

    async def generate_response(
        self, 
        message_type: str,
        message: str,
        agent_config: AgentConfig,
        conversation_history: Optional[list] = None
    ) -> dict:
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
        return await self.generate_emotion_response(message, response.choices[0].message.content, agent_config)

    async def generate_emotion_response(
        self, 
        user_message: str,
        agent_message: str,
        agent_config: AgentConfig,
    ) -> dict:
        emotion_prompt = self.create_emotion_analysis_prompt(agent_message)

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
            parsed_response = json.loads(emotion_response.choices[0].message.content)
            if not isinstance(parsed_response, dict) or "emotion" not in parsed_response:
                raise ValueError("Invalid JSON structure")
            
            if parsed_response["emotion"] not in Emotion.to_request_values():
                raise ValueError(f"Invalid emotion value: {parsed_response['emotion']}")
            return {
                    "emotion": parsed_response["emotion"],
                    "user_message": user_message,
                    "agent_message": agent_message
                }
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing emotion response: {str(e)}")
            return {
                    "emotion": Emotion.NEUTRAL,
                    "user_message": user_message,
                    "agent_message": agent_message
                }
