import asyncio
from typing import List, Optional, Union
import base64
import logging
import json
from litellm import (
    AllMessageValues,
    ChatCompletionImageObject,
    ChatCompletionImageUrlObject,
    ChatCompletionTextObject,
    ChatCompletionUserMessage,
    ChatCompletionSystemMessage,
    ChatCompletionAssistantMessage,
    Choices,
    CustomStreamWrapper,
    acompletion,  # type: ignore
    ModelResponse,  # type: ignore
    utils,  # type: ignore
)
from app.core.memory_service import MemoryService
from app.schemas.agent import AgentConfig
from app.schemas.emotion import Emotion
from app.schemas.llm import LLMResponse
from app.core.config import get_settings
from app.core.memory_service import conversation_history_lock
from app.schemas.schedule import ScheduleContext, ScheduleItem

logger = logging.getLogger(__name__)
settings = get_settings()
CHECK_SUPPORT_VISION_MODEL = settings.check_support_vision_model

memory_service = MemoryService()


class LLMService:
    def create_emotion_analysis_prompt(self, text: str) -> str:
        emotions = Emotion.to_request_values()
        return f"""analyze the following text emotion.
        Respond ONLY in the specified JSON format without any additional explanation.

        Input text: {text}

        Required JSON format:
        {{
            "emotion": One of these emotions: {', '.join(emotions)}
        }}"""
    def create_system_prompt(self, llm_system_prompt: str, context: ScheduleContext) -> str:
        return f"""
        {llm_system_prompt}

        Craft a natural, contextual response based on your current status.

        Current time: {context.current_time}
        Daily Schedule: {context.schedule}
        """

    async def generate_response(
        self,
        message: str,
        schedule_context: ScheduleContext,
        agent_config: AgentConfig,
        image: Optional[bytes] = None,
    ) -> LLMResponse:
        async with conversation_history_lock:
            conversation_history = await memory_service.get_conversation_history(
                agent_config.id
            )
            systemMessage = ChatCompletionSystemMessage(
                role="system",
                content=self.create_system_prompt(agent_config.llm_system_prompt, schedule_context),
            )

            if image:
                image_data_b64 = base64.b64encode(image).decode("utf-8")
                data_url = f"data:image/jpeg;base64,{image_data_b64}"

                if not CHECK_SUPPORT_VISION_MODEL or utils.supports_vision(
                    model=agent_config.message_generate_llm_model
                ):
                    conversation_history.append(
                        ChatCompletionUserMessage(
                            role="user",
                            content=[
                                ChatCompletionImageObject(
                                    type="image_url",
                                    image_url=ChatCompletionImageUrlObject(
                                        url=data_url
                                    ),
                                ),
                                ChatCompletionTextObject(type="text", text=message),
                            ],
                        )
                    )
                else:
                    image_description = await self.convert_images_to_text(
                        data_url, agent_config
                    )
                    conversation_history.append(
                        ChatCompletionUserMessage(
                            role="user",
                            content=f"{message}\n\n[Image description: {image_description}]",
                        )
                    )
            else:
                conversation_history.append(
                    ChatCompletionUserMessage(
                        role="user",
                        content=message,
                    )
                )

            response = await acompletion(
                base_url=agent_config.message_generate_llm_base_url,
                api_key=agent_config.message_generate_llm_api_key,
                model=agent_config.message_generate_llm_model,
                messages=[systemMessage] + conversation_history[:],
            )
            agent_message = self.get_message_content(response)
            conversation_history.append(
                ChatCompletionAssistantMessage(
                    role="assistant",
                    content=agent_message,
                )
            )

            emotion = await self.generate_emotion_response(
                user_message=message,
                agent_message=agent_message,
                agent_config=agent_config,
            )

            llm_response = LLMResponse(
                user_message=message, agent_message=agent_message, emotion=emotion
            )

            asyncio.create_task(
                memory_service.update_conversation_history(
                    agent_config.message_generate_llm_model,
                    agent_config.id,
                    systemMessage,
                    conversation_history,
                )
            )

        return llm_response

    def get_message_content(
        self, response: Union[ModelResponse, CustomStreamWrapper]
    ) -> str:
        if not isinstance(response, ModelResponse):
            raise TypeError("response is not a ModelResponse instance.")
        if not hasattr(response, "choices"):
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
            raise ValueError(
                "response.choices[0].message.content is empty or whitespace-only."
            )

        return content

    async def convert_images_to_text(
        self, data_url: str, agent_config: AgentConfig
    ) -> str:
        vision_messages: List[AllMessageValues] = [
            ChatCompletionSystemMessage(
                role="system",
                content="You are a vision model that converts images into a descriptive text.",
            ),
            ChatCompletionUserMessage(
                role="user",
                content=[
                    ChatCompletionImageObject(
                        type="image_url",
                        image_url=ChatCompletionImageUrlObject(url=data_url),
                    ),
                    ChatCompletionTextObject(
                        type="text",
                        text="Please describe the following images in a concise and clear way.",
                    ),
                ],
            ),
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
            ),
        ]
        emotion_response = await acompletion(
            base_url=agent_config.analyze_generate_llm_base_url,
            api_key=agent_config.analyze_generate_llm_api_key,
            model=agent_config.analyze_generate_llm_model,
            messages=emotion_messages,
            response_format={"type": "json_object"},
        )

        try:
            parsed_response = json.loads(self.get_message_content(emotion_response))
            if (
                not isinstance(parsed_response, dict)
                or "emotion" not in parsed_response
            ):
                raise ValueError("Invalid JSON structure")

            if parsed_response["emotion"] not in Emotion.to_request_values():
                raise ValueError(f"Invalid emotion value: {parsed_response['emotion']}")
            return parsed_response["emotion"]
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing emotion response: {str(e)}")
            return Emotion.NEUTRAL.value

    async def generate_schedule(
        self,
        prompt: str,
        agent_config: AgentConfig,
    ) -> str:
        """Generate a daily schedule using LLM"""
        system_prompt = """
        You are a schedule generator for an AI agent. Create a detailed daily schedule considering the following aspects:

        Key Considerations:
        1. Activities should align with the agent's personality and role
        2. Include appropriate break times
        3. Allocate realistic time frames
        4. Account for travel time between locations
        5. Maintain consistency with the agent's established patterns

        Required Output Format:
        {
            "schedule": [
                {
                    "start_time": "HH:MM",
                    "end_time": "HH:MM",
                    "activity": "Brief activity description",
                    "status": "AVAILABLE|SLEEPING|EATING|WORKING|OUT|MAINTENANCE",
                    "description": "Detailed description of the activity",
                    "location": "Location of the activity"
                }
            ]
        }

        Guidelines:
        - Times must be in 24-hour format (HH:MM)
        - Status must match one of the defined status types
        - Activities should be specific and meaningful
        - Descriptions should provide context for the activity
        - Locations should be specific when relevant

        Note: Ensure the schedule maintains a natural flow and includes necessary transition times between activities.
        """

        messages = [
            ChatCompletionSystemMessage(role="system", content=system_prompt),
            ChatCompletionUserMessage(role="user", content=prompt),
        ]

        response = await acompletion(
            base_url=agent_config.schedule_generate_llm_base_url,
            api_key=agent_config.schedule_generate_llm_api_key,
            model=agent_config.schedule_generate_llm_model,
            messages=messages,
            response_format={"type": "json_object"},
        )
        return self.get_message_content(response)

    async def generate_laungage(self, text: str, agent_config: AgentConfig) -> str:
        systemMessage = ChatCompletionSystemMessage(
            role="system",
            content="You are an expert language analyzer. Always respond in the exact JSON format requested.",
        )
        userMessage = ChatCompletionUserMessage(
            role="user",
            content=f"""analyze the following text language.
        Respond ONLY in the specified JSON format without any additional explanation.

        Input text: {text}

        Required JSON format:
        {{
            "language": One language
        }}""",
        )
        response = await acompletion(
            base_url=agent_config.analyze_generate_llm_base_url,
            api_key=agent_config.analyze_generate_llm_api_key,
            model=agent_config.analyze_generate_llm_model,
            messages=[systemMessage, userMessage],
        )
        return self.get_message_content(response)

    async def generate_status_response(
        self, message: str, context: ScheduleContext, agent_config: AgentConfig
    ) -> LLMResponse:
        """Generate contextual status response"""

        laungage = await self.generate_laungage(text=message, agent_config=agent_config)
        system_prompt = f"""
        You are an AI agent responding to a user about your current availability. 
        Craft a natural, contextual response based on your current status and schedule.

        Guidelines:
        1. Be polite and empathetic
        2. Explain your current status/activity naturally
        3. Provide clear information about when you'll be available next
        4. If you're partially available (e.g., can respond to chat but not voice), explain this
        5. Keep the response concise but informative

        Answer language must be {laungage}
        """

        user_prompt = f"""
        Current time: {context.current_time}
        Daily Schedule: {context.schedule}

        Generate a natural response explaining your current status and availability.
        """
        messages = [
            ChatCompletionSystemMessage(
                role="system",
                content=system_prompt,
            )
        ] + [ChatCompletionUserMessage(role="user", content=user_prompt)]

        response = await acompletion(
            base_url=agent_config.message_generate_llm_base_url,
            api_key=agent_config.message_generate_llm_api_key,
            model=agent_config.message_generate_llm_model,
            messages=messages,
        )
        return LLMResponse(
            user_message=message,
            agent_message=self.get_message_content(response),
            emotion="neutral",
        )
