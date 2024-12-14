# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from typing import List, Optional, Union

from litellm import Choices, CustomStreamWrapper, Message, acompletion, ModelResponse  # type: ignore
from app.schemas.agent import AgentConfig
from app.schemas.emotion import Emotion
from app.schemas.llm import LLMMessage, LLMResponse
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
        conversation_history: Optional[List[LLMMessage]] = None
    ) -> LLMResponse:
        messages: List[LLMMessage] = []
        
        if agent_config.llm_system_prompt:
            messages.append(LLMMessage(
                role="system",
                content=agent_config.llm_system_prompt,
                function_call=None,
                tool_calls=[]
            ))
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append(LLMMessage(
            role="user",
            content=message,
                function_call=None,
                tool_calls=[]
        ))
        response = await acompletion(
            base_url=agent_config.message_generate_llm_base_url,
            api_key=agent_config.message_generate_llm_api_key,
            model=agent_config.message_generate_llm_model,
            messages=messages
        )
        agent_message = self.get_message_content(response)
        emotion = await self.generate_emotion_response(message, agent_message, agent_config)
        return LLMResponse(user_message=message, agent_message=agent_message, emotion=emotion)

    def get_message_content(self, response: Union[ModelResponse, CustomStreamWrapper]) -> str:
        if not isinstance(response, ModelResponse):
            raise TypeError("response is not a ModelResponse instance.")

        if not hasattr(response, 'choices'):
            raise AttributeError("response has no 'choices' attribute.")
        
        if len(response.choices) == 0:
            raise IndexError("response.choices is empty, no elements to access.")

        first_choice = response.choices[0]
        if not isinstance(first_choice, Choices):
            raise TypeError("response.choices[0] is not an instance of Choice.")

        content = first_choice.message.content

        if not isinstance(content, str):
            raise TypeError("response.choices[0].message.content is not a string.")

        if not content.strip():
            raise ValueError("response.choices[0].message.content is empty or whitespace-only.")

        return content

    async def generate_emotion_response(
        self, 
        user_message: str,
        agent_message: str,
        agent_config: AgentConfig,
    ) -> str:
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
            parsed_response = json.loads(self.get_message_content(emotion_response))
            if not isinstance(parsed_response, dict) or "emotion" not in parsed_response:
                raise ValueError("Invalid JSON structure")
            
            if parsed_response["emotion"] not in Emotion.to_request_values():
                raise ValueError(f"Invalid emotion value: {parsed_response['emotion']}")
            return parsed_response["emotion"]
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing emotion response: {str(e)}")
            return Emotion.NEUTRAL.value
