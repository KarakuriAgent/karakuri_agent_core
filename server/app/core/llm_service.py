from typing import List, Optional, Union
import base64
import logging
import json

from litellm import (
    AllMessageValues, ChatCompletionImageObject, ChatCompletionImageUrlObject, ChatCompletionTextObject,
    ChatCompletionUserMessage, ChatCompletionSystemMessage, ChatCompletionAssistantMessage,
    Choices, CustomStreamWrapper, acompletion, ModelResponse, utils, litellm # type: ignore
)
from app.schemas.agent import AgentConfig
from app.schemas.emotion import Emotion
from app.schemas.llm import LLMResponse
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
CHECK_SUPPORT_VISION_MODEL = settings.check_support_vision_model

conversation_history: List[AllMessageValues] = []

class LLMService:
    MAX_ROUNDS = 10

    def create_emotion_analysis_prompt(self, text: str) -> str:
        emotions = Emotion.to_request_values()
        return f"""analyze the following text emotion.
        Respond ONLY in the specified JSON format without any additional explanation.

Input text: {text}

Required JSON format:
{{
    "emotion": One of these emotions: {', '.join(emotions)}
}}"""

    async def generate_response(
        self, 
        message_type: str,
        message: str,
        agent_config: AgentConfig,
        image: Optional[bytes] = None
    ) -> LLMResponse:
        global conversation_history
        messages: List[AllMessageValues] = []
        
        if agent_config.llm_system_prompt:
            messages.append(
                ChatCompletionSystemMessage(
                    role="system",
                    content=agent_config.llm_system_prompt,
                )
            )

        messages.extend(conversation_history)

        if image:
            image_data_b64 = base64.b64encode(image).decode('utf-8')
            data_url = f"data:image/jpeg;base64,{image_data_b64}"
            
            if not CHECK_SUPPORT_VISION_MODEL or utils.supports_vision(model=agent_config.message_generate_llm_model):
                messages.append(
                    ChatCompletionUserMessage(
                        role="user",
                        content=[
                            ChatCompletionImageObject(
                                type="image_url",
                                image_url=ChatCompletionImageUrlObject(url=data_url),
                            ),
                            ChatCompletionTextObject(
                                type="text",
                                text=message
                            ),
                        ]
                    )
                )
            else:
                image_description = await self.convert_images_to_text(data_url, agent_config)
                messages.append(
                    ChatCompletionUserMessage(
                        role="user",
                        content=f"{message}\n\n[Image description: {image_description}]"
                    )
                )
        else:
            messages.append(
                ChatCompletionUserMessage(
                    role="user",
                    content=message,
                )
            )

        response = await acompletion(
            base_url=agent_config.message_generate_llm_base_url,
            api_key=agent_config.message_generate_llm_api_key,
            model=agent_config.message_generate_llm_model,
            messages=messages
        )
        agent_message = self.get_message_content(response)

        emotion = await self.generate_emotion_response(
            user_message=message,
            agent_message=agent_message,
            agent_config=agent_config
        )

        conversation_history = self._update_conversation_history(
            conversation_history,
            user_message=message,
            agent_message=agent_message
        )

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
            raise TypeError("response.choices[0] is not an instance of Choices.")

        content = first_choice.message.content
        if not isinstance(content, str):
            raise TypeError("response.choices[0].message.content is not a string.")
        if not content.strip():
            raise ValueError("response.choices[0].message.content is empty or whitespace-only.")

        return content
    
    async def convert_images_to_text(self, data_url: str, agent_config: AgentConfig) -> str:
        vision_messages: List[AllMessageValues] = [
            ChatCompletionSystemMessage(
                role="system",
                content="You are a vision model that converts images into a descriptive text."
            ),
            ChatCompletionUserMessage(
                role="user",
                content=[
                    ChatCompletionImageObject(
                        type="image_url",
                        image_url=ChatCompletionImageUrlObject(url=data_url)
                    ),
                    ChatCompletionTextObject(
                        type="text",
                        text="Please describe the following images in a concise and clear way."
                    ),
                ]
            )
        ]
        vision_response = await acompletion(
            base_url=agent_config.vision_generate_llm_base_url,
            api_key=agent_config.vision_generate_llm_api_key,
            model=agent_config.vision_generate_llm_model,
            messages=vision_messages,
        )
        return self.get_message_content(vision_response)

    async def generate_emotion_response(
        self, 
        user_message: str,
        agent_message: str,
        agent_config: AgentConfig,
    ) -> str:
        emotion_prompt = self.create_emotion_analysis_prompt(agent_message)
        emotion_messages: List[AllMessageValues] = [
            ChatCompletionSystemMessage(
                role="system",
                content="You are an expert emotion analyzer. Always respond in the exact JSON format requested.",
            ),
            ChatCompletionUserMessage(
                role="user",
                content=emotion_prompt,
            )
        ]
        emotion_response = await acompletion(
            base_url=agent_config.emotion_generate_llm_base_url,
            api_key=agent_config.emotion_generate_llm_api_key,
            model=agent_config.emotion_generate_llm_model,
            messages=emotion_messages,
            response_format={"type": "json_object"},
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

    def _update_conversation_history(
        self,
        conversation_history: List[AllMessageValues],
        user_message: str,
        agent_message: str
    ) -> List[AllMessageValues]:
        conversation_history.append(
            ChatCompletionUserMessage(
                role="user",
                content=user_message
            )
        )
        conversation_history.append(
            ChatCompletionAssistantMessage(
                role="assistant",
                content=agent_message
            )
        )

        max_length = self.MAX_ROUNDS * 2
        if len(conversation_history) > max_length:
            conversation_history = conversation_history[-max_length:]
        
        return conversation_history
