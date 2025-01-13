# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from litellm import ChatCompletionRequest, CustomStreamWrapper, ModelResponse  # type: ignore
from app.dependencies import get_llm_service
from app.core.llm_service import LLMService
from app.core.agent_manager import get_agent_manager
import logging
from app.core.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


@router.post("/chat/completions", response_model=ModelResponse)
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

    # if image_file is not None:
    #     image_content = await image_file.read()
    # else:
    image_content = None

    try:
        llm_response = await llm_service.generate_response(
            message_type="text_to_text",
            message=get_content_from_message(request["messages"][-1]),
            agent_config=agent_config,
            image=image_content,
            openai_request=True,
        )
        if isinstance(llm_response, CustomStreamWrapper):
            raise HTTPException(status_code=400, detail="Streaming not supported")
        return llm_response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


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
        # text_contents = [
        #     block["text"] for block in content
        #     if isinstance(block, dict) and "text" in block
        # ]
        # return " ".join(text_contents)
    else:
        return str(content)
