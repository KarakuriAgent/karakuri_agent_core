# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
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
from app.core.date_util import DateUtil
from app.schemas.agent import AgentConfig
from app.schemas.emotion import Emotion
from app.schemas.llm import LLMResponse
from app.core.config import get_settings
from app.core.memory.memory_service import MemoryService, conversation_history_lock

logger = logging.getLogger(__name__)
settings = get_settings()
CHECK_SUPPORT_VISION_MODEL = settings.check_support_vision_model


class LLMService:
    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_facts",
                    "description": "Search user's facts",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_nodes",
                    "description": "Search user's memory nodes",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"],
                    },
                },
            },
        ]

    def create_emotion_analysis_prompt(self, text: str) -> str:
        emotions = Emotion.to_request_values()
        return f"""analyze the following text emotion.
        Respond ONLY in the specified JSON format without any additional explanation.

Input text: {text}

Required JSON format:
{{
    "emotion": One of these emotions: {", ".join(emotions)}
}}"""

    async def _process_llm_response(
        self,
        agent_config: AgentConfig,
        user_id: str,
        systemMessage: ChatCompletionSystemMessage,
        conversation_history: List[AllMessageValues],
        max_tool_calls: int = 5,
    ) -> Union[ModelResponse, CustomStreamWrapper]:
        if max_tool_calls <= 0:
            logger.warning("Maximum number of tool executions reached")
            raise Exception("Maximum number of tool executions reached")

        response = await acompletion(
            base_url=agent_config.message_generate_llm_base_url,
            api_key=agent_config.message_generate_llm_api_key,
            model=agent_config.message_generate_llm_model,
            messages=[systemMessage] + conversation_history[:],
            tools=self.tools,
            tool_choice="auto",
        )

        if isinstance(response, dict) and "tool_calls" in response:
            tool_calls = response["tool_calls"]
            tool_results = await self._handle_tool_calls(
                tool_calls, agent_config.id, user_id
            )

            conversation_history.append(
                ChatCompletionAssistantMessage(
                    role="assistant",
                    content="",
                    tool_calls=tool_calls,
                )
            )
            conversation_history.append(
                ChatCompletionUserMessage(
                    role="user",
                    content=tool_results,
                )
            )

            return await self._process_llm_response(
                agent_config,
                user_id,
                systemMessage,
                conversation_history,
                max_tool_calls - 1,
            )

        return response

    async def generate_response(
        self,
        message_type: str,
        message: str,
        agent_config: AgentConfig,
        user_id: str,
        image: Optional[bytes] = None,
        openai_request: bool = False,
    ) -> Union[Union[ModelResponse, CustomStreamWrapper], LLMResponse]:
        async with conversation_history_lock:
            session_memory = await self.memory_service.get_session_memory(
                agent_config.id, user_id, message_type
            )
            conversation_history = session_memory.messages
            systemMessage = ChatCompletionSystemMessage(
                role="system",
                content="\n\n".join(
                    [
                        agent_config.llm_system_prompt,
                        f"current date time: {DateUtil.now()}",
                        session_memory.context,
                        """
                        You have access to the following tools to help you better understand and assist the user:

                        1. search_facts: Use this tool to search for relevant facts about the user. This helps you understand the user's history and preferences.
                        - When you need to recall specific information about the user
                        - When you want to verify something the user mentioned before
                        - When you need context about past interactions

                        2. search_nodes: Use this tool to search through the user's memory nodes. This helps you understand the context of conversations.
                        - When you need to understand the flow of previous conversations
                        - When you want to connect current topics with past discussions
                        - When you need detailed context about specific topics

                        Guidelines for using tools:
                        - Always search for relevant information before making assumptions about the user
                        - Use both tools when you need comprehensive context
                        - When searching, use specific and relevant keywords
                        - The search results will be in JSON format - parse them carefully to extract useful information

                        Remember to use these tools proactively to provide more personalized and contextually relevant responses.""",
                    ]
                ),
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

            response = await self._process_llm_response(
                agent_config,
                user_id,
                systemMessage,
                conversation_history,
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
                self.memory_service.update_session_memory(
                    agent_config.id,
                    user_id,
                    message_type,
                    conversation_history,
                )
            )
        if openai_request:
            return response
        else:
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
            base_url=agent_config.emotion_generate_llm_base_url,
            api_key=agent_config.emotion_generate_llm_api_key,
            model=agent_config.emotion_generate_llm_model,
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

    async def _handle_tool_calls(
        self, tool_calls: List[dict], agent_id: str, user_id: str
    ) -> str:
        results = []
        for tool_call in tool_calls:
            if tool_call["function"]["name"] == "search_facts":
                args = json.loads(tool_call["function"]["arguments"])
                result = await self.memory_service.search_facts(
                    agent_id, user_id, args["query"]
                )
                logger.info(f"search_facts: {result}")
                results.append(json.dumps(result, ensure_ascii=False))
            elif tool_call["function"]["name"] == "search_nodes":
                args = json.loads(tool_call["function"]["arguments"])
                result = await self.memory_service.search_nodes(
                    agent_id, user_id, args["query"]
                )
                logger.info(f"search_nodes: {result}")
                results.append(json.dumps(result, ensure_ascii=False))
        return "\n".join(results)
