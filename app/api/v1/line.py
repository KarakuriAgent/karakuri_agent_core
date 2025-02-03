# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from starlette.requests import ClientDisconnect
from starlette.responses import FileResponse
from app.core.chat.chat_service import ChatService
from app.core.chat.line_chat_client import LineChatClient
from app.core.llm_service import LLMService
from app.core.memory.memory_service import MemoryService
from app.core.tts_service import TTSService
from app.core.stt_service import STTService
from app.dependencies import (
    get_line_chat_client,
    get_llm_service,
    get_memory_service,
    get_stt_service,
    get_tts_service,
    get_chat_service,
)
from app.schemas.user import UserConfig
from pathlib import Path
from typing import Dict
from app.schemas.agent import AgentConfig
from app.core.agent_manager import get_agent_manager
from app.core.config import get_settings
import logging


router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()
UPLOAD_DIR = settings.line_audio_files_dir
MAX_FILES = settings.line_max_audio_files
user_image_cache: Dict[str, bytes] = {}


async def process_line_events_background(
    body: str,
    signature: str,
    agent_config: AgentConfig,
    user_config: UserConfig,
    request: Request,
    llm_service: LLMService,
    tts_service: TTSService,
    #  TODO use chat_service?
    line_chat_client: LineChatClient,
):
    try:
        line_chat_client.create(agent_config)
        events = line_chat_client.parse_line_events(
            body, signature, agent_config.line_channel_secret
        )
        messages = await line_chat_client.process_message(events)

        scheme = request.headers.get("X-Forwarded-Proto", "http")
        server_host = request.headers.get("X-Forwarded-Host", request.base_url.hostname)
        base_url = f"{scheme}://{server_host}"
        await line_chat_client.process_and_send_messages(
            "chat-line",
            messages,
            agent_config,
            user_config,
            llm_service,
            tts_service,
            base_url,
            True,
        )
    except Exception as e:
        logger.exception(
            f"Error in process_line_events_background: {str(e)}", exc_info=True
        )
    finally:
        await line_chat_client.close()


@router.post("/callback/{agent_id}/{user_id}")
async def handle_line_callback(
    background_tasks: BackgroundTasks,
    request: Request,
    agent_id: str,
    user_id: str,
    llm_service: LLMService = Depends(get_llm_service),
    tts_service: TTSService = Depends(get_tts_service),
    stt_service: STTService = Depends(get_stt_service),
    memory_service: MemoryService = Depends(get_memory_service),
    line_chat_client: LineChatClient = Depends(get_line_chat_client),
    chat_service: ChatService = Depends(get_chat_service),
):
    signature, body = await extract_line_request_data(request)
    agent_manager = get_agent_manager()
    try:
        agent_config = agent_manager.get_agent(agent_id)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Agent with ID '{agent_id}' not found."
        )

    user_config = await memory_service.get_user(agent_id, user_id)
    if user_config is None:
        raise HTTPException(
            status_code=404, detail=f"User with user_id '{user_id}' not found."
        )

    # Verify signature before returning OK
    line_chat_client.parse_line_events(
        body, signature, agent_config.line_channel_secret
    )

    is_chat_available = await chat_service.is_chat_available(agent_id)
    if not is_chat_available:
        try:
            scheme = request.headers.get("X-Forwarded-Proto", "http")
            server_host = request.headers.get(
                "X-Forwarded-Host", request.base_url.hostname
            )
            line_chat_client.create(agent_config)
            events = line_chat_client.parse_line_events(
                body, signature, agent_config.line_channel_secret
            )
            messages = await line_chat_client.process_message(events)
            if messages:
                await chat_service.update_pending_messages(
                    agent_id,
                    "chat-line",
                    user_id,
                    f"{scheme}://{server_host}",
                    messages,
                )
                logger.info(
                    f"Saved {len(messages)} messages to chat service for agent {agent_id}, user {user_id}"
                )
        except Exception as e:
            logger.error(f"Error saving message to chat service: {e}")
        finally:
            await line_chat_client.close()
        return "OK"

    background_tasks.add_task(
        process_line_events_background,
        body,
        signature,
        agent_config,
        user_config,
        request,
        llm_service,
        tts_service,
        line_chat_client,
    )
    return "OK"


async def extract_line_request_data(request: Request):
    try:
        signature = request.headers.get("X-Line-Signature")
        if not signature:
            raise HTTPException(
                status_code=400, detail="X-Line-Signature header is missing"
            )

        body = await request.body()
        return signature, body.decode()
    except ClientDisconnect:
        logger.warning("Client disconnected while reading request body")
        raise HTTPException(status_code=400, detail="Client disconnected")
    except Exception as e:
        logger.error(f"Error extracting LINE request data: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid request")


@router.get(f"/{UPLOAD_DIR}/{{file_name}}")
async def get_audio(file_name: str):
    if ".." in file_name or "/" in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    file_path = Path(f"{UPLOAD_DIR}/{file_name}.wav")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)
