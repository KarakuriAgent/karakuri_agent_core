# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from typing import cast
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import StreamingResponse
from litellm import ModelResponse  # type: ignore
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
        stream = request["stream"]
        message, image_url = get_content_and_image_from_message(request["messages"][-1])
        
        # Determine message type based on presence of image
        message_type = "text_to_text" if image_url is None else "vision_to_text"
        
        llm_response = await llm_service.generate_response(
            message_type=message_type,
            message=message,
            agent_config=agent_config,
            image=image_url,
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


def get_content_and_image_from_message(message):
    """
    Extract text content and image URL from a message.
    Returns a tuple of (text_content: str, image_url: Optional[str])
    """
    if "content" not in message or message["content"] is None:
        raise HTTPException(status_code=400, detail="Message content is required")

    content = message["content"]
    
    # Handle string content (backward compatibility)
    if isinstance(content, str):
        return content, None
        
    # Handle list content (new format with possible image)
    if isinstance(content, list):
        text_parts = []
        image_url = None
        
        for item in content:
            if not isinstance(item, dict) or "type" not in item:
                raise HTTPException(status_code=400, detail="Invalid content format")
                
            if item["type"] == "text":
                if "text" not in item:
                    raise HTTPException(status_code=400, detail="Text content missing")
                text_parts.append(item["text"])
                
            elif item["type"] == "image_url":
                if "image_url" not in item or "url" not in item["image_url"]:
                    raise HTTPException(status_code=400, detail="Image URL missing")
                if image_url is not None:
                    raise HTTPException(status_code=400, detail="Multiple images not supported")
                image_url = item["image_url"]["url"]
                
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported content type: {item['type']}")
                
        return " ".join(text_parts), image_url
        
    raise HTTPException(status_code=400, detail="Invalid content format")
