# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from typing import AsyncGenerator, cast
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import StreamingResponse
from litellm import CustomStreamWrapper
from app.dependencies import get_llm_service
from app.core.llm_service import LLMService
from app.core.agent_manager import get_agent_manager
import logging
import json

from app.schemas.openai import ChatCompletionRequest

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
            stream=stream,
        )
        if stream:
            stream_response = cast(CustomStreamWrapper, llm_response)
            return StreamingResponse(
                generate_stream_response(stream_response),
                media_type="text/event-stream",
            )
        else:
            return llm_response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


def convert_none_to_null(obj):
    if obj is None:
        return "null"
    return obj


async def generate_stream_response(
    response: CustomStreamWrapper,
) -> AsyncGenerator[bytes, None]:
    try:
        async for chunk in response:
            if chunk:
                yield f"data: {json.dumps(chunk.model_dump(), default=convert_none_to_null)}\n\n".encode(
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
