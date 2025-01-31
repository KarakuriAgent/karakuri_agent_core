# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from starlette.requests import ClientDisconnect
from starlette.responses import FileResponse
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
)
from app.schemas.llm import LLMResponse
from app.schemas.user import UserConfig
from app.utils.audio import calculate_audio_duration, upload_to_storage
from pathlib import Path
from typing import Dict, cast
from app.schemas.agent import AgentConfig
from app.core.agent_manager import get_agent_manager
from app.core.config import get_settings
from app.schemas.chat_message import MessageType
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
    line_chat_client: LineChatClient,
):
    try:
        line_chat_client.create(agent_config)
        events = line_chat_client.parse_line_events(
            body, signature, agent_config.line_channel_secret
        )
        messages = await line_chat_client.process_message(events)
        try:
            for message in messages:
                token = message.reply_token
                content = message.content

                if content.type == MessageType.IMAGE:
                    if content.image:
                        user_image_cache[user_config.id] = content.image
                    continue
                elif content.type == MessageType.TEXT and content.text:
                    text_message = content.text
                else:
                    continue

                cached_image_bytes = user_image_cache.pop(user_config.id, None)
                llm_response = cast(
                    LLMResponse,
                    await llm_service.generate_response(
                        "talk",
                        text_message,
                        agent_config,
                        user_config,
                        image=cached_image_bytes,
                    ),
                )
                audio_data = await tts_service.generate_speech(
                    llm_response.agent_message, agent_config
                )
                scheme = request.headers.get("X-Forwarded-Proto", "http")
                server_host = request.headers.get(
                    "X-Forwarded-Host", request.base_url.hostname
                )
                base_url = f"{scheme}://{server_host}"
                audio_url = await upload_to_storage(
                    base_url, audio_data, "line", UPLOAD_DIR, MAX_FILES
                )
                duration = calculate_audio_duration(audio_data)
                await line_chat_client.reply_message(
                    token=token,
                    message=llm_response.agent_message,
                    audio_url=audio_url,
                    duration=duration,
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
