# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from typing import cast
import base64
import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import StreamingResponse
from litellm import (
    AllMessageValues,
    ChatCompletionImageUrlObject,
    ChatCompletionTextObject,
    ModelResponse,  # type: ignore
)
from app.dependencies import get_llm_service
from app.core.llm_service import LLMService
from app.core.agent_manager import get_agent_manager
import logging
import json

from app.schemas.openai import ChatCompletionRequest, StreamChatCompletionResponse
from app.utils.json_utils import convert_none_to_null

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
        stream = request.get("stream")
        message, image_data = await get_content_and_image_from_message(
            request["messages"][-1]
        )

        llm_response = await llm_service.generate_response(
            message_type="text_to_text",
            message=message,
            agent_config=agent_config,
            image=image_data,
            openai_request=True,
        )
        litellm_response = cast(ModelResponse, llm_response)

        if stream:
            return StreamingResponse(
                StreamChatCompletionResponse.generate_stream(litellm_response),
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


async def get_content_and_image_from_message(message: AllMessageValues):
    """
    Extract text content and image binary data from a message.
    Returns a tuple of (text_content: str, image_data: Optional[bytes])
    """
    if "content" not in message or message["content"] is None:
        raise HTTPException(status_code=400, detail="Message content is required")

    content = message["content"]

    if isinstance(content, str):
        return content, None

    content = list(content)
    text_parts = []
    image_data = None

    for item in content:
        if not isinstance(item, dict) or "type" not in item:
            raise HTTPException(status_code=400, detail="Invalid content format")

        if item["type"] == "text":
            item = cast(ChatCompletionTextObject, item)
            if "text" not in item:
                raise HTTPException(status_code=400, detail="Text content missing")
            text_parts.append(item["text"])

        elif item["type"] == "image_url":
            item = cast(ChatCompletionImageUrlObject, item)
            if "image_url" not in item or "url" not in item["image_url"]:
                raise HTTPException(status_code=400, detail="Image URL missing")
            if image_data is not None:
                raise HTTPException(
                    status_code=400, detail="Multiple images not supported"
                )

            url = item["image_url"]["url"]
            if url.startswith("data:image/"):
                try:
                    base64_data = url.split(",", 1)[1]
                    image_data = base64.b64decode(base64_data)
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid base64 image data: {str(e)}",
                    )
            else:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url)
                        response.raise_for_status()
                        image_data = response.content
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to fetch image from URL: {str(e)}",
                    )

        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported content type: {item['type']}"
            )

    return " ".join(text_parts), image_data
