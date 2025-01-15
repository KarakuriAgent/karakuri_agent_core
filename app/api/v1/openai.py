# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from typing import AsyncGenerator, cast
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import StreamingResponse
from litellm import Choices, ModelResponse  # type: ignore
from app.dependencies import get_llm_service
from app.core.llm_service import LLMService
from app.core.agent_manager import get_agent_manager
import logging
import json

from app.schemas.openai import (
    ChatCompletionRequest,
    Choice,
    DeltaContent,
    StreamChatCompletionResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat/completions")
async def openai_chat_completions(
    request: ChatCompletionRequest,
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    llm_service: LLMService = Depends(get_llm_service),
):
    agent_id = request["model"]
    agent_manager = get_agent_manager()
    agent_config = agent_manager.get_agent(agent_id)

    if not agent_config:
        raise HTTPException(status_code=404, detail=f"Agent ID {agent_id} not found")

    try:
        stream = request["stream"]
        llm_response = await llm_service.generate_response(
            message_type="text_to_text",
            message=get_content_from_message(request["messages"][-1]),
            agent_config=agent_config,
            image=None,
            openai_request=True,
        )
        litellm_response = cast(ModelResponse, llm_response)
        if stream:
            return StreamingResponse(
                generate_stream_response(litellm_response),
                media_type="text/event-stream",
            )
        else:
            return f"{json.dumps(litellm_response.model_dump(), default=convert_none_to_null)}".encode(
                "utf-8"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


def convert_none_to_null(obj):
    if obj is None:
        return "null"
    return obj


async def generate_stream_response(
    response: ModelResponse,
) -> AsyncGenerator[bytes, None]:
    try:
        if response:
            choice_list = []
            for choice in response.choices:
                choices = cast(Choices, choice)
                choice_obj = Choice(
                    finish_reason=choices.finish_reason,
                    index=choices.index,
                    delta=DeltaContent(
                        content=choices.message.content,
                        role=choices.message.role,
                        function_call=None,
                        tool_calls=choices.message.tool_calls,
                        audio=None,
                    ),
                    logprobs=None,
                )
                choice_list.append(choice_obj)

            response_data = StreamChatCompletionResponse(
                id=response.id,
                created=response.created,
                model=response.model,
                object=response.object,
                system_fingerprint=response.system_fingerprint,
                choices=choice_list,
                stream_options=None,
            )
            yield f"data: {json.dumps(response_data, default=convert_none_to_null)}\n\n".encode(
                "utf-8"
            )
    except Exception as e:
        logger.error(f"Error in stream generation: {str(e)}")
        yield f"data: [ERROR] {str(e)}\n\n".encode("utf-8")
    finally:
        yield b"data: [DONE]\n\n"


def get_content_from_message(message):
    if "content" not in message or message["content"] is None:
        raise HTTPException(status_code=400, detail="Message content is required")
    if "content" not in message:
        return ""
    content = message["content"]
    if content is None:
        return ""
    elif isinstance(content, str):
        return content
    elif isinstance(content, list):
        raise HTTPException(status_code=400, detail="Only text content is supported")
    else:
        return str(content)
